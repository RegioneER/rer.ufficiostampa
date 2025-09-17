# from plone.app.contenttypes.behaviors.richtext import IRichText
# from plone.app.dexterity.textindexer import searchable
from collective.volto.blocksfield.field import BlocksField
from plone import api
from plone.app.dexterity import textindexer
from plone.autoform import directives
from plone.autoform import directives as form
from plone.supermodel import model
from rer.ufficiostampa import _
from rer.ufficiostampa.interfaces.settings import IRerUfficiostampaSettings
from zope import schema
from zope.component import getUtility
from zope.interface import Interface
from zope.interface import Invalid
from zope.interface import provider
from zope.schema.interfaces import IContextAwareDefaultFactory
from zope.schema.interfaces import IVocabularyFactory


def check_emails(value):
    """Check that all values are valid email addresses"""
    reg_tool = api.portal.get_tool(name="portal_registration")
    for address in value:
        if not reg_tool.isValidEmail(address):
            raise Invalid(
                _(
                    "validation_invalid_email",
                    default="Invalid email address: ${address}",
                    mapping={"address": address},
                )
            )
    return True


@provider(IContextAwareDefaultFactory)
def default_attachments(context):
    try:
        all_attachments_selected = api.portal.get_registry_record(
            "all_attachments_selected",
            interface=IRerUfficiostampaSettings,
        )
    except KeyError:
        all_attachments_selected = True
    if not all_attachments_selected:
        return []
    factory = getUtility(
        IVocabularyFactory, "rer.ufficiostampa.vocabularies.attachments"
    )
    return [x.value for x in factory(context)]


class IComunicatoStampa(model.Schema):
    text = BlocksField(
        title=_("comunicato_text_label", default="Testo"),
        required=False,
    )
    directives.widget("text", allowedBlocks=["slate"])

    message_sent = schema.Bool(
        title=_("label_sent", default="Sent"),
        description="",
        required=False,
        default=False,
    )
    comunicato_number = schema.TextLine(title="", description="", required=False)

    form.omitted("message_sent")
    form.omitted("comunicato_number")

    textindexer.searchable("text")


class IInvitoStampa(IComunicatoStampa):
    """ """


class ICartellaStampa(model.Schema):
    """ """


class ISendForm(Interface):
    channels = schema.List(
        title=_("send_channels_title", default="Channels"),
        description=_(
            "send_channels_description",
            default="Select which channels should receive this Comunicato. "
            "All email address subscribed to this channel will receive it. ",
        ),
        required=False,
        missing_value=(),
        value_type=schema.Choice(source="rer.ufficiostampa.vocabularies.channels"),
    )
    additional_addresses = schema.List(
        title=_("additional_addresses_title", default="Additional addresses"),
        description=_(
            "additional_addresses_description",
            default="Insert a list of additional addressed that will receive "
            "the mail. One per line. You can use this field also for testing "
            "without sending emails to all subscribed addresses.",
        ),
        required=False,
        missing_value=(),
        value_type=schema.TextLine(),
        constraint=check_emails,
    )
    notes = schema.Text(
        title=_("notes_title", default="Notes"),
        description=_(
            "notes_description",
            default="Additional notes.",
        ),
        required=False,
    )
    attachments = schema.List(
        title=_("send_attachments_title", default="Attachments"),
        description=_(
            "send_attachments_description",
            default="Select which attachment you want to send via email. "
            "You can only select first level Files and Images.",
        ),
        required=False,
        missing_value=(),
        value_type=schema.Choice(source="rer.ufficiostampa.vocabularies.attachments"),
        # questa factory mette di default tutti gli allegati del comunicato,
        # la richiesta è di avere il default vuoto
        defaultFactory=default_attachments,
    )
