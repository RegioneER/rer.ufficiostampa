from Acquisition import aq_base
from plone import api
from plone.api.exc import InvalidParameterError
from plone.app.vocabularies.catalog import KeywordsVocabulary
from plone.app.vocabularies.terms import safe_encode
from rer.ufficiostampa.interfaces import IRerUfficiostampaSettings
from zope.interface import directlyProvides
from zope.interface import implementer
from zope.schema.interfaces import ITitledTokenizedTerm
from zope.schema.interfaces import ITokenizedTerm
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

import json


@implementer(ITokenizedTerm)
class UnsafeSimpleTerm:
    """
    Needed to allow unicode tokens in vocabularies.
    Copied from plone.volto < 5.0.0 (https://github.com/plone/plone.volto/blob/5.0.0b2/src/plone/volto/vocabularies/subject.py)
    It is removed in plone.volto 5.0.0 because volto 18 ignore tokenized tokens but we are still using 17
    """

    def __init__(self, value, token, title):
        """Create a term for value and token. If token is omitted,
        str(value) is used for the token.  If title is provided,
        term implements ITitledTokenizedTerm.
        """
        self.value = value
        self.token = token
        self.title = title
        if title is not None:
            directlyProvides(self, ITitledTokenizedTerm)


def unsafe_simplevocabulary_from_values(values, query=None):
    return SimpleVocabulary(
        [
            UnsafeSimpleTerm(value, value, value)
            for value in values
            if query is None or safe_encode(query) in safe_encode(value)
        ]
    )


@implementer(IVocabularyFactory)
class ArgumentsVocabularyFactory:
    def __call__(self, context):
        stored = getattr(aq_base(context), "legislature", "")
        arguments = []
        try:
            legislatures = json.loads(
                api.portal.get_registry_record(
                    "legislatures", interface=IRerUfficiostampaSettings
                )
            )
            if not legislatures:
                pass
            for data in legislatures:
                if data.get("legislature", "") == stored:
                    arguments = data.get("arguments", [])
                    break
            if not arguments:
                arguments = legislatures[-1].get("arguments", [])
        except (KeyError, InvalidParameterError, TypeError):
            arguments = []
        for arg in getattr(context, "arguments", []) or []:
            if arg and arg not in arguments:
                arguments.append(arg)
        return unsafe_simplevocabulary_from_values(sorted(arguments))


@implementer(IVocabularyFactory)
class ChannelsVocabularyFactory:
    def __call__(self, context):
        try:
            subscription_channels = api.portal.get_registry_record(
                "subscription_channels",
                interface=IRerUfficiostampaSettings,
            )
        except (KeyError, InvalidParameterError):
            subscription_channels = []
        return unsafe_simplevocabulary_from_values(subscription_channels)


@implementer(IVocabularyFactory)
class AttachmentsVocabularyFactory:
    def __call__(self, context):
        terms = []
        for child in context.listFolderContents(
            contentFilter={"portal_type": ["File", "Image"]}
        ):
            terms.append(
                SimpleTerm(
                    value=child.UID(),
                    token=child.UID(),
                    title=child.Title(),
                )
            )
        return SimpleVocabulary(terms)


@implementer(IVocabularyFactory)
class LegislaturesVocabularyFactory:
    def __call__(self, context):
        """
        return a list of legislature names.
        There are all possible index values sorted on reverse order from
        the registry one (last legislature is the first one).
        """
        try:
            registry_val = json.loads(
                api.portal.get_registry_record(
                    "legislatures", interface=IRerUfficiostampaSettings
                )
            )
            registry_legislatures = [x.get("legislature", "") for x in registry_val]
            registry_legislatures.reverse()
        except (KeyError, InvalidParameterError, TypeError):
            registry_legislatures = []

        pc = api.portal.get_tool(name="portal_catalog")
        catalog_legislatures = pc.uniqueValuesFor("legislature")

        legislatures = [x for x in registry_legislatures if x in catalog_legislatures]
        return unsafe_simplevocabulary_from_values(legislatures)


@implementer(IVocabularyFactory)
class AllArgumentsVocabularyFactory(KeywordsVocabulary):
    keyword_index = "arguments"


AllArgumentsVocabulary = AllArgumentsVocabularyFactory()
ArgumentsVocabulary = ArgumentsVocabularyFactory()
ChannelsVocabulary = ChannelsVocabularyFactory()
AttachmentsVocabulary = AttachmentsVocabularyFactory()
LegislaturesVocabulary = LegislaturesVocabularyFactory()
