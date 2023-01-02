# -*- coding: utf-8 -*-
from zope.component import getUtility
from rer.ufficiostampa.interfaces import ISubscriptionsStore
from rer.ufficiostampa.interfaces import IRerUfficiostampaSettings
from plone import api

import logging

logger = logging.getLogger(__name__)

DEFAULT_PROFILE = "profile-rer.ufficiostampa:default"


def to_1100(context):
    tool = getUtility(ISubscriptionsStore)
    subscription_channels = api.portal.get_registry_record(
        "subscription_channels",
        interface=IRerUfficiostampaSettings,
    )
    for record in tool.search():
        channels = []
        updated = False
        for channel in record._attrs.get("channels", []):
            channel = channel.strip()
            if channel not in subscription_channels:
                updated = True
                continue
            if channel in channels:
                updated = True
                continue
            channels.append(channel)

        if updated:
            logger.info(
                "{}: {} => {}".format(
                    record._attrs["email"], record._attrs["channels"], channels
                )
            )

            record._attrs["channels"] = channels
            tool.soup.reindex(records=[record])


def to_1200(context):
    logger.info("Enable versioning")
    context.runImportStepFromProfile(DEFAULT_PROFILE, "typeinfo")
    context.runImportStepFromProfile(DEFAULT_PROFILE, "plone-difftool")
    context.runImportStepFromProfile(DEFAULT_PROFILE, "repositorytool")


def to_1300(context):
    i = 0
    brains = api.content.find(portal_type=["ComunicatoStampa", "InvitoStampa"])
    tot = len(brains)
    for brain in brains:
        i += 1
        if i % 100 == 0:
            logger.info("Progress: [{}/{}]".format(i, tot))
        item = brain.getObject()
        setattr(item, "legislature", brain.legislature)


def to_1400(context):
    logger.info("Enable collective.dexteritytextindexer behavior")
    context.runImportStepFromProfile(DEFAULT_PROFILE, "typeinfo")

    logger.info("Reindex contents")
    i = 0
    brains = api.content.find(portal_type=["ComunicatoStampa", "InvitoStampa"])
    tot = len(brains)
    for brain in brains:
        i += 1
        if i % 100 == 0:
            logger.info("Progress: [{}/{}]".format(i, tot))
        item = brain.getObject()
        item.reindexObject(idxs=["SearchableText"])
