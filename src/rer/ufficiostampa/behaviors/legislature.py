from plone import api
from plone.api.exc import InvalidParameterError
from plone.app.z3cform.widget import AjaxSelectFieldWidget
from plone.autoform import directives
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from rer.ufficiostampa import _
from rer.ufficiostampa.interfaces.settings import IRerUfficiostampaSettings
from zope import schema
from zope.interface import provider

import json
import logging


logger = logging.getLogger(__name__)


def defaultLegislature(context=None):
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
    arguments = schema.Tuple(
        title=_("arguments_label", default="Arguments"),
        description=_("arguments_help", default="Select one or more values."),
        value_type=schema.TextLine(),
        required=True,
        missing_value=(),
    )

    directives.widget(
        "arguments",
        AjaxSelectFieldWidget,
        vocabulary="rer.ufficiostampa.vocabularies.arguments",
        pattern_options={"allowNewItems": "false"},
    )

    legislature = schema.TextLine(
        title=_("label_legislature", default="Legislature"),
        description="",
        required=True,
        defaultFactory=defaultLegislature,
    )
    form.mode(legislature="display")
