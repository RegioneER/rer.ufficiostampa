from plone.app.dexterity import _
from plone.app.dexterity.behaviors.metadata import Basic
from plone.app.dexterity.behaviors.metadata import IBasic
from plone.app.dexterity.textindexer import searchable
from plone.app.z3cform.widget import AjaxSelectFieldWidget
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from zope import schema
from zope.interface import provider


@provider(IFormFieldProvider)
class IBasicComunicati(IBasic):
    title = schema.Text(title=_("label_title", default="Title"), required=True)
    form.widget("title", rows=2)

    arguments = schema.Tuple(
        title=_("arguments_label", default="Arguments"),
        description=_("arguments_help", default="Select one or more values."),
        value_type=schema.TextLine(),
        required=True,
        missing_value=(),
    )

    form.widget(
        "arguments",
        AjaxSelectFieldWidget,
        vocabulary="rer.ufficiostampa.vocabularies.arguments",
        pattern_options={"allowNewItems": "false"},
    )

    searchable("title")


class BasicComunicati(Basic):
    """
    Basic methods to store title and description
    """
