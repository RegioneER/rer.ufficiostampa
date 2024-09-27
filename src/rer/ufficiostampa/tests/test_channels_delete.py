import unittest

from plone import api
from zope.component import getUtility

from rer.ufficiostampa.interfaces import ISubscriptionsStore
from rer.ufficiostampa.interfaces import IRerUfficiostampaSettings

from rer.ufficiostampa.testing import (
    RER_UFFICIOSTAMPA_API_INTEGRATION_TESTING,
)


class TestChannelsDeletionHandler(unittest.TestCase):

    layer = RER_UFFICIOSTAMPA_API_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.tool = getUtility(ISubscriptionsStore)

        api.portal.set_registry_record(
            interface=IRerUfficiostampaSettings,
            name="subscription_channels",
            value=["test", "test1"],
        )

        self.sb_1ch = self.tool.add(
            {
                "channels": ["test"],
                "email": "foo@foo.it",
                "name": "John",
                "surname": "Doe",
                "phone": "123456",
            },
        )
        self.sb_2ch = self.tool.add(
            {
                "channels": ["test", "test1"],
                "email": "foo1@foo.it",
                "name": "John1",
                "surname": "Doe1",
                "phone": "1234561",
            },
        )

    def test_channels_removed(self):
        api.portal.set_registry_record(
            interface=IRerUfficiostampaSettings,
            name="subscription_channels",
            value=["test1"],
        )

        self.assertIsNone(self.tool.get_record(self.sb_1ch))
        self.assertIsNotNone(self.tool.get_record(self.sb_2ch))
        self.assertListEqual(
            ["test1"], self.tool.get_record(self.sb_2ch).attrs["channels"]
        )
