from plone.app.contenttypes.behaviors.richtext import IRichText
from plone.app.dexterity.textindexer import searchable
from plone.app.z3cform.widget import AjaxSelectFieldWidget
from plone.autoform import directives
from plone.supermodel import model
from rer.ufficiostampa import _
from rer.ufficiostampa.utils import defaultLegislature
from zope import schema


class IComunicatoStampa(model.Schema):
    arguments = schema.Tuple(
        title=_("arguments_label", default="Arguments"),
        description=_("arguments_help", default="Select one or more values."),
        value_type=schema.TextLine(),
        required=True,
        missing_value=(),
    )

    directives.widget(
        "arguments",
        AjaxSelectFieldWidget,
        vocabulary="rer.ufficiostampa.vocabularies.arguments",
        pattern_options={"allowNewItems": "false"},
    )

    legislature = schema.TextLine(
        title=_("label_legislature", default="Legislature"),
        description="",
        required=True,
        defaultFactory=defaultLegislature,
    )
    directives.mode(legislature="display")

    message_sent = schema.Bool(
        title=_("label_sent", default="Sent"),
        description="",
        required=False,
        default=False,
    )
    comunicato_number = schema.TextLine(title="", description="", required=False)

    directives.omitted("message_sent")
    directives.omitted("comunicato_number")

    # set text field as searchable in SearchableText
    searchable(IRichText, "text")


class IInvitoStampa(IComunicatoStampa):
    """ """
