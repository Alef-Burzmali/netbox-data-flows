from django.utils.safestring import mark_safe


def object_list_to_string(
    objects, *, linkify=False, default="", separator=", "
):
    """Take a list of objects and return a string, with optional links"""

    if not objects:
        return default

    if linkify:
        return mark_safe(
            separator.join(
                f'<a href="{o.get_absolute_url()}">{o}</a>' for o in objects
            )
        )
    else:
        return separator.join(str(o) for o in objects)
