from django.forms import IntegerField

from django_filters import (
    ChoiceFilter,
    MultipleChoiceFilter,
    ModelMultipleChoiceFilter,
)

from utilities.filters import (
    multivalue_field_factory,
    MultiValueNumberFilter,
    TreeNodeMultipleChoiceFilter,
)


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
