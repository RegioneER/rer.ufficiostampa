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
        required=True,
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
