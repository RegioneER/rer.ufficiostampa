# -*- coding: utf-8 -*-
from plone.app.z3cform.widget import AjaxSelectFieldWidget
from plone.autoform import directives
from plone.supermodel import model
from rer.ufficiostampa import _
from rer.ufficiostampa.utils import defaultLegislature
from zope import schema


class IComunicatoStampa(model.Schema):
    arguments = schema.Tuple(
        title=_("arguments_label", default=u""),
        description=_("arguments_help", default="Select one or more values."),
        value_type=schema.TextLine(),
        required=False,
        missing_value=(),
    )

    directives.widget(
        "arguments",
        AjaxSelectFieldWidget,
        vocabulary="rer.ufficiostampa.vocabularies.arguments",
    )

    legislature = schema.TextLine(
        title=_(u"label_legislature", default=u"Legislature"),
        description=u"",
        required=True,
        defaultFactory=defaultLegislature,
    )


class IInvitoStampa(IComunicatoStampa):
    """ """
