from plone.dexterity.content import Container
from rer.ufficiostampa.interfaces import ICartellaStampa
from rer.ufficiostampa.interfaces import IComunicatoStampa
from rer.ufficiostampa.interfaces import IInvitoStampa
from zope.interface import implementer


@implementer(IComunicatoStampa)
class ComunicatoStampa(Container):
    """ """


@implementer(IInvitoStampa)
class InvitoStampa(Container):
    """ """


@implementer(ICartellaStampa)
class CartellaStampa(Container):
    """
    Cartella stampa content type.
    """
