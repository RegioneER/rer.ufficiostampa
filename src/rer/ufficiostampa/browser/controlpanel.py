from collective.z3cform.jsonwidget.browser.widget import JSONFieldWidget
from plone import api
from plone.app.registry.browser import controlpanel
from Products.CMFPlone.resources import add_bundle_on_request
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from rer.ufficiostampa import _
from rer.ufficiostampa.interfaces import ILegislaturesRowSchema
from rer.ufficiostampa.interfaces import IRerUfficiostampaSettings
from z3c.form import button
from z3c.form import field
from z3c.form.interfaces import HIDDEN_MODE


class UfficiostampaSettingsEditForm(controlpanel.RegistryEditForm):
    """ """

    schema = IRerUfficiostampaSettings
    id = "UfficiostampaSettingsEditForm"
    label = _("Ufficio Stampa settings")
    description = ""

    fields = field.Fields(IRerUfficiostampaSettings)
    fields["legislatures"].widgetFactory = JSONFieldWidget

    @property
    def can_manage_settings(self):
        current = api.user.get_current()
        return api.user.has_permission(
            "rer.ufficiostampa: Manage Settings", user=current
        )

    def updateWidgets(self):
        """ """
        super().updateWidgets()
        self.widgets["legislatures"].schema = ILegislaturesRowSchema

        if not self.can_manage_settings:
            fields = [
                "token_secret",
                "token_salt",
                "frontend_url",
                "external_sender_url",
                "css_styles",
                "comunicato_number",
                "comunicato_year",
            ]
            for field_id in fields:
                self.widgets[field_id].mode = HIDDEN_MODE

    @button.buttonAndHandler(_("Save"), name="save")
    def handleSave(self, action):
        super().handleSave(self, action)

    @button.buttonAndHandler(_("Cancel"), name="cancel")
    def handleCancel(self, action):
        if not self.can_manage_settings:
            api.portal.show_message(
                message=_("Changes canceled."),
                type="info",
                request=self.request,
            )
            self.request.response.redirect(
                "{}/channels-management".format(api.portal.get().absolute_url())
            )
        else:
            super().handleCancel(self, action)


class UfficiostampaSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    """ """

    form = UfficiostampaSettingsEditForm
    index = ViewPageTemplateFile("templates/controlpanel_layout.pt")

    def __call__(self):
        add_bundle_on_request(self.request, "z3cform-jsonwidget-bundle")
        return super().__call__()

    def can_access_controlpanels(self):
        current = api.user.get_current()
        return api.user.has_permission("Manage portal", user=current)
