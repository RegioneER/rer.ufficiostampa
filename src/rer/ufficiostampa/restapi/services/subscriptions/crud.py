# -*- coding: utf-8 -*-
from plone import api
from plone.restapi.deserializer import json_body
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service
from rer.ufficiostampa.interfaces import IRerUfficiostampaSettings
from rer.ufficiostampa.interfaces import ISubscriptionsStore
from zExceptions import BadRequest
from zope.component import getUtility
from zope.publisher.interfaces import IPublishTraverse
from zope.interface import implementer


class SubscriptionsGet(Service):
    def reply(self):
        # soup = get_soup("subscriptions_soup", self.context)
        tool = getUtility(ISubscriptionsStore)
        records = [self.expand_data(x) for x in tool.search()]
        data = {
            "@id": "{}/@subscriptions".format(self.context.absolute_url()),
            "items": records,
            "items_total": len(records),
            "channels": api.portal.get_registry_record(
                "subscription_channels", interface=IRerUfficiostampaSettings
            ),
        }
        return data

    def expand_data(self, record):
        data = {k: json_compatible(v) for k, v in record.attrs.items()}
        data["id"] = record.intid
        return data


class SubscriptionAdd(Service):
    def reply(self):
        form_data = json_body(self.request)
        self.validate_form(form_data=form_data)

        tool = getUtility(ISubscriptionsStore)
        res = tool.add(form_data)

        if res:
            return self.reply_no_content()

        self.request.response.setStatus(500)
        return dict(
            error=dict(
                type="InternalServerError",
                message="Unable to add subscription. Contact site manager.",
            )
        )

    def validate_form(self, form_data):
        """
        check all required fields and parameters
        """
        for field in ["channels", "email"]:
            if not form_data.get(field, ""):
                raise BadRequest(
                    "Campo obbligatorio mancante: {}".format(field)
                )


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
            raise BadRequest("Subscriber id should be a number.")
        return self

    def reply(self):
        raise NotImplementedError


class SubscriptionUpdate(TraversableService):
    """ Update an entry """

    def reply(self):
        if not self.id:
            raise BadRequest("Missing subscriber id")

        form_data = json_body(self.request)

        tool = getUtility(ISubscriptionsStore)
        res = tool.update(id=self.id, data=form_data)
        if not res:
            return self.reply_no_content()
        if res.get("error", "") == "NotFound":
            raise BadRequest(
                'Unable to find subscription with id "{}"'.format(self.id)
            )
        self.request.response.setStatus(500)
        return dict(
            error=dict(
                type="InternalServerError",
                message="Unable to update subscription. Contact site manager.",
            )
        )


class SubscriptionDelete(TraversableService):
    def reply(self):
        if not self.id:
            raise BadRequest("Missing subscriber id")
        tool = getUtility(ISubscriptionsStore)
        res = tool.delete(id=self.id)
        if not res:
            return self.reply_no_content()
        if res.get("error", "") == "NotFound":
            raise BadRequest(
                'Unable to find subscription with id "{}"'.format(self.id)
            )
        self.request.response.setStatus(500)
        return dict(
            error=dict(
                type="InternalServerError",
                message="Unable to delete subscription. Contact site manager.",
            )
        )


class SubscriptionsClear(Service):
    def reply(self):
        # soup = get_soup("subscriptions_soup", self.context)
        tool = getUtility(ISubscriptionsStore)
        tool.clear()
        return self.reply_no_content()
