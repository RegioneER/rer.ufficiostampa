# -*- coding: utf-8 -*-
from datetime import datetime
from plone import api
from rer.ufficiostampa.interfaces import ISubscriptionsStore
from rer.ufficiostampa.interfaces import ISendHistoryStore
from souper.soup import get_soup
from souper.soup import Record
from zope.interface import implementer

import logging
import six

logger = logging.getLogger(__name__)


class BaseStore(object):
    """
    """

    @property
    def soup(self):

        return get_soup(self.soup_name, api.portal.get())

    def add(self, data):
        record = Record()
        for k, v in data.items():
            if k not in self.fields:
                logger.warning(
                    "[ADD {}] SKIP unkwnown field: {}".format(
                        self.soup_type, k
                    )
                )
            else:
                record.attrs[k] = v
        record.attrs["date"] = datetime.now()
        return self.soup.add(record)

    def length(self):
        return len([x for x in self.soup.data.values()])

    def search(self, query=None, sort_index="date", reverse=True):
        queries = []
        if query:
            queries = [
                self.parse_query_params(index, value)
                for index, value in query.items()
                if index in self.indexes and value
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
        # return all data
        records = self.soup.data.values()
        return sorted(
            records, key=lambda k: k.attrs[sort_index], reverse=reverse
        )

    def parse_query_params(self, index, value):
        if index == self.text_index:
            return "'{}' in {}".format(value, self.text_index)
        elif index in self.keyword_indexes:
            if isinstance(value, list):
                return "{} in any({})".format(index, value)
            elif isinstance(value, six.text_type):
                return "{} in any('{}')".format(index, value)
        else:
            return "{} == '{}'".format(index, value)

    def get_record(self, id):
        if isinstance(id, six.text_type):
            id = int(id)
        return self.soup.get(id)

    def update(self, id, data):
        try:
            record = self.soup.get(id)
        except KeyError:
            logger.error(
                '[UPDATE {}] item with id "{}" not found.'.format(
                    self.soup_type, id
                )
            )
            return {"error": "NotFound"}
        for k, v in data.items():
            if k not in self.fields:
                logger.warning(
                    "[UPDATE {}] SKIP unkwnown field: {}".format(
                        self.soup_type, k
                    )
                )

            else:
                record.attrs[k] = v
        self.soup.reindex(record)

    def delete(self, id):
        try:
            record = self.soup.get(id)
        except KeyError:
            logger.error(
                '[DELETE {}] Subscription with id "{}" not found.'.format(
                    self.soup_type, id
                )
            )
            return {"error": "NotFound"}
        del self.soup[record]

    def clear(self):
        self.soup.clear()


@implementer(ISubscriptionsStore)
class SubscriptionsStore(BaseStore):
    soup_name = "subscriptions_soup"
    soup_type = "SUBSCRIPTION"
    fields = [
        "name",
        "surname",
        "email",
        "phone",
        "channels",
        "newspaper",
    ]
    indexes = ["text", "channels", "email"]
    keyword_indexes = ["channels"]
    text_index = "text"


@implementer(ISendHistoryStore)
class SendHistoryStore(BaseStore):
    soup_name = "send_history_soup"
    soup_type = "HISTORY"
    fields = [
        "subject",
        "type",
        "recipients",
        "channels",
        "status",
        "completed_date",
    ]
    indexes = ["subject", "channels", "date", "type"]
    keyword_indexes = []
    text_index = "subject"
