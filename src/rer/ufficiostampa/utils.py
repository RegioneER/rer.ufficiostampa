from datetime import datetime
from email.utils import formataddr
from itsdangerous.exc import BadSignature
from itsdangerous.exc import SignatureExpired
from itsdangerous.url_safe import URLSafeTimedSerializer
from plone import api
from plone.api.exc import InvalidParameterError
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces.controlpanel import IMailSchema
from Products.CMFPlone.interfaces.controlpanel import ISiteSchema
from rer.ufficiostampa import _
from rer.ufficiostampa.interfaces.settings import IRerUfficiostampaSettings
from rer.ufficiostampa.interfaces.store import ISubscriptionsStore
from zExceptions import BadRequest
from zope.component import getUtility
from zope.globalrequest import getRequest

import logging
import premailer


logger = logging.getLogger(__name__)


def get_site_title():
    registry = getUtility(IRegistry)
    site_settings = registry.forInterface(ISiteSchema, prefix="plone", check=False)
    site_title = getattr(site_settings, "site_title") or ""
    return site_title


def decode_token():
    request = getRequest()
    secret = request.form.get("secret", "")
    if not secret:
        return {
            "error": _(
                "unsubscribe_confirm_secret_null",
                default="Unable to manage subscriptions. Token not present.",  # noqa
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
                default="Unable to manage subscriptions. Token keys not set in control panel.",  # noqa
            )
        }
    if not token_secret or not token_salt:
        return {
            "error": _(
                "unsubscribe_confirm_secret_token_settings_error",
                default="Unable to manage subscriptions. Token keys not set in control panel.",  # noqa
            )
        }
    serializer = URLSafeTimedSerializer(token_secret, token_salt)
    try:
        data = serializer.loads(secret, max_age=86400)
    except SignatureExpired:
        return {
            "error": _(
                "unsubscribe_confirm_secret_expired",
                default="Unable to manage subscriptions. Token expired.",
            )
        }
    except BadSignature:
        return {
            "error": _(
                "unsubscribe_confirm_secret_invalid",
                default="Unable to manage subscriptions. Invalid token.",
            )
        }
    record_id = data.get("id", "")
    email = data.get("email", "")
    if not record_id or not email:
        return {
            "error": _(
                "unsubscribe_confirm_invalid_parameters",
                default="Unable to manage subscriptions. Invalid parameters.",
            )
        }
    tool = getUtility(ISubscriptionsStore)
    record = tool.get_record(record_id)
    if not record:
        return {
            "error": _(
                "unsubscribe_confirm_invalid_id",
                default="Unable to manage subscriptions. Invalid id.",
            )
        }
    if record.attrs.get("email", "") != email:
        return {
            "error": _(
                "unsubscribe_confirm_invalid_email",
                default="Unable to manage subscriptions. Invalid email.",
            )
        }
    return {"data": record}


def prepare_email_message(context, template, parameters):
    mail_template = context.restrictedTraverse(template)
    try:
        css = api.portal.get_registry_record(
            "css_styles", interface=IRerUfficiostampaSettings
        )
    except (KeyError, InvalidParameterError):
        css = ""
    if css:
        parameters["css"] = css
    html = mail_template(**parameters)
    # convert it
    html = premailer.transform(html)

    try:
        frontend_url = api.portal.get_registry_record(
            "frontend_url", interface=IRerUfficiostampaSettings
        )
    except (KeyError, InvalidParameterError):
        frontend_url = ""

    if frontend_url:
        source_link = api.portal.get().absolute_url()
        html = html.replace(source_link, frontend_url)
    return html


def mail_from():
    try:
        email_from_name = api.portal.get_registry_record(
            "email_from_name", interface=IRerUfficiostampaSettings
        )
        email_from_address = api.portal.get_registry_record(
            "email_from_address", interface=IRerUfficiostampaSettings
        )
    except (KeyError, InvalidParameterError):
        registry = getUtility(IRegistry)
        mail_settings = registry.forInterface(IMailSchema, prefix="plone")
        email_from_address = mail_settings.email_from_address
        email_from_name = mail_settings.email_from_name
    return formataddr((email_from_name, email_from_address))


def get_next_comunicato_number():
    comunicato_year = api.portal.get_registry_record(
        "comunicato_year", interface=IRerUfficiostampaSettings
    )
    comunicato_number = api.portal.get_registry_record(
        "comunicato_number", interface=IRerUfficiostampaSettings
    )
    current_year = datetime.now().year

    if comunicato_year < current_year:
        # first comunicato of new year
        comunicato_year = current_year
        comunicato_number = 1
        # update value
        api.portal.set_registry_record(
            "comunicato_year",
            current_year,
            interface=IRerUfficiostampaSettings,
        )
        api.portal.set_registry_record(
            "comunicato_number",
            comunicato_number,
            interface=IRerUfficiostampaSettings,
        )
    else:
        comunicato_number += 1
        # update value
        api.portal.set_registry_record(
            "comunicato_number",
            comunicato_number,
            interface=IRerUfficiostampaSettings,
        )

    return f"{comunicato_number}/{comunicato_year}"


MAX_ATTACHMENT_SIZE = 1 * 1024 * 1024


def get_attachments(data, as_link=False, max_attachment_size=MAX_ATTACHMENT_SIZE):
    attachments = []
    for uid in data.get("attachments", []):
        item = api.content.get(UID=uid)
        field = None
        if not item:
            continue
        if item.portal_type == "Image":
            field = item.image
            if field.size > max_attachment_size and not as_link:
                continue
            if field.size <= max_attachment_size and as_link:
                continue
        elif item.portal_type == "File":
            field = item.file
            if field.size > max_attachment_size and not as_link:
                continue
            if field.size <= max_attachment_size and as_link:
                continue
        elif item.portal_type == "Link":
            if not as_link:
                continue
        else:
            raise BadRequest(_("Invalid attachment type"))
        if as_link:
            if item.portal_type == "Link":
                url = item.remoteUrl
            else:
                url = item.absolute_url()
            attachments.append(
                {
                    "url": url,
                    "title": item.Title(),
                    "description": item.Description(),
                }
            )
        else:
            attachments.append(
                {
                    "data": field.data,
                    "filename": field.filename,
                    "content_type": item.content_type(),
                    "url": item.absolute_url(),
                    "title": item.Title(),
                    "description": item.Description(),
                }
            )
    return attachments


def get_attachments_external(data):
    return [
        (
            x["filename"],
            (x["filename"], x["data"], x["content_type"]),
        )
        for x in get_attachments(data)
    ]
