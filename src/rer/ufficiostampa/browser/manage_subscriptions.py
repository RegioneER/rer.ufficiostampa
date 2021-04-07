# -*- coding: utf-8 -*-
from itsdangerous.url_safe import URLSafeTimedSerializer
from plone import api
from plone import schema
from plone.protect.authenticator import createToken
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces.controlpanel import IMailSchema
from rer.ufficiostampa import _
from rer.ufficiostampa.interfaces import ISubscriptionsStore
from rer.ufficiostampa.utils import decode_token
from rer.ufficiostampa.utils import get_site_title
from smtplib import SMTPException
from z3c.form import button
from z3c.form import field
from z3c.form import form
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.i18n import translate
from zope.interface import Interface
from z3c.form.interfaces import HIDDEN_MODE
from plone.api.exc import InvalidParameterError
from rer.ufficiostampa.interfaces.settings import IRerUfficiostampaSettings
from rer.ufficiostampa.utils import prepare_email_message

import logging

logger = logging.getLogger(__name__)


def getSubscriptions():
    data = decode_token()
    if not data:
        return ()
    if data.get("error", ""):
        return ()
    return data["data"].attrs.get("channels", [])


def getUid():
    data = decode_token()
    if not data:
        return None
    if data.get("error", ""):
        return None
    return data["data"].intid


class IManageSubscriptionsRequestForm(Interface):
    """ define field to manage subscriptions """

    email = schema.Email(
        title=_(u"manage_subscriptions_email_title", default=u"Email"),
        description=_(
            u"manage_subscriptions_description",
            default=u"Insert the email for wich you want to manage "
            u"subscriptions.",
        ),
        required=True,
    )


class IManageSubscriptionsForm(Interface):
    """  """

    channels = schema.List(
        title=_(u"manage_subscriptions_channels_title", default=u"Channels"),
        description=_(
            u"manage_subscriptions_channels_description",
            default=u"Select which channels you want to be subscribed or not. "
            u"Disable all if you don't want to be notified.",
        ),
        required=False,
        defaultFactory=getSubscriptions,
        missing_value=(),
        value_type=schema.Choice(
            source="rer.ufficiostampa.vocabularies.channels"
        ),
    )
    uid = schema.Int(readonly=True, defaultFactory=getUid)


