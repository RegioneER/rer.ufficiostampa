# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
from plone.supermodel import model
from rer.ufficiostampa import _
from zope import schema


class IRerUfficiostampaSettings(model.Schema):
    legislatures = schema.SourceText(
        title=_("legislatures_label", default=u"List of legislatures.",),
        description=_(
            "legislatures_help",
            default=u"This is a list of all legislatures. The last one is the"
            u" one used to fill fields in a new Comunicato.",
        ),
        required=True,
    )


class ILegislaturesRowSchema(model.Schema):
    legislature = schema.SourceText(
        title=_("legislature_label", default=u"Legislature",),
        description=_(
            "legislature_help", default=u"Insert the legislature name.",
        ),
        required=True,
    )
    arguments = schema.List(
        title=_("legislature_arguments_label", default=u"Arguments",),
        description=_(
            "legislature_arguments_help",
            default=u"Insert a list of arguments related to this legislature."
            u" One per line.",
        ),
        required=True,
        value_type=schema.TextLine(),
    )
