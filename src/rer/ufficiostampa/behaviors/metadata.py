from plone.app.dexterity import _
from plone.app.dexterity import searchable
from plone.app.dexterity.behaviors.metadata import Basic
from plone.app.dexterity.behaviors.metadata import IBasic
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from zope import schema
from zope.interface import provider


@provider(IFormFieldProvider)
class IBasicComunicati(IBasic):
    title = schema.Text(title=_("label_title", default="Title"), required=True)
    form.widget("title", rows=2)

    searchable("title")


class BasicComunicati(Basic):
    """
    Basic methods to store title and description
    """
