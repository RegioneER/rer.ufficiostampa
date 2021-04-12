# -*- coding: utf-8 -*-
from plone import api
from plone.restapi.services import Service
from rer.ufficiostampa import _
from zope.component import getUtility
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from zope.schema.interfaces import IVocabularyFactory


def getVocabularyTermsForForm(vocab_name, context):
    """
    Return the values of vocabulary
    """
    utility = getUtility(IVocabularyFactory, vocab_name)

    values = []

    vocab = utility(context)

    for entry in vocab:
        if entry.title != u"select_label":
            values.append({"value": entry.value, "label": entry.title})
    return values


def getSearchFields():
    request = getRequest()
    portal = api.portal.get()

    return [
        {
            "id": "SearchableText",
            "label": translate(
                _("comunicati_search_text_label", default=u"Search text"),
                context=request,
            ),
            "help": "",
            "type": "text",
        },
        {
            "id": "legislature",
            "label": translate(
                _("label_legislature", default="Legislature"), context=request,
            ),
            "help": "",
            "type": "select",
            "multivalued": True,
            "options": getVocabularyTermsForForm(
                context=portal,
                vocab_name="rer.ufficiostampa.vocabularies.legislatures",
            ),
        },
        {
            "id": "arguments",
            "label": translate(
                _("legislature_arguments_label", default="Arguments"),
                context=request,
            ),
            "help": "",
            "type": "select",
            "multivalued": True,
            "options": getVocabularyTermsForForm(
                context=portal,
                vocab_name="rer.ufficiostampa.vocabularies.all_arguments",
            ),
        },
        {
            "id": "Subject",
            "label": translate(
                _("subject_label", default="Subjects"), context=request,
            ),
            "help": "",
            "type": "select",
            "multivalued": True,
            "options": getVocabularyTermsForForm(
                context=portal, vocab_name="plone.app.vocabularies.Keywords"
            ),
        },
    ]


@implementer(IPublishTraverse)
class SearchParametersGet(Service):
    def __init__(self, context, request):
        super(SearchParametersGet, self).__init__(context, request)

    def reply(self):
        return getSearchFields()
