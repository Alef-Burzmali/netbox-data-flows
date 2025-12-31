from django.db import models
from django.urls import reverse

from netbox.models import OrganizationalModel, PrimaryModel
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
    # owner

    comments = models.TextField(blank=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("plugins:netbox_data_flows:applicationrole", args=[self.pk])


class Application(ContactsMixin, PrimaryModel):
    """Representation of an application hosted on devices or VM."""

    # Inherited fields:
    # description
    # comments
    # owner

    name = models.CharField(max_length=100, unique=True, help_text="The name of this application")
    role = models.ForeignKey(
        to=ApplicationRole,
        on_delete=models.SET_NULL,
        related_name="applications",
        blank=True,
        null=True,
        help_text="The role of this application",
    )
    tenant = models.ForeignKey(
        to="tenancy.Tenant", on_delete=models.PROTECT, related_name="applications", blank=True, null=True
    )

    class Meta:
        ordering = ("name",)

    clone_fields = ("role", "tenant", "owner")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("plugins:netbox_data_flows:application", args=[self.pk])
