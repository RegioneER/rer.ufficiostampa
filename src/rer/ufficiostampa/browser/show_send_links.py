from plone import api
from Products.Five import BrowserView


class View(BrowserView):
    def __call__(self):
        portal_type = self.context.portal_type
        if portal_type not in ["ComunicatoStampa", "InvitoStampa"]:
            return False
        if portal_type == "InvitoStampa":
            return True
        review_state = api.content.get_state(obj=self.context)
        if portal_type == "ComunicatoStampa" and review_state == "published":  # noqa
            return True
        return False
