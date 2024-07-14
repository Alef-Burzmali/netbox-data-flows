from django.forms import IntegerField
from django_filters import ChoiceFilter, ModelMultipleChoiceFilter, MultipleChoiceFilter

from utilities.filters import MultiValueNumberFilter, TreeNodeMultipleChoiceFilter, multivalue_field_factory


__all__ = (
    "ChoiceFilter",
    "ModelMultipleChoiceFilter",
    "MultipleChoiceFilter",
    "MultiValueNumberFilter",
    "MultiValueNumericArrayFilter",
    "TreeNodeMultipleChoiceFilter",
)


class MultiValueNumericArrayFilter(MultipleChoiceFilter):
    field_class = multivalue_field_factory(IntegerField)
