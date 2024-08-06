from copy import deepcopy
from datetime import datetime
from defusedcsv import csv
from io import StringIO
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.batching import HypermediaBatch
from plone.restapi.deserializer import json_body
from plone.restapi.search.utils import unflatten_dotted_dict
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service
from zExceptions import BadRequest
from zope.component import getUtility
from zope.index.text.parsetree import ParseError
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse

import logging


logger = logging.getLogger(__name__)


class DataGet(Service):
    def reply(self):
        tool = getUtility(self.store)
        query = self.parse_query()
        try:
            results = tool.search(**query)
        except ParseError as e:
            self.request.response.setStatus(500)
            return dict(error=dict(type="Error", message=e.message))
        batch = HypermediaBatch(self.request, results)
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
        data = self.get_data()
        if isinstance(data, dict):
            if data.get("error", False):
                self.request.response.setStatus(500)
                return dict(
                    error=dict(
                        type="InternalServerError",
                        message="Unable export. Contact site manager.",
                    )
                )
        self.request.response.setHeader("Content-Type", "text/csv")
        now = datetime.now()
        self.request.response.setHeader(
            "Content-Disposition",
            'attachment; filename="{type}_{date}.csv"'.format(
                type=self.type, date=now.strftime("%d%m%Y-%H%M%S")
            ),
        )
        return data
        # self.request.response.write(data)

    def get_data(self):
        """get data for csv export"""
        tool = getUtility(self.store)
        query = self.parse_query()
        sbuf = StringIO()
        rows = []
        for item in tool.search(**query):
            data = {}
            for k, v in item.attrs.items():
                if k not in self.columns:
                    continue
                if isinstance(v, list):
                    v = ", ".join(v)
                elif isinstance(v, int):
                    v = str(v)
                elif isinstance(v, datetime):
                    v = v.strftime("%Y-%m-%d %H:%M:%S")
                # if v:
                #     v = json_compatible(v)
                #     v = v.encode("utf-8")
                data[k] = v
            rows.append(data)
        writer = csv.DictWriter(sbuf, fieldnames=self.columns, delimiter=",")
        writer.writeheader()
        for row in rows:
            try:
                writer.writerow(row)
            except Exception as e:
                logger.exception(e)
                return {"error": True}
        res = sbuf.getvalue()
        sbuf.close()
        return res


class DataAdd(Service):
    def reply(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        form_data = json_body(self.request)
        self.validate_form(form_data=form_data)

        tool = getUtility(self.store)
        try:
            res = tool.add(form_data)
        except ValueError as e:
            self.request.response.setStatus(500)
            return dict(
                error=dict(
                    type="InternalServerError",
                    message=getattr(e, "message", e.__str__()),
                )
            )

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
    """Update an entry"""

    def __init__(self, context, request):
        super().__init__(context, request)
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
    """Update an entry"""

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
            raise BadRequest(f'Unable to find item with id "{self.id}"')
        self.request.response.setStatus(500)
        return dict(
            error=dict(
                type="InternalServerError",
                message="Unable to update item. Contact site manager.",
            )
        )


class DataDelete(TraversableService):
    def reply(self):
        form_data = json_body(self.request)
        if not self.id and not form_data.get("id"):
            raise BadRequest("Missing id")
        alsoProvides(self.request, IDisableCSRFProtection)
        tool = getUtility(self.store)
        if self.id:
            res = tool.delete(id=self.id)
            if res:
                raise BadRequest(f'Unable to delete item with id "{self.id}"')
        for id in form_data.get("id", []):
            res = tool.delete(id=id)
            if res:
                raise BadRequest(f'Unable to delete item with id "{id}"')
        return self.reply_no_content()


class DataClear(Service):
    def reply(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        tool = getUtility(self.store)
        tool.clear()
        return self.reply_no_content()
