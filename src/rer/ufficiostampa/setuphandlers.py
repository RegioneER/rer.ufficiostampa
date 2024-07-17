from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implementer


@implementer(INonInstallable)
class HiddenProfiles:
    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller."""
        return [
            "rer.ufficiostampa:uninstall",
        ]


def post_install(context):
    """Post install script"""


def uninstall(context):
    """Uninstall script"""
