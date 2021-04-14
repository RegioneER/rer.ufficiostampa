# -*- coding: utf-8 -*-
from email.utils import formataddr
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
from zope.interface import provider
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

import logging

logger = logging.getLogger(__name__)


class ISubscriptionSchema(Interface):
    """  """

    name = schema.TextLine(
        title=_(u"name_label", default=u"Name"), description=u"", required=True
    )
    surname = schema.TextLine(
        title=_(u"surname_label", default=u"Surname"),
        description=u"",
        required=True,
    )
    email = schema.TextLine(
        title=_(u"email_label", default=u"Email"),
        description=u"",
        required=True,
    )
    phone = schema.TextLine(
        title=_(u"phone_label", default=u"Phone"),
        description=u"",
        required=False,
    )
    newspaper = schema.TextLine(
        title=_(u"newspaper_label", default=u"Newspaper"),
        description=u"",
        required=False,
    )
    channels = schema.List(
        title=_(u"manage_subscriptions_channels_title", default=u"Channels"),
        description=_(
            u"manage_subscriptions_channels_description",
            default=u"Select which channels you want to be subscribed. "
            u"Disable all if you don't want to be notified.",
        ),
        required=True,
        missing_value=(),
        value_type=schema.Choice(
            source="rer.ufficiostampa.vocabularies.channels"
        ),
    )


class ISubscriptionEditSchema(ISubscriptionSchema):
    uid = schema.Int(readonly=True)


class AddSubscriptionForm(form.Form):
    label = _("add_subscription_title", u"Add subscription")
    description = _("add_subscription_help", u"")
    ignoreContext = True
    fields = field.Fields(ISubscriptionSchema)
    fields["channels"].widgetFactory = CheckBoxFieldWidget

    @button.buttonAndHandler(_(u"save_button", default="Save"))
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        tool = getUtility(ISubscriptionsStore)
        res = tool.add(data=data)
        if not res:
            msg = _(
                u"add_subscription_error",
                default=u"Error in adding new subscription.",
            )
            api.portal.show_message(
                message=msg, request=self.request, type=u"error"
            )
            return self.request.response.redirect(
                "{}/@@channels-management".format(
                    api.portal.get().absolute_url()
                )
            )

        msg = _(u"add_subscription_success", default=u"Subscription added.",)
        api.portal.show_message(
            message=msg, request=self.request, type=u"info"
        )
        return self.request.response.redirect(
            "{}/@@channels-management".format(api.portal.get().absolute_url())
        )

    @button.buttonAndHandler(
        _(u"cancel_button", default="Cancel"), name="cancel"
    )
    def handleCancel(self, action):
        api.portal.show_message(
            message=_("cancel_action", default=u"Action cancelled",),
            request=self.request,
            type=u"info",
        )
        return self.request.response.redirect(
            "{}/@@channels-management".format(api.portal.get().absolute_url())
        )


class EditSubscriptionForm(form.Form):
    label = _("edit_subscription_title", u"Edit subscription")
    description = _("edit_subscription_help", u"")
    ignoreContext = True
    fields = field.Fields(ISubscriptionEditSchema)
    fields["channels"].widgetFactory = CheckBoxFieldWidget

    def render(self):
        if "uid" not in self.request.form:
            msg = _(
                "missing_uid",
                default=u"Unable to manage subscription. Missing uid parameter.",
            )
            return self.return_with_message(message=msg, type="error")
        return super(EditSubscriptionForm, self).render()

    def updateWidgets(self):
        super(EditSubscriptionForm, self).updateWidgets()
        uid = self.request.get("uid", None)
        if not uid:
            return

        tool = getUtility(ISubscriptionsStore)
        record = tool.get_record(uid)
        if not record:
            msg = _(
                "record_not_found",
                default=u"Unable to manage subscription. Record with id ${id} not found.",
                mapping={"id": uid},
            )
            return self.return_with_message(message=msg, type="error")
        # self.widgets["uid"].value = self.request.get("uid")

    # def updateWidgets(self):
    #     super(EditSubscriptionForm, self).updateWidgets()
    #     self.widgets["uid"].mode = HIDDEN_MODE

    @button.buttonAndHandler(_(u"save_button", default="Save"))
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        tool = getUtility(ISubscriptionsStore)
        res = tool.add(data=data)
        if not res:
            msg = _(
                u"add_subscription_error",
                default=u"Error in adding new subscription.",
            )
            api.portal.show_message(
                message=msg, request=self.request, type=u"error"
            )
            return self.request.response.redirect(
                "{}/@@channels-management".format(
                    api.portal.get().absolute_url()
                )
            )

        msg = _(u"add_subscription_success", default=u"Subscription added.",)
        api.portal.show_message(
            message=msg, request=self.request, type=u"info"
        )
        return self.request.response.redirect(
            "{}/@@channels-management".format(api.portal.get().absolute_url())
        )

    def return_with_message(self, message, type):
        api.portal.show_message(
            message=message, request=self.request, type=type,
        )
        return self.request.response.redirect(
            "{}/@@channels-management".format(api.portal.get().absolute_url())
        )

    @button.buttonAndHandler(
        _(u"cancel_button", default="Cancel"), name="cancel"
    )
    def handleCancel(self, action):
        api.portal.show_message(
            message=_("cancel_action", default=u"Action cancelled",),
            request=self.request,
            type=u"info",
        )
        return self.request.response.redirect(
            "{}/@@channels-management".format(api.portal.get().absolute_url())
        )
