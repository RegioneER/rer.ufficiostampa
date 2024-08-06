from datetime import datetime
from email.message import EmailMessage
from plone import api
from plone.api.exc import InvalidParameterError
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from rer.ufficiostampa import _
from rer.ufficiostampa.interfaces import ISendHistoryStore
from rer.ufficiostampa.interfaces import ISubscriptionsStore
from rer.ufficiostampa.interfaces.settings import IRerUfficiostampaSettings
# from rer.ufficiostampa.utils import decode_token
from rer.ufficiostampa.utils import get_site_title
from rer.ufficiostampa.utils import mail_from
from rer.ufficiostampa.utils import prepare_email_message
from smtplib import SMTPException
from zExceptions import BadRequest
from zope.component import getUtility
from zope.interface import alsoProvides
from zope.schema.interfaces import IVocabularyFactory

import logging


logger = logging.getLogger(__name__)


class SendComunicato(Service):
    def reply(self):
        # TODO: use rer.ufficiostampa.browser.send.ISendForm
        alsoProvides(self.request, IDisableCSRFProtection)
        data = json_body(self.request)
        rcpts = self.get_subscribers(data=data)
        if not rcpts:
            raise BadRequest(
                _(
                    "empty_subscribers",
                    default="You need to provide at least one email address or channel.",  # noqa
                )
            )

        # if errors:
        #     self.status = self.formErrorsMessage
        #     return
        return self.sendMessage(data=data)

    def get_value_from_settings(self, field):
        try:
            return api.portal.get_registry_record(
                field, interface=IRerUfficiostampaSettings
            )
        except (KeyError, InvalidParameterError):
            return None

    def get_channels(self, data):
        vocab = getUtility(
            IVocabularyFactory, name="rer.ufficiostampa.vocabularies.channels"
        )
        return [
            vocab(self.context).getTermByToken(x).value
            for x in data.get("channels", [])
        ]

    def get_subscribers(self, data):
        subscribers = set()
        tool = getUtility(ISubscriptionsStore)
        for channel in self.get_channels(data):
            records = tool.search(query={"channels": channel})
            subscribers.update([x.attrs.get("email", "").lower() for x in records])
        subscribers.update([x.lower() for x in data.get("additional_addresses", [])])
        return sorted(list(subscribers))

    def sendMessage(self, data):
        external_sender_url = self.get_value_from_settings(field="external_sender_url")
        body = prepare_email_message(
            context=self.context,
            template="@@send_mail_template",
            parameters={
                "notes": data.get("notes", ""),
                "site_title": get_site_title(),
                "date": datetime.now(),
                # ??? perchè qui si usano i folder, poi nell'invio si usano gli attachments ?
                "folders": self.get_folders_attachments(),
            },
        )
        if external_sender_url:
            return self.send_external(data=data, body=body)
        else:
            return self.send_internal(data=data, body=body)

    def get_folders_attachments(self):
        # if self.context.portal_type == "InvitoStampa":
        #     return []
        return self.context.listFolderContents(
            contentFilter={"portal_type": ["Folder"]}
        )

    # TODO: move to utility ?
    def send_internal(self, data, body):
        rcpts = self.get_subscribers(data)
        encoding = api.portal.get_registry_record(
            "plone.email_charset", default="utf-8"
        )
        msg = EmailMessage()
        msg.set_content(body)
        msg["Subject"] = self.subject
        msg["From"] = mail_from()
        msg["Reply-To"] = mail_from()
        msg.replace_header("Content-Type", 'text/html; charset="utf-8"')

        self.manage_attachments(data=data, msg=msg)
        host = api.portal.get_tool(name="MailHost")
        msg["Bcc"] = ", ".join(rcpts)

        # log start
        send_id = self.set_history_start(data=data, subscribers=len(rcpts))

        try:
            host.send(msg, charset=encoding)
        except (SMTPException, RuntimeError) as e:
            logger.exception(e)
            # self.add_send_error_message()
            self.update_history(send_id=send_id, status="error")
            raise BadRequest(_("Errore non previsto durante l'invio del comunicato"))
        # api.portal.show_message(
        #     message=_(
        #         "success_send_mail",
        #         default="Send complete.",
        #     ),
        #     request=self.request,
        #     type="info",
        # )

        if send_id:
            self.update_history(send_id=send_id, status="success")
        return {
            "status": "success",
            "id": send_id,
        }

    def manage_attachments(self, data, msg):
        attachments = self.get_attachments(data=data)
        for attachment in attachments:
            msg.add_attachment(
                attachment["data"],
                maintype=attachment["content_type"],
                subtype=attachment["content_type"],
                filename=attachment["filename"],
            )

    def get_attachments(self, data):
        attachments = []
        for uid in data.get("attachments", []):
            item = api.content.get(UID=uid)
            if not item:
                continue
            if item.portal_type == "Image":
                field = item.image
            elif item.portal_type == "File":
                field = item.file
            else:
                raise BadRequest(_("Invalid attachment type"))
            attachments.append(
                {
                    "data": field.data,
                    "filename": field.filename,
                    "content_type": item.content_type(),
                }
            )
        return attachments

    @property
    def subject(self):
        value = "{type}: {title}".format(
            type=self.context.portal_type == "ComunicatoStampa"
            and "Comunicato Regione"  # noqa
            or "Invito Regione",  # noqa
            title=self.context.title,
        )
        return value

    @property
    def type_name(self):
        types_tool = api.portal.get_tool(name="portal_types")
        return types_tool.getTypeInfo(self.context.portal_type).title

    # TODO: move to utility ?
    def set_history_start(self, data, subscribers):
        # if it's a preview, do not store infos
        if not data.get("channels", []):
            return ""
        # mark as sent
        self.context.message_sent = True
        tool = getUtility(ISendHistoryStore)
        intid = tool.add(
            {
                "type": self.type_name,
                "title": self.context.Title(),
                "number": getattr(self.context, "comunicato_number", ""),
                "url": self.context.absolute_url(),
                "recipients": subscribers,
                "channels": self.get_channels(data),
                "status": "sending",
            }
        )
        return intid

    # TODO: move to utility ?
    def update_history(self, send_id, status):
        tool = getUtility(ISendHistoryStore)
        res = tool.update(
            id=send_id,
            data={"completed_date": datetime.now(), "status": status},
        )
        if res and "error" in res:
            logger.error(
                'Unable to update history with id "{}": {}'.format(
                    send_id, res["error"]
                )
            )


