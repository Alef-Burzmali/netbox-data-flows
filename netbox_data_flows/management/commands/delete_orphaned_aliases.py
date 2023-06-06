import sys

from django.core.management.base import BaseCommand

from netbox_data_flows.models import ObjectAliasTarget


class Command(BaseCommand):
    help = "Delete aliases that are pointing to deleted Netbox objects."

    def add_arguments(self, parser):
        parser.add_argument(
            "--check",
            action="store_true",
            dest="check_only",
            help="Exits with a non-zero status if orphaned aliases exist.",
        )

    def handle(self, *args, **options):
        aliases = ObjectAliasTarget.objects.all()
        orphaned = [a.pk for a in aliases if a.target is None]

        if orphaned:
            if options["check_only"]:
                self.stdout.write(
                    f"Identified {len(orphaned)} orphaned aliases."
                )
                sys.exit(1)
            else:
                ObjectAliasTarget.objects.filter(pk__in=orphaned).delete()
                self.stdout.write(f"Deleted {len(orphaned)} orphaned aliases.")
        else:
            self.stdout.write("No orphaned aliases to delete.")