class ManageSubscriptionsRequestForm(form.Form):
    label = _("manage_subscriptions_request_title", u"Channels subscriptions")
    description = _(
        "manage_subscriptions_request_help",
        u"If you want to manage your subscriptions, please insert your email "
        u"address. You will receive an email with the link to manage them. "
        u"That link will expire in 24 hours.",
    )
    ignoreContext = True
    fields = field.Fields(IManageSubscriptionsRequestForm)

    def updateWidgets(self):
        super(ManageSubscriptionsRequestForm, self).updateWidgets()
        if self.request.get("email", None):
            self.widgets["email"].value = self.request.get("email")

    @button.buttonAndHandler(_(u"send_button", default="Send"))
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        email = data.get("email", None)
        tool = getUtility(ISubscriptionsStore)
        subscriptions = tool.search(query={"email": email})
        if not subscriptions:
            msg = _(
                u"manage_subscriptions_request_inexistent_mail",
                default=u"Mail not found. Unable to send the link.",
            )
            api.portal.show_message(
                message=msg, request=self.request, type=u"error"
            )
            return

        subscription = subscriptions[0]
        # create CSRF token
        token = createToken()

        # sign data
        serializer = self.get_serializer()
        if not serializer:
            msg = _(
                u"manage_subscriptions_request_serializer_error",
                default=u"Serializer secret and salt not set in control panel."
                u" Unable to send the link.",
            )
            api.portal.show_message(
                message=msg, request=self.request, type=u"error"
            )
            return
        secret = serializer.dumps(
            {
                "id": subscription.intid,
                "email": subscription.attrs.get("email", ""),
            }
        )

        # send confirm email
        url = "{url}/manage-subscriptions?secret={secret}&_authenticator={token}".format(  # noqa
            url=self.context.absolute_url(), secret=secret, token=token
        )
        site_title = get_site_title()
        mail_text = prepare_email_message(
            context=api.portal.get(),
            template="@@manage_subscriptions_mail_template",
            parameters={"url": url, "site_title": site_title},
        )

        res = self.send(message=mail_text, mto=email, site_title=site_title)
        if not res:
            msg = _(
                u"manage_subscriptions_not_send",
                default=u"Unable to send manage subscriptions link. "
                u"Please contact site administrator.",
            )
            msg_type = "error"
        else:
            msg = _(
                u"manage_subscriptions_send_success",
                default=u"You will receive an email with a link to manage "
                u"your subscriptions.",
            )
            msg_type = "info"
        api.portal.show_message(
            message=msg, request=self.request, type=msg_type
        )

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
            None
        return URLSafeTimedSerializer(token_secret, token_salt)

    def send(self, message, mto, site_title):
        portal = api.portal.get()
        overview_controlpanel = getMultiAdapter(
            (portal, self.request), name="overview-controlpanel"
        )
        if overview_controlpanel.mailhost_warning():
            logger.error("MailHost is not configured.")
            return False

        registry = getUtility(IRegistry)
        mail_settings = registry.forInterface(IMailSchema, prefix="plone")
        mfrom = mail_settings.email_from_address
        encoding = registry.get("plone.email_charset", "utf-8")
        mailHost = api.portal.get_tool(name="MailHost")
        subject = translate(
            _(
                "manage_subscription_subject_label",
                default=u"Manage your subscriptions for ${site}",
                mapping={"site": site_title},
            ),
            context=self.request,
        )
        try:
            mailHost.send(
                message,
                mto=mto,
                mfrom=mfrom,
                subject=subject,
                charset=encoding,
                msg_type="text/html",
                immediate=True,
            )
        except (SMTPException, RuntimeError) as e:
            logger.exception(e)
            return False
        return True


class ManageSubscriptionsForm(form.Form):
    label = _("manage_subscriptions_title", u"Channels subscriptions")
    description = _(
        "manage_subscriptions_help",
        u"This is the list of available channels and your subscriptions.",
    )
    ignoreContext = True
    fields = field.Fields(IManageSubscriptionsForm)
    fields["channels"].widgetFactory = CheckBoxFieldWidget

    def updateWidgets(self):
        super(ManageSubscriptionsForm, self).updateWidgets()
        self.widgets["uid"].mode = HIDDEN_MODE

    def render(self):
        data = decode_token()
        if data.get("error", ""):
            return self.return_with_message(
                message=data["error"], type=u"error"
            )
        return super(ManageSubscriptionsForm, self).render()

    def return_with_message(self, message, type):
        api.portal.show_message(
            message=message, request=self.request, type=type,
        )
        return self.request.response.redirect(api.portal.get().absolute_url())

    @button.buttonAndHandler(_(u"save_button", default="Save"))
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        tool = getUtility(ISubscriptionsStore)
        res = tool.update(
            id=data.get("uid", None), data={"channels": data.get("channels")},
        )
        if res and res.get("error", "NotFound"):
            msg = _(
                u"manage_subscriptions_inexistent_mail",
                default=u"Mail not found. Unable to change settings.",
            )
            return self.return_with_message(message=msg, type="error")
        return self.return_with_message(
            message=_(
                "manage_subscriptions_success",
                default=u"Subscriptions updated",
            ),
            type=u"info",
        )

    @button.buttonAndHandler(
        _(u"cancel_button", default="Cancel"), name="cancel"
    )
    def handleCancel(self, action):
        return self.return_with_message(
            message=_("cancel_action", default=u"Action cancelled",),
            type=u"info",
        )
