from django.core.exceptions import ImproperlyConfigured

from extras.choices import CustomFieldTypeChoices
from extras.models import CustomField
from netbox.plugins.utils import get_plugin_config
from utilities.views import GetRelatedModelsMixin


class GetRelatedCustomFieldModelsMixin(GetRelatedModelsMixin):
    custom_field_setting = None
    _custom_field_name = None
    _custom_field = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_custom_field()

    def init_custom_field(self):
        self._custom_field_name = get_plugin_config(self.queryset.model._meta.app_label, self.custom_field_setting)
        if not self._custom_field_name:
            return

        try:
            self._custom_field = CustomField.objects.get(name=self._custom_field_name)
        except CustomField.DoesNotExist as e:
            raise ImproperlyConfigured(
                f"Custom field `{self._custom_field_name}` does not exists. "
                f"Create it before adding it to the plugin configuration ({self.custom_field_setting})."
            ) from e

        if (
            self._custom_field.type not in (CustomFieldTypeChoices.TYPE_OBJECT, CustomFieldTypeChoices.TYPE_MULTIOBJECT)
            or self._custom_field.related_object_type.model_class() is not self.queryset.model
        ):
            raise ImproperlyConfigured(
                f"Custom field `{self._custom_field_name}` must be of type Object or Multiple Objects "
                f"and must reference model `{self.queryset.model}`. "
                f"Create it before adding it to the plugin configuration ({self.custom_field_setting})."
            )

    def get_related_models(self, request, instance, omit=tuple(), extra=tuple()):
        """
        Get related models of the view's `queryset` model based on a custom_field.

        Args:
            request: Current request being processed.
            instance: The instance related models should be looked up for.
            omit: Remove relationships to these models from the result. Needs to be passed, if related models don't
                provide a `_list` view.
            extra: Add extra models to the list of automatically determined related models. Can be used to add indirect
                relationships.
        """
        if self._custom_field is None:
            return None

        model = self.queryset.model

        operator = "__contains" if self._custom_field.type == CustomFieldTypeChoices.TYPE_MULTIOBJECT else ""
        field_name = f"custom_field_data__{self._custom_field_name}"
        filters = {f"{field_name}{operator}": instance.pk}
        query_str = f"cf_{self._custom_field_name}"

        # Fetch all related models
        related_models = [m.model_class() for m in self._custom_field.object_types.all()]
        related_models = filter(lambda m: m is not model and m not in omit, related_models)
        related_models = [
            (
                m.objects.restrict(request.user, "view").filter(**filters),
                query_str,
            )
            for m in related_models
        ]
        related_models.extend(extra)

        return super().get_related_models(request, instance, omit=omit, extra=related_models)