# from datetime import datetime
# from DateTime import DateTime
# from plone import api
# from plone import schema
# from plone.memoize.view import memoize
# from plone.registry.interfaces import IRegistry
# from requests.exceptions import ConnectionError
# from requests.exceptions import Timeout
# from rer.ufficiostampa import _
# from rer.ufficiostampa.utils import get_site_title
# from rer.ufficiostampa.utils import mail_from
# from rer.ufficiostampa.utils import prepare_email_message
# from smtplib import SMTPException
# from z3c.form import button
# from z3c.form import field
# from z3c.form import form
# from z3c.form.browser.checkbox import CheckBoxFieldWidget
# from z3c.form.interfaces import ActionExecutionError
# from zope.component import getMultiAdapter
# from zope.interface import Interface
# from zope.interface import Invalid
# from zope.interface import provider
# from zope.schema.interfaces import IContextAwareDefaultFactory
# from zope.schema.interfaces import IVocabularyFactory
# from email.message import EmailMessage

# import json
# import logging
# import requests


# logger = logging.getLogger(__name__)


# def check_emails(value):
#     """Check that all values are valid email addresses"""
#     reg_tool = api.portal.get_tool(name="portal_registration")
#     for address in value:
#         if not reg_tool.isValidEmail(address):
#             raise Invalid(
#                 _(
#                     "validation_invalid_email",
#                     default="Invalid email address: ${address}",
#                     mapping={"address": address},
#                 )
#             )
#     return True


# class SendForm(form.Form):
#     description = _(
#         "send_form_help",
#         "Send this Comunicato or Invito to a list of recipients.",
#     )
#     ignoreContext = True
#     fields = field.Fields(ISendForm)
#     fields["channels"].widgetFactory = CheckBoxFieldWidget
#     fields["attachments"].widgetFactory = CheckBoxFieldWidget

#     @property
#     def label(self):
#         types_tool = api.portal.get_tool(name="portal_types")
#         return _(
#             "send_form_title",
#             "Send ${type}",
#             mapping={"type": types_tool.getTypeInfo(self.context.portal_type).title},
#         )

#     @button.buttonAndHandler(_("send_button", default="Send"))
#     def handleSave(self, action):
#         data, errors = self.extractData()
#         if not self.get_subscribers(data=data):
#             raise ActionExecutionError(
#                 Invalid(
#                     _(
#                         "empty_subscribers",
#                         default="You need to provide at least one email address or channel.",  # noqa
#                     )
#                 )
#             )
#         if errors:
#             self.status = self.formErrorsMessage
#             return
#         return self.sendMessage(data=data)

#     @button.buttonAndHandler(_("cancel_button", default="Cancel"), name="cancel")
#     def handleCancel(self, action):
#         api.portal.show_message(
#             message=_(
#                 "cancel_action",
#                 default="Action cancelled",
#             ),
#             type="info",
#             request=self.request,
#         )
#         return self.request.response.redirect(self.context.absolute_url())


