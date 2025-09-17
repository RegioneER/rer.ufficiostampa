from plone.autoform import directives
from plone.restapi.controlpanels import IControlpanel
from plone.supermodel import model
from rer.ufficiostampa import _
from zope import schema
from zope.interface import Interface


class IUfficioStampaLogoView(Interface):
    """
    Marker interface for logo
    """


class IRerUfficiostampaSettings(model.Schema):
    legislatures = schema.SourceText(
        title=_(
            "legislatures_label",
            default="List of legislatures",
        ),
        description=_(
            "legislatures_help",
            default="This is a list of all legislatures. The last one is the"
            " one used to fill fields in a new Comunicato.",
        ),
        required=False,
    )

    email_from_name = schema.TextLine(
        title=_(
            "email_from_name_label",
            default="Email from name",
        ),
        description=_(
            "email_from_name_help",
            default="Insert the name of the sender for emails.",
        ),
        required=True,
    )

    email_from_address = schema.TextLine(
        title=_(
            "email_from_address_label",
            default="Email from address",
        ),
        description=_(
            "email_from_address_help",
            default="Insert the email address of the sender for emails.",
        ),
        required=True,
    )

    subscription_channels = schema.List(
        title=_("subscription_channels_label", default="Subscription Channels"),
        description=_(
            "subscription_channels_description",
            default="List of available subscription channels."
            "One per line."
            "These channels will be used for users subscriptions "
            "and for select to which channel send a Comunicato.",
        ),
        required=True,
        default=[],
        missing_value=[],
        value_type=schema.TextLine(),
    )

    token_secret = schema.TextLine(
        title=_("token_secret_label", default="Token secret"),
        description=_(
            "token_secret_help",
            default="Insert the secret key for token generation.",
        ),
        required=True,
    )
    token_salt = schema.TextLine(
        title=_("token_salt_label", default="Token salt"),
        description=_(
            "token_salt_help",
            default="Insert the salt for token generation. This, in "
            "conjunction with the secret, will generate unique tokens for "
            "subscriptions management links.",
        ),
        required=True,
    )

    frontend_url = schema.TextLine(
        title=_("frontend_url_label", default="Frontend URL"),
        description=_(
            "frontend_url_help",
            default="If the frontend site is published with a different URL "
            "than the backend, insert it here. All links in emails will be "
            "converted with that URL.",
        ),
        required=False,
    )
    external_sender_url = schema.TextLine(
        title=_("external_sender_url_label", default="External sender URL"),
        description=_(
            "external_sender_url_help",
            default="If you want to send emails with an external tool "
            "(rer.newsletterdispatcher.flask), insert the url of the service "
            "here. If empty, all emails will be sent from Plone.",
        ),
        required=False,
    )

    css_styles = schema.SourceText(
        title=_(
            "css_styles_label",
            default="Styles",
        ),
        description=_(
            "css_styles_help",
            default="Insert a list of CSS styles for received emails.",
        ),
        required=False,
    )
    mail_logo = schema.Bytes(
        title=_("mail_logo_label", default="Mail logo"),
        description=_(
            "mail_logo_help",
            default="Insert a logo that will be used in the emails.",
        ),
        required=False,
    )
    comunicato_number = schema.Int(
        title=_(
            "comunicato_number_label",
            default="Comunicato number",
        ),
        description=_(
            "comunicato_number_help",
            default="The number of last sent Comunicato. You don't have to "
            "edit this. It's automatically updated when a Comunicato is published.",  # noqa
        ),
        required=True,
        default=0,
    )
    comunicato_year = schema.Int(
        title=_(
            "comunicato_year_label",
            default="Comunicato year",
        ),
        description=_(
            "comunicato_year_help",
            default="You don't have to edit this. It's automatically updated"
            " on every new year.",
        ),
        required=True,
        default=2021,
    )

    recursive_publish = schema.Bool(
        title=_("recursive_publish_label", default="Recursive publish"),
        description=_(
            "recursive_publish_help",
            default="If checked, when a Comunicato/Invito is published, all its "
            "children will be published too. This is useful to publish "
            "all the Cartelle Stampa and Allegati related to a Comunicato.",
        ),
        required=False,
        default=False,
    )
    all_attachments_selected = schema.Bool(
        title=_(
            "all_attachments_selected_label", default="Show all attachments by default"
        ),
        description=_(
            "all_attachments_selected_help",
            default="If checked, in Comunicato/Invito send form, you will have all attachments selected by default.",
        ),
        required=False,
        default=True,
    )
    max_attachments_size = schema.Int(
        title=_("max_attachments_size_label", default="Max attachments size"),
        description=_(
            "max_attachments_size_help",
            default="Set max attachments size that will sent via email. "
            "If an attachment exceed that size, it will be discarded. "
            "Set 0 to not limit the size.",
        ),
        required=False,
        default=0,
    )
    directives.write_permission(email_from_name="rer.ufficiostampa.ManageSettings")
    directives.write_permission(email_from_address="rer.ufficiostampa.ManageSettings")
    directives.write_permission(token_secret="rer.ufficiostampa.ManageSettings")
    directives.write_permission(token_salt="rer.ufficiostampa.ManageSettings")
    directives.write_permission(frontend_url="rer.ufficiostampa.ManageSettings")
    directives.write_permission(external_sender_url="rer.ufficiostampa.ManageSettings")
    directives.write_permission(css_styles="rer.ufficiostampa.ManageSettings")
    directives.write_permission(mail_logo="rer.ufficiostampa.ManageSettings")
    directives.write_permission(comunicato_number="rer.ufficiostampa.ManageSettings")
    directives.write_permission(comunicato_year="rer.ufficiostampa.ManageSettings")
    directives.write_permission(recursive_publish="rer.ufficiostampa.ManageSettings")
    directives.write_permission(
        all_attachments_selected="rer.ufficiostampa.ManageSettings"
    )
    directives.write_permission(max_attachments_size="rer.ufficiostampa.ManageSettings")


class ILegislaturesRowSchema(model.Schema):
    legislature = schema.SourceText(
        title=_(
            "legislature_label",
            default="Legislature",
        ),
        description=_(
            "legislature_help",
            default="Insert the legislature name.",
        ),
        required=True,
    )
    arguments = schema.List(
        title=_(
            "legislature_arguments_label",
            default="Arguments",
        ),
        description=_(
            "legislature_arguments_help",
            default="Insert a list of arguments related to this legislature."
            " One per line.",
        ),
        required=True,
        value_type=schema.TextLine(),
    )


class IUfficioStampaControlPanel(IControlpanel):
    """Control panel for Ufficio Stampa settings."""


class IUfficioStampaManageChannels(IControlpanel):
    """Schema for managing subscription channels."""


class IUfficioStampaManageHistory(IControlpanel):
    """Schema for managing subscription channels."""
