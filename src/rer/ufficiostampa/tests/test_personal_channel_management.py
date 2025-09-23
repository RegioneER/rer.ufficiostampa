from itsdangerous.url_safe import URLSafeTimedSerializer
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.registry.interfaces import IRegistry
from plone.restapi.testing import RelativeSession
from rer.ufficiostampa.interfaces import ISubscriptionsStore
from rer.ufficiostampa.interfaces.settings import IRerUfficiostampaSettings
from rer.ufficiostampa.testing import RER_UFFICIOSTAMPA_API_FUNCTIONAL_TESTING
from unittest.mock import patch
from zope.component import getUtility

import transaction
import unittest


class TestPersonalChannelsManagement(unittest.TestCase):
    layer = RER_UFFICIOSTAMPA_API_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        # set salt and secret
        api.portal.set_registry_record(
            "token_salt",
            "qwertyuiop",
            interface=IRerUfficiostampaSettings,
        )
        api.portal.set_registry_record(
            "token_secret",
            "asdfghjkl",
            interface=IRerUfficiostampaSettings,
        )

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        self.tool = getUtility(ISubscriptionsStore)
        self.id_1 = self.tool.add(
            {
                "channels": ["foo", "bar"],
                "email": "foo@foo.it",
                "name": "John",
                "surname": "Doe",
                "phone": "123456",
            },
        )
        self.id_2 = self.tool.add(
            {
                "channels": ["bar"],
                "email": "bar@bar.it",
                "name": "John",
                "surname": "Smith",
                "phone": "98765",
            },
        )

        self.patcher = patch("Products.MailHost.MailHost.MailHost.send")
        self.fake_send = self.patcher.start()
        self.fake_send.return_value = None

        registry = getUtility(IRegistry)
        registry["plone.email_from_address"] = "info@plone.org"
        registry["plone.email_from_name"] = "Plone test site"
        api.portal.set_registry_record(
            "email_from_name", "Plone test site", interface=IRerUfficiostampaSettings
        )
        api.portal.set_registry_record(
            "email_from_address", "info@plone.org", interface=IRerUfficiostampaSettings
        )

        transaction.commit()

    def tearDown(self):
        self.patcher.stop()
        self.api_session.close()

    def generate_secret(self, email):
        token_secret = api.portal.get_registry_record(
            "token_secret", interface=IRerUfficiostampaSettings
        )
        token_salt = api.portal.get_registry_record(
            "token_salt", interface=IRerUfficiostampaSettings
        )
        serializer = URLSafeTimedSerializer(token_secret, token_salt)

        subscription = self.get_record_from_email(email=email)

        return serializer.dumps(
            {
                "id": subscription.intid,
                "email": subscription.attrs.get("email", ""),
            }
        )

    def get_record_from_email(self, email):
        tool = getUtility(ISubscriptionsStore)
        records = tool.search(query={"email": email})
        if records:
            return records[0]
        return None

    def test_send_link_raise_badrequest_if_missing_email_field(self):
        """
        email is required.
        """
        self.assertEqual(
            self.api_session.post(
                f"{self.portal_url}/@personal-channels-management-send-link"
            ).status_code,
            400,
        )

    def test_send_link_raise_badrequest_if_wrong_email(self):
        """
        email is required and should be present in tool.
        """
        self.assertEqual(
            self.api_session.post(
                f"{self.portal_url}/@personal-channels-management-send-link",
                json={"email": "dfsdf@dfdf.it"},
            ).status_code,
            400,
        )

    def test_send_link_raise_badrequest_if_token_not_set(self):
        """ """
        api.portal.set_registry_record(
            "token_salt",
            "",
            interface=IRerUfficiostampaSettings,
        )
        transaction.commit()
        res = self.api_session.post(
            f"{self.portal_url}/@personal-channels-management-send-link",
            json={"email": "foo@foo.it"},
        )
        self.assertEqual(
            res.status_code,
            500,
        )
        self.assertEqual(
            res.json()["error"]["message"],
            "Serializer secret and salt not set in control panel. Unable to send the link.",
        )

    def test_send_link_success(self):
        """ """
        res = self.api_session.post(
            f"{self.portal_url}/@personal-channels-management-send-link",
            json={"email": "foo@foo.it"},
        )
        self.assertEqual(
            res.status_code,
            204,
        )

    def test_token_verify_raise_badrequest_if_wrong_token(self):
        """ """
        res = self.api_session.post(
            f"{self.portal_url}/@personal-channels-management-token-verify",
            json={"secret": "xxx"},
        )
        self.assertEqual(
            res.status_code,
            400,
        )

    def test_token_verify_return_list_of_channels(self):
        res = self.api_session.post(
            f"{self.portal_url}/@personal-channels-management-token-verify",
            json={"secret": self.generate_secret(email="foo@foo.it")},
        )
        self.assertEqual(res.json(), {"channels": ["foo", "bar"]})

    def test_update_raise_badrequest_if_missing_params(self):
        """ """
        res = self.api_session.post(
            f"{self.portal_url}/@personal-channels-management-update",
            json={},
        )
        self.assertEqual(
            res.status_code,
            400,
        )

        res = self.api_session.post(
            f"{self.portal_url}/@personal-channels-management-update",
            json={"secret": self.generate_secret(email="foo@foo.it")},
        )
        self.assertEqual(
            res.status_code,
            400,
        )

        res = self.api_session.post(
            f"{self.portal_url}/@personal-channels-management-update",
            json={"channels": ["foo", "bar"]},
        )
        self.assertEqual(
            res.status_code,
            400,
        )

    def test_update_raise_badrequest_if_wrong_token(self):
        """ """
        res = self.api_session.post(
            f"{self.portal_url}/@personal-channels-management-update",
            json={
                "secret": "xxx",
                "channels": ["foo"],
            },
        )
        self.assertEqual(
            res.status_code,
            400,
        )

    def test_update_remove_channels(self):
        """ """
        record = self.get_record_from_email(email="foo@foo.it")

        self.assertEqual(record.attrs.get("channels", []), ["foo", "bar"])

        self.api_session.post(
            f"{self.portal_url}/@personal-channels-management-update",
            json={
                "secret": self.generate_secret(email="foo@foo.it"),
                "channels": ["foo"],
            },
        )
        transaction.commit()
        record = self.get_record_from_email(email="foo@foo.it")
        self.assertEqual(record.attrs.get("channels", []), ["foo"])

    def test_update_remove_channels_delete_email_if_no_channels_remaining(self):
        """ """
        record = self.get_record_from_email(email="foo@foo.it")

        self.assertEqual(record.attrs.get("channels", []), ["foo", "bar"])

        self.api_session.post(
            f"{self.portal_url}/@personal-channels-management-update",
            json={
                "secret": self.generate_secret(email="foo@foo.it"),
                "channels": [],
            },
        )
        transaction.commit()
        record = self.get_record_from_email(email="foo@foo.it")
        self.assertIsNone(record)
