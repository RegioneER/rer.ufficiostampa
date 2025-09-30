from plone import api
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import RelativeSession
from rer.ufficiostampa.interfaces import ISubscriptionsStore
from rer.ufficiostampa.testing import (  # noqa: E501,
    RER_UFFICIOSTAMPA_API_FUNCTIONAL_TESTING,
)
from zope.component import getUtility
from rer.ufficiostampa.interfaces import IRerUfficiostampaSettings

import transaction
import unittest


class TestCleanupDeletedChannels(unittest.TestCase):
    layer = RER_UFFICIOSTAMPA_API_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        api.portal.set_registry_record(
            "subscription_channels",
            ["foo", "bar"],
            interface=IRerUfficiostampaSettings,
        )

        self.tool = getUtility(ISubscriptionsStore)

        self.id = self.tool.add(
            {
                "channels": ["foo", "bar"],
                "email": "foo@foo.it",
                "name": "John",
                "surname": "Doe",
                "phone": "123456",
            },
        )
        transaction.commit()

    def test_when_remove_a_channel_from_list_cleanup_subscriptions(self):

        record = self.tool.search(query={"text": "John"})[0]

        self.assertEqual(record.attrs["channels"], ["foo", "bar"])

        # now remove one channel
        api.portal.set_registry_record(
            "subscription_channels",
            ["foo"],
            interface=IRerUfficiostampaSettings,
        )
        transaction.commit()

        record = self.tool.search(query={"text": "John"})[0]
        self.assertEqual(record.attrs["channels"], ["foo"])
