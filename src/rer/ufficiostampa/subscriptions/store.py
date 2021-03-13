# -*- coding: utf-8 -*-
from datetime import datetime
from plone import api
from rer.ufficiostampa.interfaces import ISubscriptionsStore
from souper.soup import get_soup
from souper.soup import Record
from zope.interface import implementer

import logging
import six

logger = logging.getLogger(__name__)

SUBSCRIPTION_FIELDS = ["name", "surname", "email", "phone", "channels"]


@implementer(ISubscriptionsStore)
class SubscriptionsStore(object):
    """
    """

    @property
    def soup(self):

        return get_soup("subscriptions_soup", api.portal.get())

    def add(self, data):

        record = Record()
        for k, v in data.items():
            if k not in SUBSCRIPTION_FIELDS:
                logger.warning(
                    "[ADD SUBSCRIPTION] SKIP unkwnown field: {}".format(k)
                )
            else:
                record.attrs[k] = v
        record.attrs["date"] = datetime.now()
        return self.soup.add(record)

    def length(self):
        return len([x for x in self.soup.data.values()])

    def search(self, query=None, sort_index="date", reverse=False):
        if query:
            queries = [
                self.parse_query_params(index, value)
                for index, value in query.items()
                if index in ["text", "channels"]
            ]
            if queries:
                return [
                    x
                    for x in self.soup.query(
                        " and ".join(queries),
                        sort_index=sort_index,
                        reverse=reverse,
                    )
                ]
        records = self.soup.data.values()
        return sorted(
            records, key=lambda k: k.attrs[sort_index], reverse=reverse
        )

    def parse_query_params(self, index, value):
        if index == "text":
            return "'{}' in text".format(value)
        elif index == "channels":
            if isinstance(value, list):
                return "channels in any({})".format(value)
            elif isinstance(value, six.text_type):
                return "channels in any('{}')".format(value)

    def get_record(self, id):
        if isinstance(id, six.text_type):
            id = int(id)
        return self.soup.get(id)

    def update(self, id, data):
        try:
            record = self.soup.get(id)
        except KeyError:
            logger.error(
                '[UPDATE SUBSCRIPTION] Subscription with id "{}" not found.'.format(  # noqa
                    id
                )
            )
            return {"error": "NotFound"}
        for k, v in data.items():
            if k not in SUBSCRIPTION_FIELDS:
                logger.warning(
                    "[UPDATE SUBSCRIPTION] SKIP unkwnown field: {}".format(k)
                )

            else:
                record.attrs[k] = v
        self.soup.reindex(record)

    def delete(self, id):
        try:
            record = self.soup.get(id)
        except KeyError:
            logger.error(
                '[DELETE SUBSCRIPTION] Subscription with id "{}" not found.'.format(  # noqa
                    id
                )
            )
            return {"error": "NotFound"}
        del self.soup[record]

    def clear(self):
        self.soup.clear()
