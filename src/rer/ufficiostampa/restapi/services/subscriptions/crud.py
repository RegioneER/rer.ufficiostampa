from plone import api
from rer.ufficiostampa.interfaces import IRerUfficiostampaSettings
from rer.ufficiostampa.interfaces import ISubscriptionsStore
from rer.ufficiostampa.restapi.services.common import DataAdd
from rer.ufficiostampa.restapi.services.common import DataClear
from rer.ufficiostampa.restapi.services.common import DataDelete
from rer.ufficiostampa.restapi.services.common import DataGet
from rer.ufficiostampa.restapi.services.common import DataUpdate
from zExceptions import BadRequest


class SubscriptionsGet(DataGet):

    store = ISubscriptionsStore

    def reply(self):
        data = super().reply()
        data["channels"] = api.portal.get_registry_record(
            "subscription_channels", interface=IRerUfficiostampaSettings
        )
        return data


class SubscriptionAdd(DataAdd):
    store = ISubscriptionsStore

    def validate_form(self, form_data):
        """
        check all required fields and parameters
        """
        for field in ["channels", "email"]:
            if not form_data.get(field, ""):
                raise BadRequest(f"Campo obbligatorio mancante: {field}")


class SubscriptionUpdate(DataUpdate):
    """Update an entry"""

    store = ISubscriptionsStore


class SubscriptionDelete(DataDelete):
    store = ISubscriptionsStore


class SubscriptionsClear(DataClear):
    store = ISubscriptionsStore
