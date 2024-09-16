"""JsonSchema providers."""
from plone.restapi.types.interfaces import IJsonSchemaProvider
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.interface import Interface
from zope.schema.interfaces import IList
from plone.restapi.types.adapters import ListJsonSchemaProvider as Base
from plone import api
from plone.restapi.interfaces import ISerializeToJsonSummary



@adapter(IList, Interface, Interface)
@implementer(IJsonSchemaProvider)
class ACuraDiJsonSchemaProvider(Base):
    def additional(self):
        info = super().additional()
        # XXX: va contrallato che la richiesta arrivi per lo schema del CT ComunicatoStampa
        #      perchè anche altri CT potrebbero avere un campo a_cura_di
        if self.request.URL.endswith("@types/ComunicatoStampa"):
            # Add default
            if "default" not in info:
                default = "/amministrazione/aree-amministrative/ufficio-stampa"
                target = api.content.get(default)
                if target:
                    info["default"] = [
                        getMultiAdapter(
                            (target, self.request), ISerializeToJsonSummary
                        )()
                    ]
        return info
