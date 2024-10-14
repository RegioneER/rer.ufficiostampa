from DateTime import DateTime
from plone import api
from plone.api.exc import InvalidParameterError
from Products.Five import BrowserView
from rer.ufficiostampa.interfaces.settings import IRerUfficiostampaSettings
from rer.ufficiostampa.utils import get_attachments
from rer.ufficiostampa.utils import get_site_title
from rer.ufficiostampa.utils import prepare_email_message
from zope.interface import implementer
from zope.interface import Interface
from zope.publisher.interfaces import IPublishTraverse


class IView(Interface):
    pass


@implementer(IView)
class View(BrowserView):

    def get_html(self):
        notes = self.request.form.get("notes")
        return prepare_email_message(
            context=self.context,
            template="@@send_mail_template",
            parameters={
                "notes": notes,
                "site_title": get_site_title(),
                "date": DateTime(),
                "links": get_attachments(data=self.request.form, as_link=True),
            },
        )

    def get_styles(self):
        try:
            return api.portal.get_registry_record(
                "css_styles", interface=IRerUfficiostampaSettings
            )
        except (KeyError, InvalidParameterError):
            return ""

    def get_attachments(self):
        return get_attachments(data=self.request.form)


@implementer(IPublishTraverse)
class Download(BrowserView):

    def publishTraverse(self, request, id):
        return self

    def __call__(self):
        return self.context()
