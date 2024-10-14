"""JsonSchema providers."""

from plone import api
from plone.api.exc import InvalidParameterError
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.types.adapters import ListJsonSchemaProvider as Base
from plone.restapi.types.interfaces import IJsonSchemaProvider
from rer.ufficiostampa.interfaces.settings import IRerUfficiostampaSettings
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.interface import Interface
from zope.schema.interfaces import IList


@adapter(IList, Interface, Interface)
@implementer(IJsonSchemaProvider)
class ACuraDiJsonSchemaProvider(Base):
    def additional(self):
        info = super().additional()
        # XXX: va controllato che la richiesta arrivi per lo schema del CT ComunicatoStampa
        #      perchè anche altri CT potrebbero avere un campo a_cura_di
        if self.request.URL.endswith("@types/ComunicatoStampa"):
            # Add default
            if "default" not in info:
                try:
                    default = api.portal.get_registry_record(
                        "default_acura_di", interface=IRerUfficiostampaSettings
                    )
                except (KeyError, InvalidParameterError):
                    default = ""
                # default = "/amministrazione/aree-amministrative/ufficio-stampa"
                if default:
                    target = api.content.get(default)
                    if target:
                        info["default"] = [
                            getMultiAdapter(
                                (target, self.request), ISerializeToJsonSummary
                            )()
                        ]
        return info


@adapter(IList, Interface, Interface)
@implementer(IJsonSchemaProvider)
class ArgomentiJsonSchemaProvider(Base):
    def additional(self):
        info = super().additional()
        # XXX: va controllato che la richiesta arrivi per lo schema del CT ComunicatoStampa
        #      perchè anche altri CT potrebbero avere un campo tassonomia_argomenti
        if self.request.URL.endswith("@types/ComunicatoStampa"):
            if "default" not in info:
                value = []
                # TODO: sposare con configurazione in plone.registry
                try:
                    default = api.portal.get_registry_record(
                        "default_argomenti", interface=IRerUfficiostampaSettings
                    )
                except (KeyError, InvalidParameterError):
                    default = []
                for path in default:
                    target = api.content.get(path)
                if target:
                    value.append(
                        getMultiAdapter(
                            (target, self.request), ISerializeToJsonSummary
                        )()
                    )
                info["default"] = value
        return info
