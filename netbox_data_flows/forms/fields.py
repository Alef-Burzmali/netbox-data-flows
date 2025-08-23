from django import forms

from utilities.data import array_to_string
from utilities.forms.fields import DynamicModelMultipleChoiceField
from utilities.forms.fields import NumericArrayField as NumericArrayField_


__all__ = ("NumericArrayField",)


class NumericArrayField(NumericArrayField_):
    """Format ranges in a human-friendly way before displaying the field."""

    def prepare_value(self, value):
        if not value:
            return ""

        if isinstance(value, str):
            return value

        try:
            value = [int(v) for v in value]
        except TypeError:
            return ""

        return array_to_string(value)


class IcmpTypeChoiceField(forms.TypedMultipleChoiceField):
    """MultipleChoiceField with coercion to int and "Any" as placeholder."""

    def __init__(self, *args, placeholder=None, **kwargs):
        kwargs["coerce"] = int

        super().__init__(*args, **kwargs)

        if placeholder is not None:
            self.widget.attrs["placeholder"] = placeholder


class PlaceholderModelMultipleChoiceField(DynamicModelMultipleChoiceField):
    """DynamicModelMultipleChoiceField with an optional placeholder definition."""

    def __init__(self, *args, placeholder=None, **kwargs):
        super().__init__(*args, **kwargs)

        if placeholder is not None:
            self.widget.attrs["placeholder"] = placeholder
