from DateTime import DateTime
from plone import api
from plone.api.exc import InvalidParameterError
from Products.Five import BrowserView
from rer.ufficiostampa.interfaces.settings import IRerUfficiostampaSettings
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
                "folders": self.get_folders_attachments(),
                "links": self.get_links_attachments(),
            },
        )

    def get_styles(self):
        try:
            return api.portal.get_registry_record(
                "css_styles", interface=IRerUfficiostampaSettings
            )
        except (KeyError, InvalidParameterError):
            return ""

    def get_folders_attachments(self):
        if self.context.portal_type == "InvitoStampa":
            return []
        return self.context.listFolderContents(
            contentFilter={"portal_type": ["Folder"]}
        )

    def get_links_attachments(self):
        return [
            b.getObject() for b in api.content.find(self.context, portal_type=["Link"])
        ]


@implementer(IPublishTraverse)
class Download(BrowserView):

    def publishTraverse(self, request, id):
        return self

    def __call__(self):
        return self.context()
