# -*- coding: utf-8 -*-
from itsdangerous.exc import SignatureExpired, BadSignature
from itsdangerous.url_safe import URLSafeTimedSerializer
from plone import api
from plone.api.exc import InvalidParameterError
from plone.registry.interfaces import IRegistry
from rer.ufficiostampa import _
from rer.ufficiostampa.interfaces.store import ISubscriptionsStore
from rer.ufficiostampa.interfaces.settings import IRerUfficiostampaSettings
from zope.component import getUtility
from zope.globalrequest import getRequest

try:
    # rer.agidtheme overrides site tile field
    from rer.agidtheme.base.interfaces import IRERSiteSchema as ISiteSchema
    from rer.agidtheme.base.utility.interfaces import ICustomFields

    RER_THEME = True
except ImportError:
    from Products.CMFPlone.interfaces.controlpanel import ISiteSchema

    RER_THEME = False

import json
import six


def defaultLegislature():
    try:
        legislatures = json.loads(
            api.portal.get_registry_record(
                "legislatures", interface=IRerUfficiostampaSettings
            )
        )
    except (KeyError, InvalidParameterError):
        return ""

    if not legislatures:
        return ""
    current = legislatures[-1]
    return current.get("legislature", "")


def get_site_title():
    registry = getUtility(IRegistry)
    site_settings = registry.forInterface(
        ISiteSchema, prefix="plone", check=False
    )
    site_title = getattr(site_settings, "site_title") or ""
    if RER_THEME:
        site_subtitle_style = (
            getattr(site_settings, "site_subtitle_style") or ""
        )
        fields_value = getUtility(ICustomFields)
        site_title = fields_value.titleLang(site_title)
        site_subtitle = fields_value.subtitleLang(
            getattr(site_settings, "site_subtitle") or "{}"
        )
        if site_subtitle and site_subtitle_style == "subtitle-normal":
            site_title += " {}".format(site_subtitle)

    if six.PY2:
        site_title = site_title.decode("utf-8")
    return site_title


def decode_token():
    request = getRequest()
    secret = request.form.get("secret", "")
    if not secret:
        return {
            "error": _(
                "unsubscribe_confirm_secret_null",
                default=u"Unable to manage subscriptions. Token not present.",  # noqa
            )
        }
    try:
        token_secret = api.portal.get_registry_record(
            "token_secret", interface=IRerUfficiostampaSettings
        )
        token_salt = api.portal.get_registry_record(
            "token_salt", interface=IRerUfficiostampaSettings
        )
    except (KeyError, InvalidParameterError):
        return {
            "error": _(
                "unsubscribe_confirm_secret_token_settings_error",
                default=u"Unable to manage subscriptions. Token keys not set in control panel.",  # noqa
            )
        }
    if not token_secret or not token_salt:
        return {
            "error": _(
                "unsubscribe_confirm_secret_token_settings_error",
                default=u"Unable to manage subscriptions. Token keys not set in control panel.",  # noqa
            )
        }
    serializer = URLSafeTimedSerializer(token_secret, token_salt)
    try:
        data = serializer.loads(secret, max_age=86400)
    except SignatureExpired:
        return {
            "error": _(
                "unsubscribe_confirm_secret_expired",
                default=u"Unable to manage subscriptions. Token expired.",
            )
        }
    except BadSignature:
        return {
            "error": _(
                "unsubscribe_confirm_secret_invalid",
                default=u"Unable to manage subscriptions. Invalid token.",
            )
        }
    record_id = data.get("id", "")
    email = data.get("email", "")
    if not record_id or not email:
        return {
            "error": _(
                "unsubscribe_confirm_invalid_parameters",
                default=u"Unable to manage subscriptions. Invalid parameters.",
            )
        }
    tool = getUtility(ISubscriptionsStore)
    record = tool.get_record(record_id)
    if not record:
        return {
            "error": _(
                "unsubscribe_confirm_invalid_id",
                default=u"Unable to manage subscriptions. Invalid id.",
            )
        }
    if record.attrs.get("email", "") != email:
        return {
            "error": _(
                "unsubscribe_confirm_invalid_email",
                default=u"Unable to manage subscriptions. Invalid email.",
            )
        }
    return {"data": record}
