from django.db.models import Q
from django.utils.safestring import mark_safe

from core.models import ObjectType

from ipam.models import IPAddress


def object_list_to_string(objects, *, linkify=False, default="", separator=", "):
    """Take a list of objects and return a string, with optional links."""
    if not objects:
        return default

    if linkify:
        return mark_safe(separator.join(f'<a href="{o.get_absolute_url()}">{o}</a>' for o in objects))
    else:
        return separator.join(str(o) for o in objects)


def _get_ip_qs(device):
    """Return a querystring matching any IP assigned to the device."""
    interfaces = device.interfaces.all()
    ct = ObjectType.objects.get_for_model(interfaces.model)

    return Q(
        assigned_object_type=ct.pk,
        assigned_object_id__in=interfaces,
    )


def get_one_device_ipaddresses(device):
    """Return the list of IP addresses of a device or virtual machine."""
    ip_qs = _get_ip_qs(device)
    return IPAddress.objects.filter(ip_qs)


def get_device_ipaddresses(*devices):
    """Return the list of IP addresses of a list of devices or virtual machines."""
    qs = Q()
    for dev in devices:
        qs |= _get_ip_qs(dev)

    return IPAddress.objects.filter(qs)
