# -*- coding: utf-8 -*-
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from rer.ufficiostampa.interfaces import IRerUfficiostampaSettings
from plone import api
from plone.api.exc import InvalidParameterError
from plone.app.vocabularies.terms import safe_simplevocabulary_from_values
import json


@implementer(IVocabularyFactory)
class ArgumentsVocabularyFactory(object):
    def __call__(self, context):
        try:
            legislatures = json.loads(
                api.portal.get_registry_record(
                    "legislatures", interface=IRerUfficiostampaSettings
                )
            )
            if legislatures:
                arguments = legislatures[-1].get("arguments", [])
            else:
                arguments = []

        except (KeyError, InvalidParameterError):
            arguments = []
        for arg in getattr(context, "arguments", []):
            if arg and arg not in arguments:
                arguments.append(arg)
        terms = [
            SimpleTerm(value=x, token=x.encode("utf-8"), title=x)
            for x in arguments
        ]
        return SimpleVocabulary(terms)


ArgumentsVocabulary = ArgumentsVocabularyFactory()


@implementer(IVocabularyFactory)
class ChannelsVocabularyFactory(object):
    def __call__(self, context):
        try:
            subscription_channels = api.portal.get_registry_record(
                "subscription_channels", interface=IRerUfficiostampaSettings,
            )
        except (KeyError, InvalidParameterError):
            subscription_channels = []
        return safe_simplevocabulary_from_values(subscription_channels)


ArgumentsVocabulary = ArgumentsVocabularyFactory()
ChannelsVocabulary = ChannelsVocabularyFactory()
