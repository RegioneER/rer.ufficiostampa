from plone.registry.interfaces import IRecordModifiedEvent
from rer.ufficiostampa.interfaces.settings import IRerUfficiostampaSettings
from zope.component import getUtility
from rer.ufficiostampa.interfaces import ISubscriptionsStore
from zope.component import adapter


@adapter(IRecordModifiedEvent)
def update_channels_list(event):
    """ """
    if event.record.interface != IRerUfficiostampaSettings:
        return
    if event.record.fieldName != "subscription_channels":
        return
    removed_channels = list(set(event.oldValue) - set(event.newValue))

    # now remove entry from subscriptions
    tool = getUtility(ISubscriptionsStore)

    for channel in removed_channels:
        records = tool.search(query={"channels": channel})
        for record in records:
            new_channels = [x for x in record.attrs["channels"] if x != channel]
            tool.update(id=record.intid, data={"channels": new_channels})
