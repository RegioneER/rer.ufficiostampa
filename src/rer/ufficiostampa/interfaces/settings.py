from plone.restapi.controlpanels import IControlpanel
from plone.supermodel import model
from rer.ufficiostampa import _
from zope import schema


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

    default_acura_di = schema.TextLine(
        title=_(
            "default_acura_di_label",
            default="Default a cura di",
        ),
        description=_(
            "default_acura_di_help",
            default="Inserire il percorso della pagina a cura di predefinita.",
        ),
        required=False,
        default="/amministrazione/aree-amministrative/ufficio-stampa",
    )

    default_argomenti = schema.List(
        title=_(
            "default_argomenti_label",
            default="Default argomenti",
        ),
        description=_(
            "default_argomenti_help",
            default="Inserire i percorsi delle pagine argomenti predefinite."
            "Una per riga.",
        ),
        required=False,
        default=[
            "/argomenti/sala-stampa",
            "/argomenti/comunicazione-istituzionale",
        ],
        value_type=schema.TextLine(),
    )


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
