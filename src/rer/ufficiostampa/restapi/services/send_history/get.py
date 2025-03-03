from plone import api
from rer.ufficiostampa.interfaces import IRerUfficiostampaSettings
from rer.ufficiostampa.interfaces import ISendHistoryStore
from rer.ufficiostampa.restapi.services.common import DataClear
from rer.ufficiostampa.restapi.services.common import DataCSVGet
from rer.ufficiostampa.restapi.services.common import DataGet


class SendHistoryGet(DataGet):
    store = ISendHistoryStore

    def reply(self):
        data = super().reply()
        data["channels"] = api.portal.get_registry_record(
            "subscription_channels", interface=IRerUfficiostampaSettings
        )
        return data


class SendHistoryCSVGet(DataCSVGet):
    store = ISendHistoryStore
    type = "history"
    columns = [
        "status",
        "type",
        "date",
        "completed_date",
        "recipients",
        "channels",
        "title",
        "number",
    ]


class SendHistoryClearGet(DataClear):
    store = ISendHistoryStore
