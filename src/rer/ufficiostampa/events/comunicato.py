from plone import api
from Products.CMFPlone.interfaces import ISelectableConstrainTypes
from rer.ufficiostampa.interfaces import IRerUfficiostampaSettings
from rer.ufficiostampa.utils import get_next_comunicato_number


def changeWorkflow(item, event):
    if event.action == "publish":
        if item.portal_type == "ComunicatoStampa" and not getattr(
            item, "comunicato_number", ""
        ):
            setattr(item, "comunicato_number", get_next_comunicato_number())
    try:
        recursive_publish = api.portal.get_registry_record(
            "recursive_publish",
            interface=IRerUfficiostampaSettings,
        )
    except KeyError:
        recursive_publish = False
    if not recursive_publish:
        return

    if event.action in ["publish", "retract", "reject"]:
        # recursive publish/unpublish contents
        for brain in api.content.find(context=item):
            if brain.UID == item.UID():
                continue
            obj = brain.getObject()
            if event.action == "publish" and brain.review_state == "private":
                api.content.transition(obj, "publish")
            elif (
                event.action in ["retract", "reject"]
                and brain.review_state == "published"
            ):
                api.content.transition(obj, event.action)


def createComunicato(item, event):
    """
    Reset it when copy a comunicato and force set legislature
    """
    setattr(item, "comunicato_number", "")
    setattr(item, "message_sent", False)

    # this is needed because it's a readonly field and that doesn't store anything
    # in the content. Side effect is that it also have a defaultFactory value that
    # always return the latest legislature. When you try to edit an item for a past
    # legislature, you always get the latest one, instead the "stored" one.

    setattr(item, "legislature", getattr(item, "legislature", ""))


def createCartellaStampa(item, event):
    if item.portal_type == "ComunicatoStampa":
        cartella_stampa = api.content.create(
            container=item,
            type="CartellaStampa",
            title="Cartella stampa",
            id="cartella-stampa",
        )

        # exclude from search
        cartella_stampa.exclude_from_search = True
        cartella_stampa.reindexObject(idxs=["exclude_from_search"])

        # disable CartellaStampa from allowed types
        constraints_context = ISelectableConstrainTypes(item)
        constraints_context.setConstrainTypesMode(1)
        constraints_context.setLocallyAllowedTypes(["Image", "File"])


def fixText(item, event):
    transform_tool = api.portal.get_tool(name="portal_transforms")
    item.title = transform_tool.convert(
        "html_to_web_intelligent_plain_text", item.title
    ).getData()
    item.description = transform_tool.convert(
        "html_to_web_intelligent_plain_text", item.description
    ).getData()
