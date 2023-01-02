# -*- coding: utf-8 -*-
from collective import dexteritytextindexer
from plone.app.dexterity import _
from plone.app.dexterity.behaviors.metadata import IBasic, Basic
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from zope import schema
from zope.interface import provider


@provider(IFormFieldProvider)
class IBasicComunicati(IBasic):
    title = schema.Text(title=_(u"label_title", default=u"Title"), required=True)
    form.widget("title", rows=2)

    dexteritytextindexer.searchable("title")


class BasicComunicati(Basic):
    """
    Basic methods to store title and description
    """
