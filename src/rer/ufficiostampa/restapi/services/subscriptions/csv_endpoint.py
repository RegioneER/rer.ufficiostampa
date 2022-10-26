# -*- coding: utf-8 -*-
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from plone.schema.email import Email, InvalidEmail
from plone import api
from rer.ufficiostampa import _
from rer.ufficiostampa.interfaces import ISubscriptionsStore
from rer.ufficiostampa.restapi.services.common import DataCSVGet
from six import StringIO
from zExceptions import BadRequest
from zope.component import getUtility
from zope.interface import alsoProvides
from zope.i18n import translate

from rer.ufficiostampa.interfaces.settings import IRerUfficiostampaSettings

import base64
import csv
import logging
import six
import itertools

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

        # clone generator for validation checks and processing
        csv_gen, csv_gen_checks = itertools.tee(csv_data.get("csv", []))

        res = {
            "errored": [],
            "skipped": [],
            "imported": 0,
        }

        # check for data errors
        for i, row in enumerate(csv_gen_checks):
            try:
                Email().validate(row.get("email", ""))
            except InvalidEmail:
                msg = translate(
                    _(
                        "invalid_email",
                        default="[${row}] - row with invalid email",
                        mapping={"row": i},
                    ),
                    context=self.request,
                )
                logger.warning("[ERROR] - {}".format(msg))
                res["errored"].append(msg)

            request_channels = set(
                map(lambda r: r.strip(), row.get("channels").split(","))
            )
            channels_filtered = [
                ch
                for ch in request_channels
                if ch
                in api.portal.get_registry_record(
                    interface=IRerUfficiostampaSettings, name="subscription_channels"
                )
            ]

            if len(request_channels) != len(channels_filtered):
                msg = translate(
                    _(
                        "invalid_channels",
                        default="[${row}] - row with invalid channels",
                        mapping={"row": i},
                    ),
                    context=self.request,
                )
                logger.warning("[ERROR] - {}".format(msg))
                res["errored"].append(msg)

        # return if we have errored fields
        if len(res["errored"]):
            return res

        for i, row in enumerate(csv_gen):
            email = row.get("email", "")
            row["channels"] = row["channels"].split(",")
            records = tool.search(query={"email": email})
            if not records:
                # add it
                record_id = tool.add(data=row)
                if not record_id:
                    msg = translate(
                        _(
                            "skip_unable_to_add",
                            default="[${row}] - unable to add",
                            mapping={"row": i},
                        ),
                        context=self.request,
                    )
                    logger.warning("[SKIP] - {}".format(msg))
                    res["skipped"].append(msg)
                    continue
                res["imported"] += 1
            else:
                if len(records) != 1:
                    msg = translate(
                        _(
                            "skip_duplicate_multiple",
                            default='[${row}] - Multiple values for "${email}"',  # noqa
                            mapping={"row": i, "email": email},
                        ),
                        context=self.request,
                    )
                    logger.warning("[SKIP] - {}".format(msg))
                    res["skipped"].append(msg)
                    continue
                record = records[0]
                if not overwrite:
                    msg = translate(
                        _(
                            "skip_duplicate",
                            default='[${row}] - "${email}" already in database',  # noqa
                            mapping={"row": i, "email": email},
                        ),
                        context=self.request,
                    )
                    if six.PY2:
                        msg = msg.encode("utf-8")
                    logger.warning("[SKIP] - {}".format(msg))
                    res["skipped"].append(msg)
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
                    default="You need to pass a csv file.",
                )
            )
        csv_data = data["data"]
        if data.get("encoding", "") == "base64":
            csv_data = base64.b64decode(csv_data)
            try:
                csv_data = csv_data.decode()
            except UnicodeDecodeError:
                pass
            csv_value = StringIO(csv_data)
        else:
            csv_value = csv_data

        try:
            dialect = csv.Sniffer().sniff(csv_data, delimiters=";,")

            if six.PY2:
                dialect.delimiter = dialect.delimiter.encode()
                dialect.quotechar = dialect.quotechar.encode()

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
            return {"error": _("error_reading_csv", default="Error reading csv file.")}

    def parse_query(self):
        data = json_body(self.request)
        if "file" not in data:
            raise BadRequest(
                _("missing_file", default="You need to pass a file at least.")
            )
        return data
