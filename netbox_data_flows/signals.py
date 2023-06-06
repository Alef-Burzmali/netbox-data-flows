from django.db.models.signals import pre_delete
from django.dispatch import receiver

from netbox_data_flows.models.objectaliases import (
    ObjectAliasTarget,
    OBJECTALIAS_ASSIGNMENT_OBJECTS,
)


@receiver(pre_delete)
def delete_orphaned_alias(sender, instance, **kwargs):
    if sender not in OBJECTALIAS_ASSIGNMENT_OBJECTS:
        return

    alias = ObjectAliasTarget.objects.contains(instance)
    alias.delete()
