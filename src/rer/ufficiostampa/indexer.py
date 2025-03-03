from plone.indexer.decorator import indexer
from rer.ufficiostampa.interfaces import IComunicatoStampa


@indexer(IComunicatoStampa)
def arguments(comunicato, **kw):
    arguments = getattr(comunicato, "arguments", [])
    if not arguments:
        return []
    return arguments


@indexer(IComunicatoStampa)
def legislature(comunicato, **kw):
    legislature = getattr(comunicato, "legislature", "")
    return legislature
