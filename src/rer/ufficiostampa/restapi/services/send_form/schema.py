from plone.restapi.serializer.converters import IJsonCompatible
from plone.restapi.services import Service
from plone.restapi.types.utils import get_fieldset_infos
from plone.restapi.types.utils import get_fieldsets
from plone.restapi.types.utils import get_jsonschema_properties
from plone.restapi.types.utils import iter_fields
from rer.ufficiostampa import _
from rer.ufficiostampa.browser.send import ISendForm


class SendComunicatoSchema(Service):
    title = _("Send Comunicato Schema")

    def reply(self):
        fieldsets = get_fieldsets(self.context, self.request, ISendForm)
        properties = get_jsonschema_properties(self.context, self.request, fieldsets)
        # Determine required fields
        required = []
        for field in iter_fields(fieldsets):
            if field.field.required:
                required.append(field.field.getName())

        # Include field modes
        for field in iter_fields(fieldsets):
            if field.mode:
                properties[field.field.getName()]["mode"] = field.mode
        return {
            "type": "object",
            "title": self.title,
            "properties": IJsonCompatible(properties),
            "required": required,
            "fieldsets": get_fieldset_infos(fieldsets),
        }
