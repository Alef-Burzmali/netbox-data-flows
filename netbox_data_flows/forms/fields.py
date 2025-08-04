from utilities.data import array_to_string
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
