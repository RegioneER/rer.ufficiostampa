# from plone.app.contenttypes.behaviors.richtext import IRichText
# from plone.app.dexterity.textindexer import searchable
from plone.autoform import directives as form
from plone.supermodel import model
from rer.ufficiostampa import _
from zope import schema


class IComunicatoStampa(model.Schema):
    message_sent = schema.Bool(
        title=_("label_sent", default="Sent"),
        description="",
        required=False,
        default=False,
    )
    comunicato_number = schema.TextLine(title="", description="", required=False)

    tipologia_news = schema.TextLine(
        title=_("label_tipologia_news", default="Tipologia News"),
        description="",
        required=True,
        default="Comunicato Stampa",
        readonly=True,
    )
    form.mode(tipologia_news="hidden")
    form.omitted("message_sent")
    form.omitted("comunicato_number")

    # set text field as searchable in SearchableText
    # searchable(IRichText, "text")


class IInvitoStampa(IComunicatoStampa):
    """ """
