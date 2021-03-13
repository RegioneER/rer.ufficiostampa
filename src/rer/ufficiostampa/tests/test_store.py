# -*- coding: utf-8 -*-
from rer.ufficiostampa.testing import RER_UFFICIOSTAMPA_FUNCTIONAL_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import RelativeSession
from zope.component import getUtility
from rer.ufficiostampa.interfaces import ISubscriptionsStore

import transaction
import unittest


class TestTool(unittest.TestCase):

    layer = RER_UFFICIOSTAMPA_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        # self.tool = getUtility(ISubscriptionsStore)
        # self.id = self.tool.add(
        #     {
        #         "channels": ["foo"],
        #         "email": "foo@foo.it",
        #         "name": "John",
        #         "surname": "Doe",
        #         "phone": "123456",
        #     },
        # )
        # transaction.commit()

    def test_search(self):
        tool = getUtility(ISubscriptionsStore)
        tool.add(
            {
                "channels": ["foo"],
                "email": "foo@foo.it",
                "name": "John",
                "surname": "xxx",
                "phone": "123456",
            },
        )
        tool.add(
            {
                "channels": ["foo", "bar"],
                "email": "bar@bar.it",
                "name": "Jack",
                "surname": "yyy",
                "phone": "123456",
            },
        )
        tool.add(
            {
                "channels": ["baz"],
                "email": "baz@baz.it",
                "name": "Jim",
                "surname": "zzz",
                "phone": "123456",
            },
        )
        transaction.commit()

        self.assertEqual(len(tool.search()), 3)

        #  search by text (index name, surname and email)
        self.assertEqual(len(tool.search(query={"text": "John"})), 1)
        self.assertEqual(len(tool.search(query={"text": "baz"})), 1)
        self.assertEqual(len(tool.search(query={"text": "xxx"})), 1)

        # search by channel
        self.assertEqual(len(tool.search(query={"channels": "foo"})), 2)
        self.assertEqual(len(tool.search(query={"channels": "baz"})), 1)
        self.assertEqual(
            len(tool.search(query={"channels": ["foo", "bar"]})), 2
        )

        # combined search
        self.assertEqual(
            len(tool.search(query={"channels": "foo", "text": "Jack"})), 1
        )
