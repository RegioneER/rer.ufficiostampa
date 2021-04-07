# -*- coding: utf-8 -*-
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service
from rer.ufficiostampa.interfaces import ISendHistoryStore
from zope.component import getUtility
from plone.restapi.batching import HypermediaBatch
from plone.protect.interfaces import IDisableCSRFProtection
from zope.interface import alsoProvides


class SendHistoryGet(Service):
    def reply(self):
        tool = getUtility(ISendHistoryStore)

        batch = HypermediaBatch(self.request, tool.search())
        data = {
            "@id": batch.canonical_url,
            "items": [self.expand_data(x) for x in batch],
            "items_total": batch.items_total,
        }
        links = batch.links
        if links:
            data["batching"] = links
        return data

    def expand_data(self, record):
        data = {k: json_compatible(v) for k, v in record.attrs.items()}
        data["id"] = record.intid
        return data


class SendHistoryClearGet(Service):
    def reply(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        # soup = get_soup("subscriptions_soup", self.context)
        tool = getUtility(ISendHistoryStore)
        tool.clear()
        return self.reply_no_content()
