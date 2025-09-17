from datetime import datetime
from plone import api
from plone.api.exc import InvalidParameterError
from plone.formwidget.namedfile.converter import b64decode_file
from plone.namedfile.browser import Download
from plone.namedfile.file import NamedImage
from Products.Five import BrowserView
from rer.blocks2html.interfaces import IBlocksToHtml
from rer.ufficiostampa.interfaces import IUfficioStampaLogoView
from rer.ufficiostampa.interfaces.settings import IRerUfficiostampaSettings
from rer.ufficiostampa.utils import get_attachments
from rer.ufficiostampa.utils import get_folder_attachments
from rer.ufficiostampa.utils import get_site_title
from rer.ufficiostampa.utils import prepare_email_message
from zope.component import getUtility
from zope.interface import implementer
from zope.interface import Interface
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces import NotFound


@implementer(IUfficioStampaLogoView)
class UfficioStampaLogoView(BrowserView):
    """"""

    def __call__(self):
        return

    def absolute_url(self):
        """
        Needed for plone.namedfile >= 6.4.0 with canonical header
        """
        return f"{self.context.portal_url()}/{self.__name__}"


@implementer(IPublishTraverse)
class ImagesLogoView(Download):
    def __init__(self, context, request):
        super().__init__(context=context, request=request)
        self.data = None

    def publishTraverse(self, request, name):
        super().publishTraverse(request=request, name=name)
        value = api.portal.get_registry_record(
            "mail_logo", interface=IRerUfficiostampaSettings
        )
        if value:
            filename, data = b64decode_file(value)
            data = NamedImage(data=data, filename=filename)
            self.data = data
        return self

    def _getFile(self):
        if not self.data:
            raise NotFound(self, "", self.request)
        return self.data


class IView(Interface):
    pass


class BaseView(BrowserView):
    """"""

    def get_logo_url(self):
        value = api.portal.get_registry_record(
            "mail_logo", interface=IRerUfficiostampaSettings
        )
        if not value:
            return ""
        filename, data = b64decode_file(value)
        portal_state = api.content.get_view(
            name="plone_portal_state", context=self.context, request=self.request
        )

        return f"{portal_state.navigation_root_url()}/ufficiostampa-logo/@@images/{filename}"

    def get_text(self):
        text = getattr(
            self.context, "text", {"blocks": {}, "blocks_layout": {"items": []}}
        )
        if not text:
            return ""
        blocks_converter = getUtility(IBlocksToHtml)
        return blocks_converter(
            context=self.context,
            blocks=text.get("blocks", {}),
            blocks_layout=text.get("blocks_layout", {}),
        )


class SendMailView(BaseView):
    """"""


@implementer(IView)
class SendPreviewView(BaseView):
    def get_html(self):
        notes = self.request.form.get("notes")
        return prepare_email_message(
            context=self.context,
            template="@@send_mail_template",
            parameters={
                "notes": notes,
                "site_title": get_site_title(),
                "date": datetime.now(),
                "folders": get_folder_attachments(context=self.context),
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