#     @property
#     @memoize
#     def subject(self):
#         value = "{type}: {title}".format(
#             type=self.context.portal_type == "ComunicatoStampa"
#             and "Comunicato Regione"  # noqa
#             or "Invito Regione",  # noqa
#             title=self.context.title,
#         )
#         return value


#     def get_attachments_external(self, data):
#         attachments = []
#         for item_id in data.get("attachments", []):
#             item = self.context.get(item_id, None)
#             if not item:
#                 continue
#             field = item.portal_type == "Image" and item.image or item.file
#             attachments.append(
#                 (
#                     field.filename,
#                     (field.filename, field.open(), item.content_type()),
#                 )
#             )
#         return attachments

#     def manage_attachments(self, data, msg):
#         attachments = self.get_attachments(data=data)
#         for attachment in attachments:
#             msg.add_attachment(
#                 attachment["data"],
#                 maintype=attachment["content_type"],
#                 subtype=attachment["content_type"],
#                 filename=attachment["filename"],
#             )

#     def add_send_error_message(self):
#         api.portal.show_message(
#             message=_(
#                 "error_send_mail",
#                 default="Error sending mail. Contact site administrator.",
#             ),
#             request=self.request,
#             type="error",
#         )

#     # main methods

#     def send_internal(self, data, body):
#         portal = api.portal.get()
#         overview_controlpanel = getMultiAdapter(
#             (portal, self.request), name="overview-controlpanel"
#         )
#         if overview_controlpanel.mailhost_warning():
#             return {"error": "MailHost is not configured."}
#         subscribers = self.get_subscribers(data)
#         registry = getUtility(IRegistry)
#         encoding = registry.get("plone.email_charset", "utf-8")

#         msg = EmailMessage()
#         msg.set_content(body)
#         msg["Subject"] = self.subject
#         msg["From"] = mail_from()
#         msg["Reply-To"] = mail_from()
#         msg.replace_header("Content-Type", 'text/html; charset="utf-8"')

#         self.manage_attachments(data=data, msg=msg)
#         host = api.portal.get_tool(name="MailHost")
#         msg["Bcc"] = ", ".join(subscribers)
#         send_id = self.set_history_start(data=data, subscribers=len(subscribers))

#         try:
#             host.send(msg, charset=encoding)
#         except (SMTPException, RuntimeError) as e:
#             logger.exception(e)
#             self.add_send_error_message()
#             self.update_history(send_id=send_id, status="error")
#             return
#         api.portal.show_message(
#             message=_(
#                 "success_send_mail",
#                 default="Send complete.",
#             ),
#             request=self.request,
#             type="info",
#         )

#         if send_id:
#             self.update_history(send_id=send_id, status="success")

#     def send_external(self, data, body):
#         frontend_url = self.get_value_from_settings(field="frontend_url")
#         external_sender_url = self.get_value_from_settings(field="external_sender_url")

#         channel_url = api.portal.get().absolute_url()
#         if frontend_url:
#             channel_url = frontend_url
#         subscribers = self.get_subscribers(data)
#         send_uid = self.set_history_start(data=data, subscribers=len(subscribers))

#         payload = {
#             "channel_url": channel_url,
#             "subscribers": subscribers,
#             "subject": self.subject,
#             "mfrom": mail_from(),
#             "text": body,
#             "send_uid": send_uid,
#         }

#         params = {"url": external_sender_url}
#         attachments = self.get_attachments_external(data)
#         if attachments:
#             params["data"] = payload
#             params["files"] = self.get_attachments_external(data)
#         else:
#             params["data"] = json.dumps(payload)
#             params["headers"] = {"Content-Type": "application/json"}

#         try:
#             response = requests.post(**params)
#         except (ConnectionError, Timeout) as e:
#             logger.exception(e)
#             self.add_send_error_message()
#             if send_uid:
#                 self.update_history(send_id=send_uid, status="error")
#             return
#         if response.status_code != 200:
#             logger.error(
#                 'Unable to send "{message}": {reason}'.format(  # noqa
#                     message=self.subject,
#                     reason=response.text,
#                 )
#             )
#             self.add_send_error_message()
#             if send_uid:
#                 self.update_history(send_id=send_uid, status="error")
#             return
#         # finish status will be managed via async calls
#         api.portal.show_message(
#             message=_(
#                 "success_send_mail_async",
#                 default="Send queued with success. " "See the status in send history.",
#             ),
#             request=self.request,
#             type="info",
#         )
