from datetime import datetime
from plone import api
from repoze.catalog.query import And
from repoze.catalog.query import Any
from repoze.catalog.query import Contains
from repoze.catalog.query import Eq
from rer.ufficiostampa import _
from rer.ufficiostampa.interfaces import ISendHistoryStore
from rer.ufficiostampa.interfaces import ISubscriptionsStore
from souper.soup import get_soup
from souper.soup import Record
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.interface import implementer

import logging


logger = logging.getLogger(__name__)


class BaseStore:
    """ """

    @property
    def soup(self):

        return get_soup(self.soup_name, api.portal.get())

    def add(self, data):
        record = Record()
        for k, v in data.items():
            if k not in self.fields:
                logger.warning(f"[ADD {self.soup_type}] SKIP unkwnown field: {k}")
            else:
                record.attrs[k] = v
        record.attrs["date"] = datetime.now()
        return self.soup.add(record)

    def length(self):
        return len([x for x in self.soup.data.values()])

    def search(self, query=None, sort_index="date", reverse=True):
        parsed_query = self.parse_query_params(query=query)
        if parsed_query:
            return [
                x
                for x in self.soup.query(
                    queryobject=parsed_query,
                    sort_index=sort_index,
                    reverse=reverse,
                )
            ]
        # return all data
        records = self.soup.data.values()
        if sort_index == "date":
            return sorted(
                records,
                key=lambda k: k.attrs[sort_index] or None,
                reverse=reverse,
            )
        return sorted(
            records,
            key=lambda k: k.attrs.get(sort_index, "") or "",
            reverse=reverse,
        )

    def parse_query_params(self, query):
        if not query:
            return []
        queries = []
        for index, value in query.items():
            if not value or value in ["*", "**"]:
                continue
            if index not in self.indexes:
                continue
            if index == self.text_index:
                queries.append(Contains("text", value))
            elif index in self.keyword_indexes:
                queries.append(Any(index, value))
            else:
                queries.append(Eq(index, value))
        if not queries:
            return None
        return And(*queries)

    def get_record(self, id):
        if isinstance(id, str) or isinstance(id, str):
            try:
                id = int(id)
            except ValueError as e:
                logger.exception(e)
                return None
        try:
            return self.soup.get(id)
        except KeyError as e:
            logger.exception(e)
            return None

    def update(self, id, data):
        try:
            record = self.soup.get(id)
        except KeyError:
            logger.error(f'[UPDATE {self.soup_type}] item with id "{id}" not found.')
            return {"error": "NotFound"}
        for k, v in data.items():
            if k not in self.fields:
                logger.warning(f"[UPDATE {self.soup_type}] SKIP unkwnown field: {k}")

            else:
                record.attrs[k] = v
        self.soup.reindex(records=[record])

    def delete(self, id):
        try:
            del self.soup[self.soup.get(id)]
        except KeyError:
            logger.error(
                '[DELETE %s] Subscription with id "%s" not found.',
                self.soup_type,
                id,
            )
            return {"error": "NotFound"}

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

    def add(self, data):
        old_record = self.search(query={"email": data.get("email", "")})
        if old_record:
            msg = translate(
                _(
                    "address_already_registered",
                    default="E-mail address already registered.",
                ),
                context=getRequest(),
            )
            raise ValueError(msg)
        return super().add(data=data)


@implementer(ISendHistoryStore)
class SendHistoryStore(BaseStore):
    soup_name = "send_history_soup"
    soup_type = "HISTORY"
    fields = [
        "number",
        "title",
        "type",
        "recipients",
        "channels",
        "status",
        "status_message",
        "completed_date",
        "url",
    ]
    indexes = ["title", "channels", "date", "type"]
    keyword_indexes = []
    text_index = "title"
