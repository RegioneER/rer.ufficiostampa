# -*- coding: utf-8 -*-
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from rer.ufficiostampa import _
from rer.ufficiostampa.interfaces import ISubscriptionsStore
from rer.ufficiostampa.restapi.services.common import DataCSVGet
from six import StringIO
from zExceptions import BadRequest
from zope.component import getUtility
from zope.interface import alsoProvides

import base64
import csv
import logging

logger = logging.getLogger(__name__)

COLUMNS = [
    "name",
    "surname",
    "email",
    "phone",
    "channels",
    "newspaper",
    "date",
]


class SubscriptionsCSVGet(DataCSVGet):
    type = "subscriptions"
    store = ISubscriptionsStore
    columns = COLUMNS


class SubscriptionsCSVPost(Service):
    def reply(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        query = self.parse_query()
        tool = getUtility(ISubscriptionsStore)

        clear = query.get("clear", False)
        overwrite = query.get("overwrite", False)
        if clear:
            tool.clear()
        csv_data = self.get_csv_data(data=query["file"])
        if csv_data.get("error", "") or not csv_data.get("csv", None):
            self.request.response.setStatus(500)
            return dict(
                error=dict(
                    type="InternalServerError",
                    message=csv_data.get("error", ""),
                )
            )
        res = {
            "skipped": [],
            "imported": 0,
        }

        i = 0
        for row in csv_data.get("csv", []):
            i += 1
            email = row.get("email", "")
            row["channels"] = row["channels"].split(",")
            if not email:
                logger.warning("[SKIP] - row without email: {}".format(row))
                res["skipped"].append(i - 1)
                continue
            records = tool.search(query={"email": email})
            if not records:
                # add it
                record_id = tool.add(data=row)
                if not record_id:
                    logger.warning("[SKIP] - Unable to add: {}".format(row))
                    res["skipped"].append(i - 1)
                    continue
                res["imported"] += 1
            else:
                if len(records) != 1:
                    logger.warning(
                        '[SKIP] - Multiple values for "{}" into database'.format(  # noqa
                            email
                        )
                    )
                    res["skipped"].append(i - 1)
                    continue
                record = records[0]
                if not overwrite:
                    logger.warning(
                        '[SKIP] - Do not update data for "{}" (overwrite not set)'.format(  # noqa
                            email
                        )
                    )
                    res["skipped"].append(i - 1)
                    continue
                else:
                    tool.update(id=record.intid, data=row)
                    res["imported"] += 1

        return res

    def get_csv_data(self, data):
        if data.get("content-type", "") != "text/comma-separated-values":
            raise BadRequest(
                _(
                    "wrong_content_type",
                    default=u"You need to pass a csv file.",
                )
            )
        csv_data = data["data"]
        if data.get("encoding", "") == "base64":
            csv_data = base64.b64decode(csv_data).decode()
            csv_value = StringIO(csv_data)
        else:
            csv_value = csv_data

        try:
            dialect = csv.Sniffer().sniff(csv_data, delimiters=";,")
            return {
                "csv": csv.DictReader(
                    csv_value,
                    lineterminator=dialect.lineterminator,
                    quoting=dialect.quoting,
                    doublequote=dialect.doublequote,
                    delimiter=dialect.delimiter,
                    quotechar=dialect.quotechar,
                )
            }
        except Exception as e:
            logger.exception(e)
            return {
                "error": _(
                    "error_reading_csv", default=u"Error reading csv file."
                )
            }

    def parse_query(self):
        data = json_body(self.request)
        if "file" not in data:
            raise BadRequest(
                _("missing_file", default=u"You need to pass a file at least.")
            )
        return data
