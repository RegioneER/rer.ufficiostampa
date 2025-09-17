from plone import api
from plone.restapi.batching import HypermediaBatch
from plone.restapi.search.utils import unflatten_dotted_dict
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service
from rer.ufficiostampa.restapi.services.search_comunicati_archive.search_handler import (
    DettaglioComunicato,
)
from rer.ufficiostampa.restapi.services.search_comunicati_archive.search_handler import (
    RicercaComunicatiAdvanced,
)
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


ALLOWED_KEYS = [
    "codStruttura",  # string 10
    "tiporicerca",  # string
    "codArea",  # string 10
    "titolo",  # string 255
    "oggetto",  # string 255
    "parolechiave",  # string 255
    "dataDa",  # string YYYY-MM-DD
    "dataA",  # string YYYY-MM-DD
    "nrMaxComunicati",  # int
    "soloPrincipale",  # int (def. 0)
]


class SearchComunicatiArchiveGet(Service):
    """ """

    def reply(self):
        query = self.fix_form()
        if not query or query.keys() == ["b_size", "b_start"]:
            comunicati = []
        else:
            comunicati = (
                RicercaComunicatiAdvanced(empty_if_errors=True, **query)
                .as_list()
                .get("results", [])
            )
        batch = HypermediaBatch(self.request, comunicati)
        portal_url = api.portal.get().absolute_url()
        results = {}
        results["@id"] = batch.canonical_url
        results["items_total"] = batch.items_total
        links = batch.links
        if links:
            results["batching"] = links

        results["items"] = []
        for brain in batch:
            data = {k: json_compatible(v) for (k, v) in brain.items()}
            data["@id"] = (
                f"{portal_url}/@dettaglio-comunicato-archive/{brain.get('codice', '')}"
            )

            results["items"].append(data)

        return results

    def fix_form(self):
        form = self.request.form.copy()
        form = unflatten_dotted_dict(form)
        keys = list(form.keys())
        if keys == ["b_size"] or keys == ["b_size", "b_start"]:
            # non vogliamo tornare tutti i risultati
            return {}
        query = {
            "tiporicerca": "like",
            "codStruttura": "st_giunta",
        }
        for k, v in form.items():
            if k not in ALLOWED_KEYS:
                continue
            query[k] = v

        return query


@implementer(IPublishTraverse)
class DettaglioComunicatoArchiveGet(Service):
    """ """

    def __init__(self, context, request):
        super().__init__(context, request)
        self.params = []

    def publishTraverse(self, request, code):
        self.params.append(code)
        return self

    def reply(self):
        codice = self.params and self.params[0] or None
        if not codice:
            self.request.response.setStatus(404)
            return

        comunicato = DettaglioComunicato(codComunicato=codice).comunicato

        if not comunicato:
            self.request.response.setStatus(404)
            return

        return json_compatible(comunicato)
