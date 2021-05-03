# -*- coding: utf-8 -*-
from rer.ufficiostampa.utils import get_next_comunicato_number


def setNumber(item, event):
    if item.portal_type != "ComunicatoStampa":
        return
    if event.action != "publish":
        return
    if getattr(item, "comunicato_number", ""):
        # already set
        return
    setattr(item, "comunicato_number", get_next_comunicato_number())
