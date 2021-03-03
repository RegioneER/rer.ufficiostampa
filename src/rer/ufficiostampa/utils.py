# -*- coding: utf-8 -*-
from plone import api
from plone.api.exc import InvalidParameterError
from rer.ufficiostampa.interfaces.settings import IRerUfficiostampaSettings

import json


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
