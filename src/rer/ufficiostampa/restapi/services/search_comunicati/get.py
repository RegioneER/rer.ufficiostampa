from plone.restapi.search.handler import SearchHandler
from plone.restapi.search.utils import unflatten_dotted_dict
from plone.restapi.services.search.get import SearchGet


class SearchComunicatiGet(SearchGet):
    """ """

    def reply(self):
        query = self.request.form.copy()
        query = unflatten_dotted_dict(query)
        # force to search only 'Comunicati' content type
        query["portal_type"] = "ComunicatoStampa"
        return SearchHandler(self.context, self.request).search(query)
