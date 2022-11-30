import logging
from copy import deepcopy

from django import forms
from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.html import escape
from django.utils.safestring import mark_safe

from netbox.views import generic as generic_views
from extras.signals import clear_webhooks
from utilities.exceptions import AbortRequest, PermissionsViolation
from utilities.forms import restrict_form_fields
from utilities.permissions import get_permission_for_model
from utilities.utils import normalize_querydict


__all__ = (
    "AddAliasesForm",
    "AddAliasesView",
)


class AddAliasesForm(forms.Form):
    """Link aliased objects to an object"""

    aliased_fields = tuple()

    def get_aliased_objects(self):
        for field_name in self.aliased_fields:
            if self.cleaned_data[field_name]:
                for obj in self.cleaned_data[field_name]:
                    yield obj


class AddAliasesView(generic_views.ObjectEditView):
    """Link aliased objects to an object"""

    form = None
    alias_model = None
    aliases_attribute = None

    def get_required_permission(self):
        return get_permission_for_model(self.queryset.model, "change")

    def get_aliases(self, aliased_objects):
        for o in aliased_objects:
            yield self.alias_model.get_or_create(o)

    def get(self, request, *args, **kwargs):
        """
        GET request handler.

        Args:
            request: The current request
        """
        obj = get_object_or_404(self.queryset, pk=kwargs["pk"])
        # obj = self.alter_object(obj, request, args, kwargs)
        model = self.queryset.model

        initial_data = normalize_querydict(request.GET)
        form = self.form(initial=initial_data)
        restrict_form_fields(form, request.user)

        return render(
            request,
            self.template_name,
            {
                "model": model,
                "object": obj,
                "form": form,
                "return_url": self.get_return_url(request, obj),
                "prerequisite_model": [],
                **self.get_extra_context(request, obj),
            },
        )

    def post(self, request, *args, **kwargs):
        """
        POST request handler.

        Args:
            request: The current request
        """
        logger = logging.getLogger("netbox.views.ObjectEditView")
        obj = get_object_or_404(self.queryset, pk=kwargs["pk"])

        if obj.pk and hasattr(obj, "snapshot"):
            obj.snapshot()

        form = self.form(data=request.POST, files=request.FILES)
        restrict_form_fields(form, request.user)

        if form.is_valid():
            logger.debug("Form validation was successful")

            try:
                aliases = list(self.get_aliases(form.get_aliased_objects()))

                with transaction.atomic():
                    for a in aliases:
                        if a.pk is None:
                            a.save()
                    getattr(obj, self.aliases_attribute).add(*aliases)

                msg = f"Added {len(aliases)} alias to"
                logger.info(f"{msg} {obj} (PK: {obj.pk})")
                if hasattr(obj, "get_absolute_url"):
                    msg = mark_safe(
                        f'{msg} <a href="{obj.get_absolute_url()}">{escape(obj)}</a>'
                    )
                else:
                    msg = f"{msg} {obj}"
                messages.success(request, msg)

                if "_addanother" in request.POST:
                    redirect_url = request.path
                    return redirect(redirect_url)

                return_url = self.get_return_url(request, obj)
                return redirect(return_url)

            except (AbortRequest, PermissionsViolation) as e:
                logger.debug(e.message)
                form.add_error(None, e.message)
                clear_webhooks.send(sender=self)

        else:
            logger.debug("Form validation failed")

        return render(
            request,
            self.template_name,
            {
                "object": obj,
                "form": form,
                "return_url": self.get_return_url(request, obj),
                **self.get_extra_context(request, obj),
            },
        )
