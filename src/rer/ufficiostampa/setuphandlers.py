from plone.dexterity.interfaces import IDexterityFTI
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces import INonInstallable
from Products.CMFPlone.interfaces import ISearchSchema
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
    installer = get_installer(context)
    if installer.is_product_installed("design.plone.contenttypes"):
        set_behavior(
            "ComunicatoStampa",
            "design.plone.contenttypes.behavior.exclude_from_search",
            True,
        )
        set_behavior(
            "InvitoStampa",
            "design.plone.contenttypes.behavior.exclude_from_search",
            True,
        )
        set_behavior(
            "CartellaStampa",
            "design.plone.contenttypes.behavior.exclude_from_search",
            True,
        )

        disable_searchable_types()


def disable_searchable_types(context=None):
    # remove some types from search enabled ones

    registry = getUtility(IRegistry)
    settings = registry.forInterface(ISearchSchema, prefix="plone")
    remove_types = ["CartellaStampa"]
    types = set(settings.types_not_searched)
    types.update(remove_types)
    settings.types_not_searched = tuple(types)


def uninstall(context):
    """Uninstall script"""
