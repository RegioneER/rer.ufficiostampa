from email.message import EmailMessage
from itsdangerous.url_safe import URLSafeTimedSerializer
from plone import api
from plone.api.exc import InvalidParameterError
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from rer.ufficiostampa import _
from rer.ufficiostampa.interfaces import ISubscriptionsStore
from rer.ufficiostampa.interfaces.settings import IRerUfficiostampaSettings
from rer.ufficiostampa.utils import decode_token
from rer.ufficiostampa.utils import get_site_title
from rer.ufficiostampa.utils import mail_from
from rer.ufficiostampa.utils import prepare_email_message
from smtplib import SMTPException
from zExceptions import BadRequest
from zope.component import getUtility
from zope.i18n import translate
from zope.interface import alsoProvides

import logging


logger = logging.getLogger(__name__)


class BaseService(Service):
    def send(self, message, mto, subject):
        """
        Send email with link to manage subscriptions
        """

        host = api.portal.get_tool(name="MailHost")
        msg = EmailMessage()

        msg.set_payload(message, charset="utf-8")
        msg.replace_header("Content-Type", "text/html; charset=utf-8")

        msg["Subject"] = subject
        msg["To"] = mto
        msg["From"] = mail_from()
        msg["Reply-To"] = mail_from()

        try:
            host.send(msg.as_string())
        except (SMTPException, RuntimeError) as e:
            logger.exception(e)
            return False
        return True


class PersonalChannelsManagementSendLink(BaseService):
    def reply(self):
        tool = getUtility(ISubscriptionsStore)
        query = json_body(self.request)

        email = query.get("email", "").strip()

        if not email:
            self.request.response.setStatus(400)
            return {
                "error": {
                    "type": "Salt not set",
                    "message": api.portal.translate(
                        _("missing_email", default="You need to pass an email.")
                    ),
                }
            }

        subscriptions = tool.search(query={"email": email})
        if not subscriptions:
            self.request.response.setStatus(400)
            return {
                "error": {
                    "type": "Salt not set",
                    "message": api.portal.translate(
                        _(
                            "manage_subscriptions_request_inexistent_mail",
                            default="Mail not found. Unable to send the link.",
                        )
                    ),
                }
            }

        subscription = subscriptions[0]

        # sign data
        serializer = self.get_serializer()
        if not serializer:
            msg = _(
                "manage_subscriptions_request_serializer_error",
                default="Serializer secret and salt not set in control panel."
                " Unable to send the link.",
            )
            self.request.response.setStatus(500)
            return {
                "error": {"type": "Salt not set", "message": api.portal.translate(msg)}
            }

        secret = serializer.dumps(
            {
                "id": subscription.intid,
                "email": subscription.attrs.get("email", ""),
            }
        )

        # send confirm email
        mail_text = prepare_email_message(
            context=api.portal.get(),
            template="cancel_subscriptions_mail_template",
            parameters={
                "url": f"{self.context.absolute_url()}/personal-channels-management?secret={secret}",
                "site_title": get_site_title(),
            },
        )
        subject = translate(
            _(
                "cancel_subscription_subject_label",
                default="Manage channels subscriptions cancel for ${site}",
                mapping={"site": get_site_title()},
            ),
            context=self.request,
        )
        res = self.send(message=mail_text, mto=email, subject=subject)

        if not res:
            msg = _(
                "manage_subscriptions_not_send",
                default="Unable to send manage subscriptions link. "
                "Please contact site administrator.",
            )
            self.request.response.setStatus(500)
            return {
                "error": {"type": "Mail not sent", "message": api.portal.translate(msg)}
            }
        return self.reply_no_content()

    def get_serializer(self):
        try:
            token_secret = api.portal.get_registry_record(
                "token_secret", interface=IRerUfficiostampaSettings
            )
            token_salt = api.portal.get_registry_record(
                "token_salt", interface=IRerUfficiostampaSettings
            )
        except (KeyError, InvalidParameterError):
            return None
        if not token_secret or not token_salt:
            return None
        return URLSafeTimedSerializer(token_secret, token_salt)


class PersonalChannelsManagementTokenVerify(Service):
    def reply(self):
        query = json_body(self.request)
        secret = query.get("secret", "") or ""
        secret = secret.strip()
        if not secret:

            msg = _(
                "unsubscribe_confirm_secret_null",
                default="Unable to manage unsubscriptions. missing token.",
            )
            raise BadRequest(api.portal.translate(msg))
        data = decode_token(secret=secret)
        if data.get("error", None):
            raise BadRequest(api.portal.translate(data["error"]))

        channels = data["data"].attrs.get("channels", [])

        if not channels:
            msg = _(
                "unsubscribe_no_channels",
                default="No channels to unsubscribe. Subscription not found.",
            )
            raise BadRequest(api.portal.translate(msg))
        return {"channels": channels}


class PersonalChannelsManagementUpdate(BaseService):
    def reply(self):

        alsoProvides(self.request, IDisableCSRFProtection)

        query = json_body(self.request)
        secret = query.get("secret", "").strip()
        channels = query.get("channels", [])
        if not secret:
            msg = _(
                "unsubscribe_confirm_secret_null",
                default="Unable to manage unsubscriptions. missing token.",
            )
            raise BadRequest(api.portal.translate(msg))
        if "channels" not in query:
            msg = _(
                "unsubscribe_no_channels_field",
                default="No channels to unsubscribe. 'channels' field missing.",
            )
            raise BadRequest(api.portal.translate(msg))
        data = decode_token(secret=secret)
        if data.get("error", None):
            raise BadRequest(api.portal.translate(data["error"]))

        record = data["data"]
        tool = getUtility(ISubscriptionsStore)
        subscription_id = record.intid

        record_channels = record.attrs.get("channels", [])
        # if there are some channels not present in the record, ignore them
        updated_channels = [x for x in channels if x in record_channels]
        removed_channels = [x for x in record_channels if x not in updated_channels]

        if not channels:
            # completely unsubscribed, so remove it from the db
            tool.delete(id=subscription_id)
            deleted = True
        else:
            tool.update(
                id=subscription_id,
                data={"channels": updated_channels},
            )
            deleted = False

        # send confirm email
        mail_text = prepare_email_message(
            context=api.portal.get(),
            template="@@cancel_subscriptions_notify_template",
            parameters={
                "site_title": get_site_title(),
                "name": f'{record.attrs.get("surname", "")} {record.attrs.get("name", "")}',
                "email": record.attrs.get("email", ""),
                "deleted": deleted,
                "channels": removed_channels,
            },
        )
        subject = translate(
            _(
                "cancel_subscription_subject_label",
                default="Manage channels subscriptions cancel for ${site}",
                mapping={"site": get_site_title()},
            ),
            context=self.request,
        )

        # notify channels admins
        self.send(message=mail_text, mto=mail_from(), subject=subject)

        return self.reply_no_content()
