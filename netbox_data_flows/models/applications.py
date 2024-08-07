from django.db import models
from django.urls import reverse

from netbox.models import NetBoxModel, OrganizationalModel
from netbox.models.features import ContactsMixin


__all__ = (
    "ApplicationRole",
    "Application",
)


class ApplicationRole(OrganizationalModel):
    """
    Functional role of an application.

    e.g.: "Infrastructure", "Management", "Business"
    """

    # Inherited fields:
    # name - unique
    # slug - unique
    # description

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("plugins:netbox_data_flows:applicationrole", args=[self.pk])


class Application(ContactsMixin, NetBoxModel):
    """Representation of an application hosted on devices or VM."""

    name = models.CharField(max_length=100, unique=True, help_text="The name of this application")
    description = models.CharField(
        max_length=200,
        blank=True,
    )
    role = models.ForeignKey(
        to=ApplicationRole,
        on_delete=models.SET_NULL,
        related_name="applications",
        blank=True,
        null=True,
        help_text="The role of this application",
    )
    comments = models.TextField(blank=True)

    class Meta:
        ordering = ("name",)

    clone_fields = ("role",)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("plugins:netbox_data_flows:application", args=[self.pk])
