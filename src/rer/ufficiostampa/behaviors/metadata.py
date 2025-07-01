from plone.app.dexterity import _
from plone.app.dexterity.behaviors.metadata import Basic
from plone.app.dexterity.behaviors.metadata import IBasic
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from zope import schema
from zope.interface import provider


@provider(IFormFieldProvider)
class IBasicComunicato(IBasic):
    title = schema.Text(title=_("label_title", default="Title"), required=True)
    form.widget("title", rows=2)

    description = schema.Text(
        title=_("label_description", default="Summary"),
        description="",
        required=True,
        missing_value="",
    )


@provider(IFormFieldProvider)
class IBasicInvito(IBasic):
    title = schema.Text(title=_("label_title", default="Title"), required=True)
    form.widget("title", rows=2)


class BasicComunicato(Basic):
    """
    Basic methods to store title and description
    """


class BasicInvito(Basic):
    """
    Basic methods to store title and description
    """
