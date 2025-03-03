from datetime import datetime
from email.message import EmailMessage
from plone import api
from plone.api.exc import InvalidParameterError
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from requests.exceptions import ConnectionError
from requests.exceptions import Timeout
from rer.ufficiostampa import _
from rer.ufficiostampa.interfaces import ISendHistoryStore
from rer.ufficiostampa.interfaces import ISubscriptionsStore
from rer.ufficiostampa.interfaces.settings import IRerUfficiostampaSettings

# from rer.ufficiostampa.utils import decode_token
from rer.ufficiostampa.utils import get_attachments
from rer.ufficiostampa.utils import get_attachments_external
from rer.ufficiostampa.utils import get_site_title
from rer.ufficiostampa.utils import mail_from
from rer.ufficiostampa.utils import prepare_email_message
from smtplib import SMTPException
from zExceptions import BadRequest
from zope.component import getUtility
from zope.interface import alsoProvides
from zope.schema.interfaces import IVocabularyFactory

import json
import logging
import requests


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
                "links": self.get_links_attachments(data),
            },
        )
        if external_sender_url:
            return self.send_external(data=data, body=body)
        else:
            return self.send_internal(data=data, body=body)

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

        if send_id:
            self.update_history(send_id=send_id, status="success")
        return {
            "status": "success",
            "id": send_id,
        }

    def send_external(self, data, body):
        external_sender_url = self.get_value_from_settings(field="external_sender_url")

        subscribers = self.get_subscribers(data)
        send_uid = self.set_history_start(data=data, subscribers=len(subscribers))

        payload = {
            "channel_url": self.get_channel_url(),
            "subscribers": subscribers,
            "subject": self.subject,
            "mfrom": mail_from(),
            "text": body,
            "send_uid": send_uid,
        }

        params = {"url": external_sender_url}
        attachments = get_attachments_external(data)
        if attachments:
            params["data"] = payload
            params["files"] = attachments
        else:
            params["data"] = json.dumps(payload)
            params["headers"] = {"Content-Type": "application/json"}

        try:
            response = requests.post(**params)
        except (ConnectionError, Timeout) as e:
            logger.exception(e)
            self.add_send_error_message()
            if send_uid:
                self.update_history(send_id=send_uid, status="error")
            return
        if response.status_code != 200:
            logger.error(f'Unable to send "{self.subject}": {response.text}')
            self.add_send_error_message()
            if send_uid:
                self.update_history(send_id=send_uid, status="error")
            return
        return {
            "status": "success",
            "id": send_uid,
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
        return get_attachments(data)

    def get_links_attachments(self, data):
        return get_attachments(data, as_link=True)

    @property
    def subject(self):
        if self.context.portal_type == "ComunicatoStampa":
            value = f"Comunicato Stampa: {self.context.title}"
        else:
            value = self.context.title
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
                f'Unable to update history with id "{send_id}": {res["error"]}'
            )

    def get_channel_url(self):
        # If volto frontend_domain is set, use it as destination link
        try:
            destination_link = api.portal.get_registry_record(
                "volto.frontend_domain", default=""
            )

        except KeyError:
            destination_link = api.portal.get().absolute_url()
        if destination_link.endswith("/"):
            destination_link = destination_link[:-1]
        destination_link += "/++api++"
        return destination_link
