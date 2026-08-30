from django.db.models import Q
from django.utils.html import format_html_join

from core.models import ObjectType

from ipam.models import IPAddress


def object_list_to_string(objects, *, linkify=False, default="", separator=", "):
    """Take a list of objects and return a string, with optional links."""
    if not objects:
        return default

    if linkify:
        return format_html_join(
            separator,
            '<a href="{}">{}</a>',
            ((o.get_absolute_url(), str(o)) for o in objects),
        )

    return separator.join(str(o) for o in objects)


def _get_ip_qs(device):
    """Return a querystring matching any IP assigned to the device."""
    interfaces = device.interfaces.all()
    ct = ObjectType.objects.get_for_model(interfaces.model)

    return Q(
        assigned_object_type=ct.pk,
        assigned_object_id__in=interfaces,
    )


def get_device_ipaddresses(*devices, primary=False, oob=False):
    """Return the list of IP addresses of a list of devices or virtual machines.

    If primary is True, primary IP v4 and v6 are returned
    If oob is True, oob IP is returned
    If neither primary nor oob is True, all assigned IPs are returned.
    """
    if not devices:
        return IPAddress.objects.none()

    qs = Q()
    for dev in devices:
        if not primary and not oob:
            qs |= _get_ip_qs(dev)
            continue

        if primary and dev.primary_ip4_id:
            qs |= Q(pk=dev.primary_ip4_id)
        if primary and dev.primary_ip6_id:
            qs |= Q(pk=dev.primary_ip6_id)
        if oob and hasattr(dev, "oob_ip_id"):
            qs |= Q(pk=dev.oob_ip_id)

    if qs == Q():
        return IPAddress.objects.none()

    return IPAddress.objects.filter(qs)


def get_ipaddress_host(ip_address):
    """Return the Device or VirtualMachine an IP address is assigned to, if any."""
    assigned_object = getattr(ip_address, "assigned_object", None)
    if not assigned_object:
        return None

    if hasattr(assigned_object, "device"):
        return assigned_object.device
    if hasattr(assigned_object, "virtual_machine"):
        return assigned_object.virtual_machine

    return None
