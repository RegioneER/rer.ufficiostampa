from datetime import datetime
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.testing import RelativeSession
from rer.ufficiostampa.interfaces import IRerUfficiostampaSettings
from rer.ufficiostampa.testing import (  # noqa: E501,
    RER_UFFICIOSTAMPA_API_FUNCTIONAL_TESTING,
)
from souper.soup import get_soup
from souper.soup import Record

import transaction
import unittest


class TestSubscriptionsGet(unittest.TestCase):

    layer = RER_UFFICIOSTAMPA_API_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        api.user.create(
            email="memberuser@example.com",
            username="memberuser",
            password="secret123",
        )

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)
        self.anon_api_session = RelativeSession(self.portal_url)
        self.anon_api_session.headers.update({"Accept": "application/json"})

        transaction.commit()

    def tearDown(self):
        self.api_session.close()
        self.anon_api_session.close()

        api.portal.set_registry_record(
            "subscription_channels", [], interface=IRerUfficiostampaSettings
        )
        transaction.commit()

    def test_anon_cant_get_data(self):
        url = f"{self.portal_url}/@subscriptions"
        self.assertEqual(self.anon_api_session.get(url).status_code, 401)

    def test_admin_get_data(self):
        url = f"{self.portal_url}/@subscriptions"
        self.assertEqual(self.api_session.get(url).status_code, 200)

    def test_gestore_comunicati_can_get_data(self):
        api_session = RelativeSession(self.portal_url)
        api_session.headers.update({"Accept": "application/json"})
        api_session.auth = ("memberuser", "secret123")

        url = f"{self.portal_url}/@subscriptions"
        self.assertEqual(api_session.get(url).status_code, 401)

        setRoles(self.portal, "memberuser", ["Gestore Comunicati"])
        transaction.commit()
        self.assertEqual(api_session.get(url).status_code, 200)

        api_session.close()

    def test_endpoint_returns_also_subscription_channels(self):
        url = f"{self.portal_url}/@subscriptions"
        response = self.api_session.get(url)
        res = response.json()
        self.assertEqual(res["channels"], [])

        api.portal.set_registry_record(
            "subscription_channels",
            ["foo", "bar"],
            interface=IRerUfficiostampaSettings,
        )
        transaction.commit()

        response = self.api_session.get(url)
        res = response.json()
        self.assertEqual(res["channels"], ["foo", "bar"])

    def test_endpoint_returns_data(self):
        url = f"{self.portal_url}/@subscriptions"
        response = self.api_session.get(url)
        res = response.json()
        self.assertEqual(res["items_total"], 0)

        now = datetime.now()
        soup = get_soup("subscriptions_soup", self.portal)
        transaction.commit()
        record = Record()
        record.attrs["name"] = "John"
        record.attrs["email"] = "jdoe@foo.com"
        record.attrs["date"] = now
        intid = soup.add(record)
        transaction.commit()

        url = f"{self.portal_url}/@subscriptions"
        response = self.api_session.get(url)
        res = response.json()

        self.assertEqual(res["items_total"], 1)
        self.assertEqual(
            res["items"],
            [
                {
                    "id": intid,
                    "email": "jdoe@foo.com",
                    "name": "John",
                    "date": json_compatible(now),
                }
            ],
        )
