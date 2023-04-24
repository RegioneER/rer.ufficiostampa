from zope.component import adapter, getUtility
from plone.registry.interfaces import IRecordModifiedEvent

from rer.ufficiostampa.interfaces import IRerUfficiostampaSettings
from rer.ufficiostampa.interfaces import ISubscriptionsStore


@adapter(IRerUfficiostampaSettings, IRecordModifiedEvent)
def channelsDeletionHandler(_, event):
    """On channels deletion update the subscribers"""

    if event.record.fieldName != "subscription_channels":
        return

    channels_diff = [i for i in event.oldValue if i not in event.record.value]

    subscriptions = getUtility(ISubscriptionsStore)

    for channel in channels_diff:
        for subsciber in subscriptions.search(query={"channels": channel}):
            subsciber.attrs["channels"].remove(channel)

            if not len(subsciber.attrs["channels"]):
                subscriptions.delete(subsciber.intid)
                continue

            subscriptions.update(subsciber.intid, subsciber.attrs)
