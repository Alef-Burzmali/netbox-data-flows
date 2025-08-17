from django.forms import IntegerField
from django_filters import ChoiceFilter, ModelMultipleChoiceFilter, MultipleChoiceFilter

from extras.filters import TagFilter
from utilities.filters import MultiValueNumberFilter, TreeNodeMultipleChoiceFilter, multivalue_field_factory


__all__ = (
    "ChoiceFilter",
    "ModelMultipleChoiceFilter",
    "MultipleChoiceFilter",
    "MultiValueNumberFilter",
    "MultiValueNumericArrayFilter",
    "TreeNodeMultipleChoiceFilter",
    "TagIDFilter",
)


class MultiValueNumericArrayFilter(MultipleChoiceFilter):
    field_class = multivalue_field_factory(IntegerField)


# FIXME: Compat NetBox 4.2.9
class TagIDFilter(TagFilter):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("field_name", "tags__id")
        kwargs.setdefault("to_field_name", "id")
        super().__init__(*args, **kwargs)
