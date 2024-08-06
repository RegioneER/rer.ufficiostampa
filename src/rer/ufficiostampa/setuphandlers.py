from plone.dexterity.interfaces import IDexterityFTI
from Products.CMFPlone.interfaces import INonInstallable
from Products.CMFPlone.utils import get_installer
from zope.component import getUtility
from zope.interface import implementer


def set_behavior(fti_id, name, value):
    """Set a behavior on a FTI
    if value is True, add the behavior, otherwise remove it
    """
    # add or remove the behavior based on the value from the form
    fti = getUtility(IDexterityFTI, name=fti_id)
    behaviors = list(fti.behaviors)
    if value and name not in behaviors:
        behaviors.append(name)
    elif not value and name in behaviors:
        behaviors.remove(name)
    fti.behaviors = tuple(behaviors)


@implementer(INonInstallable)
class HiddenProfiles:
    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller."""
        return [
            "rer.ufficiostampa:uninstall",
        ]


def post_install(context):
    """Post install script"""
    # Do something during the installation of this package
    installer = get_installer(context)
    if installer.is_product_installed("design.plone.contenttypes"):
        set_behavior(
            "ComunicatoStampa",
            "design.plone.contenttypes.behavior.argomenti_news",
            True,
        )
        set_behavior(
            "ComunicatoStampa", "design.plone.contenttypes.behavior.news_base", True
        )
        set_behavior("ComunicatoStampa", "plone.basic", True)
        set_behavior("ComunicatoStampa", "rer.ufficiostampa.basic", False)
        set_behavior("ComunicatoStampa", "rer.ufficiostampa.legislature", False)


def uninstall(context):
    """Uninstall script"""
