from extras.managers import NetBoxTaggableManager
from netbox.models.features import TagsMixin

try:
    from extras.managers import NetBoxTaggableManagerField
except ImportError:
    # Compatibility Netbox < 4.6.2
    from taggit.managers import TaggableManager

    class NetBoxTaggableManagerField(TaggableManager):
        # Copied from NetBox 4.6.2 because we need the same related_name format

        def contribute_to_class(self, cls, name):
            super().contribute_to_class(cls, name)
            if not cls._meta.abstract and self.remote_field.related_name:
                self.remote_field.related_name = self.remote_field.related_name % {
                    "class": cls.__name__.lower(),
                    "app_label": cls._meta.app_label.lower(),
                }

        def deconstruct(self):
            name, _path, args, kwargs = super().deconstruct()
            kwargs.pop("related_name", None)
            return name, "taggit.managers.TaggableManager", args, kwargs


class AccessibleTagsMixin(TagsMixin):
    """
    Tags with accessible related_name.

    Enables support for tag assignment. Assigned tags can be managed via the `tags` attribute,
    which is a `NetBoxTaggableManager` instance. The field is a `NetBoxTaggableManagerField`,
    which performs `%(app_label)s` / `%(class)s` interpolation on `related_name` to avoid
    reverse-accessor collisions between same-named models in different apps (e.g. plugins).

    Overwritten to keep the reverse relationship in NetBox 4.6.2.
    """

    tags = NetBoxTaggableManagerField(
        through="extras.TaggedItem",
        ordering=("weight", "name"),
        manager=NetBoxTaggableManager,
        related_name="%(app_label)s_%(class)s_tagged",
    )

    class Meta:
        abstract = True
