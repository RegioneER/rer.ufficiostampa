from defusedcsv import csv
from io import StringIO
from plone import api
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from plone.schema.email import Email
from plone.schema.email import InvalidEmail
from rer.ufficiostampa import _
from rer.ufficiostampa.interfaces import ISubscriptionsStore
from rer.ufficiostampa.interfaces.settings import IRerUfficiostampaSettings
from rer.ufficiostampa.restapi.services.common import DataCSVGet
from zExceptions import BadRequest
from zope.component import getUtility
from zope.i18n import translate
from zope.interface import alsoProvides

import base64
import logging
import re


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
REQUIRED = ["email", "channels"]


# @implementer(IPublishTraverse)
class SubscriptionsCSVGet(DataCSVGet):
    type = "subscriptions"
    store = ISubscriptionsStore
    columns = COLUMNS

    # def __init__(self, context, request):
    #     super().__init__(context, request)
    #     self.id = ""
    #     self.errors = {}

    # def publishTraverse(self, request, name):
    #     # Consume any path segments after /@addons as parameters
    #     try:
    #         self.id = int(id)
    #     except ValueError:
    #         raise BadRequest("Id should be a number.")
    #     return self


# XXX: cambiata la gestione degli errori, da rivedere l'implementazione Rect su Plone Classic UI
class SubscriptionsCSVPost(Service):
    def reply(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        tool = getUtility(ISubscriptionsStore)
        query = self.parse_query()

        clear = query.get("clear", False)
        overwrite = query.get("overwrite", False)
        # has_header = query.get("has_header", False)
        # csv_separator = query.get("csv_separator", ",")
        subscription_channels = set(
            api.portal.get_registry_record(
                interface=IRerUfficiostampaSettings, name="subscription_channels"
            )
        )
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

        # TODO: manage has_header

        # clone generator for validation checks and processing
        rows = [row for row in csv_data["csv"]]

        if not rows:
            # TODO: warning empty csv
            raise BadRequest(_("empty_csv", default="Empty csv file."))

        res = {
            "errored": [],
            "skipped": [],
            "imported": 0,
        }

        # required fields: (e.g. email, channels)
        for required in REQUIRED:
            if required not in rows[0]:
                res["errored"].append(
                    translate(
                        _(
                            "missing_required",
                            default="Missing required field: ${field}",
                            mapping={"field": required},
                        ),
                        context=self.request,
                    )
                )
        if res["errored"]:
            raise BadRequest("; ".join(res["errored"]))

        # check for data errors
        for i, row in enumerate(rows):
            try:
                Email().validate(row.get("email", ""))
            except InvalidEmail:
                msg = translate(
                    _(
                        "invalid_email",
                        default="[${row}] - row with invalid email ${email}",
                        mapping={"row": i, "email": row.get("email", "")},
                    ),
                    context=self.request,
                )
                logger.warning(f"[ERROR] - {msg}")
                res["errored"].append(msg)

            request_channels = {
                r.strip() for r in (row.get("channels") or "").split(",")
            }
            if not request_channels:
                msg = translate(
                    _(
                        "missing_channels",
                        default="[${row}] - row with missing channels",
                        mapping={"row": i},
                    ),
                    context=self.request,
                )
                logger.warning(f"[ERROR] - {msg}")
                res["errored"].append(msg)
                continue

            channels_invalid = request_channels.difference(subscription_channels)

            if channels_invalid:
                msg = translate(
                    _(
                        "invalid_channels",
                        default="[${row}] - row with invalid channels: ${channels}",
                        mapping={"row": i, "channels": ", ".join(channels_invalid)},
                    ),
                    context=self.request,
                )
                logger.warning(f"[ERROR] - {msg}")
                res["errored"].append(msg)

        # return if we have errored fields
        if len(res["errored"]):
            raise BadRequest("; ".join(res["errored"]))

        for i, row in enumerate(rows):
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
                    logger.warning(f"[SKIP] - {msg}")
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
                    logger.warning(f"[SKIP] - {msg}")
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
                    logger.warning(f"[SKIP] - {msg}")
                    res["skipped"].append(msg)
                    continue
                else:
                    tool.update(id=record.intid, data=row)
                    res["imported"] += 1

        return res

    def get_csv_data(self, data):
        if data.get("content-type", "") not in (
            "text/comma-separated-values",
            "text/csv",
        ):
            raise BadRequest(
                _(
                    "wrong_content_type",
                    default="You need to pass a csv file.",
                )
            )
        csv_data = data["data"]
        if data.get("encoding", "") == "base64":
            csv_data = re.sub(r"^data:.*;base64,", "", csv_data)
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
