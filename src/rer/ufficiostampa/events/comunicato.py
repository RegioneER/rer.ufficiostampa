# -*- coding: utf-8 -*-
from rer.ufficiostampa.utils import get_next_comunicato_number
from plone import api


def setNumber(item, event):
    if item.portal_type != "ComunicatoStampa":
        return
    if event.action != "publish":
        return
    if getattr(item, "comunicato_number", ""):
        # already set
        return
    setattr(item, "comunicato_number", get_next_comunicato_number())


def createComunicato(item, event):
    """
    Reset it when copy a comunicato and force set legislature
    """
    setattr(item, "comunicato_number", "")
    setattr(item, "message_sent", False)

    # this is needed because it's a readonly field and that doesn't store anything
    # in the content. Side effect is that it also have a defaultFactory value that
    # always return the latest legislature. When you try to edit an item for a past
    # legislature, you always get the latest one, instead the "stored" one.

    setattr(item, "legislature", getattr(item, "legislature", ""))


def fixText(item, event):
    transform_tool = api.portal.get_tool(name="portal_transforms")
    item.title = transform_tool.convert(
        "html_to_web_intelligent_plain_text", item.title
    ).getData()
    item.description = transform_tool.convert(
        "html_to_web_intelligent_plain_text", item.description
    ).getData()
