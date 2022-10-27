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


def getVocabularyTermsForForm(vocab_name):
    """
    Return the values of vocabulary
    """
    portal = api.portal.get()
    utility = getUtility(IVocabularyFactory, vocab_name)

    values = []

    vocab = utility(portal)

    for entry in vocab:
        if entry.title != u"select_label":
            values.append({"value": entry.value, "label": entry.title})
    values[0]["isFixed"] = True
    return values


def getArguments():
    legislatures = getVocabularyTermsForForm(
        vocab_name="rer.ufficiostampa.vocabularies.legislatures",
    )

    res = {}
    for legislature in legislatures:
        key = legislature.get("value", "")
        arguments = []
        for brain in api.content.find(legislature=key):
            for argument in brain.arguments:
                argument_dict = {"value": argument, "label": argument}
                if argument_dict not in arguments:
                    arguments.append(argument_dict)
        res[key] = sorted(arguments, key=lambda x: x["label"])
    return res


def getTypesValues():
    res = [
        {"value": "ComunicatoStampa", "label": "Comunicato Stampa"},
        {"value": "InvitoStampa", "label": "Invito Stampa"},
    ]
    return res


def getTypesDefault():
    res = ["ComunicatoStampa"]
    if not api.user.is_anonymous():
        res.append("InvitoStampa")
    return res


def getSearchFields():
    request = getRequest()
    legislatures = getVocabularyTermsForForm(
        vocab_name="rer.ufficiostampa.vocabularies.legislatures",
    )
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
            "id": "portal_type",
            "label": translate(
                _("label_portal_type", default="Type"),
                context=request,
            ),
            "help": "",
            "type": "checkbox",
            "options": getTypesValues(),
            "default": getTypesDefault(),
            "hidden": api.user.is_anonymous(),
        },
        {
            "id": "created",
            "label": translate(
                _("comunicati_search_created_label", default=u"Date"),
                context=request,
            ),
            "help": "",
            "type": "date",
        },
        {
            "id": "legislature",
            "label": translate(
                _("label_legislature", default="Legislature"),
                context=request,
            ),
            "help": "",
            "type": "select",
            "multivalued": True,
            "options": legislatures,
            "default": [legislatures[0]["value"]],
            "slave": {
                "id": "arguments",
                "label": translate(
                    _("legislature_arguments_label", default="Arguments"),
                    context=request,
                ),
                "help": "",
                "type": "select",
                "multivalued": True,
                "slaveOptions": getArguments()
                # "options": getVocabularyTermsForForm(
                #     context=portal,
                #     vocab_name="rer.ufficiostampa.vocabularies.all_arguments",
                # ),
            },
        },
    ]


@implementer(IPublishTraverse)
class SearchParametersGet(Service):
    def __init__(self, context, request):
        super(SearchParametersGet, self).__init__(context, request)

    def reply(self):
        return getSearchFields()
