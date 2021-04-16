# -*- coding: utf-8 -*-
from copy import deepcopy
from datetime import datetime
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.batching import HypermediaBatch
from plone.restapi.deserializer import json_body
from plone.restapi.search.utils import unflatten_dotted_dict
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service
from six import StringIO
from zExceptions import BadRequest
from zope.component import getUtility
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse

import csv
import six


class DataGet(Service):
    def reply(self):
        tool = getUtility(self.store)
        query = self.parse_query()
        batch = HypermediaBatch(self.request, tool.search(**query))
        data = {
            "@id": batch.canonical_url,
            "items": [self.expand_data(x) for x in batch],
            "items_total": batch.items_total,
        }
        links = batch.links
        if links:
            data["batching"] = links
        return data

    def expand_data(self, record):
        data = {k: json_compatible(v) for k, v in record.attrs.items()}
        data["id"] = record.intid
        return data

    def parse_query(self):
        query = deepcopy(self.request.form)
        query = unflatten_dotted_dict(query)
        res = {}
        if "sort_on" in query:
            res["sort_index"] = query["sort_on"]
            del query["sort_on"]
        if "sort_order" in query:
            order = query["sort_order"]
            reverse = True
            if order in ["asc", "ascending"]:
                reverse = False
            res["reverse"] = reverse
            del query["sort_order"]
        res["query"] = query
        return res


class DataCSVGet(DataGet):
    def render(self):
        now = datetime.now()
        self.request.response.setHeader(
            "Content-Disposition",
            'attachment; filename="{type}_{date}.csv"'.format(
                type=self.type, date=now.strftime("%d%m%Y-%H%M%S")
            ),
        )
        self.request.response.setHeader(
            "Content-Type", "text/comma-separated-values"
        )

        data = self.get_data()
        if isinstance(data, six.text_type):
            data = data.encode("utf-8")
        self.request.response.write(data)

    def get_data(self):
        tool = getUtility(self.store)
        query = self.parse_query()
        sbuf = StringIO()
        fixed_columns = ["date"]
        columns = []
        rows = []

        for item in tool.search(**query):
            data = {}
            for k, v in item.attrs.items():
                if k not in columns and k not in fixed_columns:
                    columns.append(k)
                if isinstance(v, list):
                    v = ", ".join(v)
                data[k] = json_compatible(v)
            rows.append(data)
        columns.extend(fixed_columns)
        writer = csv.DictWriter(sbuf, fieldnames=columns, delimiter=",")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
        res = sbuf.getvalue()
        sbuf.close()
        return res


class DataAdd(Service):
    def reply(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        form_data = json_body(self.request)
        self.validate_form(form_data=form_data)

        tool = getUtility(self.store)
        res = tool.add(form_data)

        if res:
            return self.reply_no_content()

        self.request.response.setStatus(500)
        return dict(
            error=dict(
                type="InternalServerError",
                message="Unable to add. Contact site manager.",
            )
        )

    def validate_form(self, form_data):
        pass


@implementer(IPublishTraverse)
class TraversableService(Service):
    """ Update an entry """

    def __init__(self, context, request):
        super(TraversableService, self).__init__(context, request)
        self.id = ""
        self.errors = {}

    def publishTraverse(self, request, id):
        # Consume any path segments after /@addons as parameters
        try:
            self.id = int(id)
        except ValueError:
            raise BadRequest("Id should be a number.")
        return self

    def reply(self):
        raise NotImplementedError


class DataUpdate(TraversableService):
    """ Update an entry """

    def reply(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        if not self.id:
            raise BadRequest("Missing id")

        form_data = json_body(self.request)

        tool = getUtility(self.store)
        res = tool.update(id=self.id, data=form_data)
        if not res:
            return self.reply_no_content()
        if res.get("error", "") == "NotFound":
            raise BadRequest(
                'Unable to find item with id "{}"'.format(self.id)
            )
        self.request.response.setStatus(500)
        return dict(
            error=dict(
                type="InternalServerError",
                message="Unable to update item. Contact site manager.",
            )
        )


class DataDelete(TraversableService):
    def reply(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        if not self.id:
            raise BadRequest("Missing id")
        tool = getUtility(self.store)
        res = tool.delete(id=self.id)
        if not res:
            return self.reply_no_content()
        if res.get("error", "") == "NotFound":
            raise BadRequest(
                'Unable to find item with id "{}"'.format(self.id)
            )
        self.request.response.setStatus(500)
        return dict(
            error=dict(
                type="InternalServerError",
                message="Unable to delete item. Contact site manager.",
            )
        )


class DataClear(Service):
    def reply(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        tool = getUtility(self.store)
        tool.clear()
        return self.reply_no_content()