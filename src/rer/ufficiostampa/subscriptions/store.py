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

    def search(self, query=None):
        if not query:
            records = self.soup.data.values()

        return records

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


#     def delete(self, id):
#         record = self.soup.get(id)
#         del self.soup[record]

#     def clear(self):
#         self.soup.clear()
