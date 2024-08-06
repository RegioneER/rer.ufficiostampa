from DateTime import DateTime
from plone import api
from plone.api.exc import InvalidParameterError
from Products.Five import BrowserView
from rer.ufficiostampa.interfaces.settings import IRerUfficiostampaSettings
from rer.ufficiostampa.utils import get_site_title
from rer.ufficiostampa.utils import prepare_email_message


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
