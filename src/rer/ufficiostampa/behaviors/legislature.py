from plone import api
from plone.api.exc import InvalidParameterError
from plone.app.dexterity import _
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from rer.ufficiostampa.interfaces.settings import IRerUfficiostampaSettings
from zope import schema
from zope.interface import provider

import json
import logging


logger = logging.getLogger(__name__)


def defaultLegislature():
    try:
        legislatures = json.loads(
            api.portal.get_registry_record(
                "legislatures", interface=IRerUfficiostampaSettings
            )
        )
    except (KeyError, InvalidParameterError, TypeError) as e:
        logger.exception(e)
        return ""

    if not legislatures:
        return ""
    current = legislatures[-1]
    return current.get("legislature", "")


@provider(IFormFieldProvider)
class ILegislatureComunicati(model.Schema):
    legislature = schema.TextLine(
        title=_("label_legislature", default="Legislature"),
        description="",
        required=True,
        defaultFactory=defaultLegislature,
    )
    form.mode(legislature="display")
