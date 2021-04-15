# -*- coding: utf-8 -*-
from collective.z3cform.jsonwidget.browser.widget import JSONFieldWidget
from plone import api
from plone.app.registry.browser import controlpanel
from Products.CMFPlone.resources import add_bundle_on_request
from rer.ufficiostampa import _
from rer.ufficiostampa.interfaces import ILegislaturesRowSchema
from rer.ufficiostampa.interfaces import IRerUfficiostampaSettings
from z3c.form import field
from z3c.form.interfaces import HIDDEN_MODE
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class UfficiostampaSettingsEditForm(controlpanel.RegistryEditForm):
    """
    """

    schema = IRerUfficiostampaSettings
    id = "UfficiostampaSettingsEditForm"
    label = _(u"Ufficio Stampa settings")
    description = u""

    fields = field.Fields(IRerUfficiostampaSettings)
    fields["legislatures"].widgetFactory = JSONFieldWidget

    def updateWidgets(self):
        """
        """
        super(UfficiostampaSettingsEditForm, self).updateWidgets()
        self.widgets["legislatures"].schema = ILegislaturesRowSchema

        current = api.user.get_current()
        if not api.user.has_permission(
            "rer.ufficiostampa: Manage Settings", user=current
        ):
            fields = [
                "token_secret",
                "token_salt",
                "frontend_url",
                "external_sender_url",
                "css_styles",
            ]
            for field_id in fields:
                self.widgets[field_id].mode = HIDDEN_MODE


class UfficiostampaSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    """
    """

    form = UfficiostampaSettingsEditForm
    index = ViewPageTemplateFile("templates/controlpanel_layout.pt")

    def __call__(self):
        add_bundle_on_request(self.request, "z3cform-jsonwidget-bundle")
        return super(UfficiostampaSettingsControlPanel, self).__call__()

    def can_access_controlpanels(self):
        current = api.user.get_current()
        return api.user.has_permission("Manage portal", user=current)
