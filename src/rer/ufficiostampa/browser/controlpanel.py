# -*- coding: utf-8 -*-
from collective.z3cform.jsonwidget.browser.widget import JSONFieldWidget
from plone.app.registry.browser import controlpanel
from Products.CMFPlone.resources import add_bundle_on_request
from rer.ufficiostampa import _
from rer.ufficiostampa.interfaces import IRerUfficiostampaSettings
from rer.ufficiostampa.interfaces import ILegislaturesRowSchema
from z3c.form import field


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
        Hide some fields
        """
        super(UfficiostampaSettingsEditForm, self).updateWidgets()
        self.widgets["legislatures"].schema = ILegislaturesRowSchema


class UfficiostampaSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    """
    """

    def __call__(self):
        add_bundle_on_request(self.request, "z3cform-jsonwidget-bundle")
        return super(UfficiostampaSettingsControlPanel, self).__call__()

    form = UfficiostampaSettingsEditForm
