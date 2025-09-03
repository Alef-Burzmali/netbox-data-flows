from core.models import ObjectType
from extras.choices import CustomFieldTypeChoices
from extras.models import CustomField
from utilities.testing import create_tags

from dcim import models as dcim
from ipam import models as ipam
from virtualization import models as virtualization

from netbox_data_flows import choices, models


class TestData:
    _applicationsroles = None
    _applications = None
    _dataflows = None
    _dataflowgroups = None
    _objectaliases = None

    _prefixes = None
    _ranges = None
    _ips = None

    _custom_fields = None
    _tags = None

    @property
    def tags(self):
        if not self._tags:
            self._tags = tuple(create_tags("tag0", "tag1", "tag2", "tag3", "tag4", "tag5", "tag6"))

        return self._tags

    @property
    def applicationroles(self):
        if not self._applicationsroles:
            self._applicationsroles = (
                models.ApplicationRole(
                    name="Application Role 1",
                    slug="application-role-1",
                    description="foobar 1",
                ),
                models.ApplicationRole(
                    name="Application Role 2",
                    slug="application-role-2",
                    description="foobar 2",
                ),
                models.ApplicationRole(
                    name="Application Role 3",
                    slug="application-role-3",
                    description="foobar 3",
                ),
            )
            for obj in self._applicationsroles:
                obj.save()

        return self._applicationsroles

    @property
    def applications(self):
        if not self._applications:
            roles = self.applicationroles

            self._applications = (
                models.Application(name="Application 1", description="barfoo 1", role=roles[0]),
                models.Application(name="Application 2", description="barfoo 2", role=roles[1]),
                models.Application(name="Application 3", description="barfoo 3", role=roles[1]),
                models.Application(name="Application 4", description="barfoo 4", role=roles[2]),
                models.Application(name="Application 5", description="barfoo 5", role=None),
                models.Application(name="Application 6", description="barfoo 6", role=None),
            )
            for obj in self._applications:
                obj.save()

        return self._applications

    @property
    def dataflowgroups(self):
        if not self._dataflowgroups:
            apps = self.applications
            tags = self.tags

            group1 = models.DataFlowGroup(
                # pk = 0
                application=None,
                parent=None,
                name="Group 1",
                slug="group-1",
                description="foobar1",
                status=choices.DataFlowStatusChoices.STATUS_ENABLED,
                # inherited status = enabled
                # tags = [0,1]
                # inherited tags = [0,1]
            )
            group11 = models.DataFlowGroup(
                # pk = 1
                application=apps[0],
                parent=group1,
                name="Group 1.1",
                slug="group-1-1",
                description="foobar11",
                status=choices.DataFlowStatusChoices.STATUS_DISABLED,
                # inherited status = disabled
                # tags = [1]
                # inherited tags = [0,1]
            )
            group111 = models.DataFlowGroup(
                # pk = 2
                application=apps[0],
                parent=group11,
                name="Group 1.1.1",
                slug="group-1-1-1",
                description="foobar111",
                status=choices.DataFlowStatusChoices.STATUS_ENABLED,
                # inherited status = disabled
                # tags = [3]
                # inherited tags = [0,1,3]
            )
            group112 = models.DataFlowGroup(
                # pk = 3
                application=apps[1],
                parent=group11,
                name="Group 1.1.2",
                slug="group-1-1-2",
                description="foobar112",
                status=choices.DataFlowStatusChoices.STATUS_DISABLED,
                # inherited status = disabled
                # tags = [2]
                # inherited tags = [0,1,2]
            )
            group113 = models.DataFlowGroup(
                # pk = 4
                application=apps[0],
                parent=group11,
                name="Group 1.1.3",
                slug="group-1-1-3",
                description="foobar113",
                status=choices.DataFlowStatusChoices.STATUS_ENABLED,
                # inherited status = disabled
                # tags = []
                # inherited tags = [0,1]
            )
            group12 = models.DataFlowGroup(
                # pk = 5
                application=apps[2],
                parent=group1,
                name="Group 1.2",
                slug="group-1-2",
                description="foobar12",
                status=choices.DataFlowStatusChoices.STATUS_ENABLED,
                # inherited status = enabled
                # tags = []
                # inherited tags = [0,1]
            )
            group121 = models.DataFlowGroup(
                # pk = 6
                application=None,
                parent=group12,
                name="Group 1.2.1",
                slug="group-1-2-1",
                description="foobar121",
                status=choices.DataFlowStatusChoices.STATUS_ENABLED,
                # inherited status = enabled
                # tags = []
                # inherited tags = [0,1]
            )
            group122 = models.DataFlowGroup(
                # pk = 7
                application=apps[3],
                parent=group12,
                name="Group 1.2.2",
                slug="group-1-2-2",
                description="foobar122",
                status=choices.DataFlowStatusChoices.STATUS_DISABLED,
                # inherited status = disabled
                # tags = []
                # inherited tags = [0,1]
            )
            group2 = models.DataFlowGroup(
                # pk = 8
                application=apps[4],
                parent=None,
                name="Group 2",
                slug="group-2",
                description="foobar2",
                status=choices.DataFlowStatusChoices.STATUS_ENABLED,
                # inherited status = enabled
                # tags = []
                # inherited tags = []
            )
            group3 = models.DataFlowGroup(
                # pk = 9
                application=None,
                parent=None,
                name="Group 3",
                slug="group-3",
                description="foobar3",
                status=choices.DataFlowStatusChoices.STATUS_ENABLED,
                # inherited status = enabled
                # tags = []
                # inherited tags = []
            )

            self._dataflowgroups = (
                group1,  # pk = 0
                group11,  # pk = 1
                group111,  # pk = 2
                group112,  # pk = 3
                group113,  # pk = 4
                group12,  # pk = 5
                group121,  # pk = 6
                group122,  # pk = 7
                group2,  # pk = 8
                group3,  # pk = 9
            )
            for obj in self._dataflowgroups:
                obj.save()

            group1.tags.set(tags[0:2])
            group11.tags.set(tags[1:2])
            group111.tags.set(tags[3:4])
            group112.tags.set(tags[2:3])

        return self._dataflowgroups

    @property
    def targetobjects(self):
        if not self._prefixes:
            vlans = [
                ipam.VLAN(
                    vid=100,
                    name="Vlan 100",
                ),
                ipam.VLAN(
                    vid=200,
                    name="Vlan 200",
                ),
            ]
            ipam.VLAN.objects.bulk_create(vlans)

            prefixes = [
                ipam.Prefix(
                    prefix="10.0.0.0/16",
                ),
                ipam.Prefix(
                    prefix="10.0.1.0/24",
                ),
                ipam.Prefix(
                    prefix="10.0.2.0/24",
                ),
                ipam.Prefix(
                    prefix="10.100.0.0/16",
                    vlan=vlans[0],
                ),
                ipam.Prefix(
                    prefix="10.200.0.0/16",
                    vlan=vlans[1],
                ),
            ]
            ipam.Prefix.objects.bulk_create(prefixes)
            self._prefixes = prefixes

            ranges = [
                ipam.IPRange(
                    start_address="10.0.1.10/24",
                    end_address="10.0.1.49/24",
                    size=40,
                ),
                ipam.IPRange(
                    start_address="10.0.2.10/24",
                    end_address="10.0.3.10/24",
                    size=256,
                ),
            ]
            ipam.IPRange.objects.bulk_create(ranges)
            self._ranges = ranges

            ips = [
                ipam.IPAddress(address="10.0.1.1/24"),
                ipam.IPAddress(address="10.0.1.2/24"),
                ipam.IPAddress(address="10.0.2.1/24"),
                ipam.IPAddress(address="10.0.2.2/24"),
                ipam.IPAddress(address="10.0.3.3/24"),
                ipam.IPAddress(address="10.100.1.1/24"),
                ipam.IPAddress(address="10.200.1.1/24"),
                ipam.IPAddress(address="10.10.0.1/24"),
            ]
            ipam.IPAddress.objects.bulk_create(ips)
            self._ips = ips

            site = dcim.Site.objects.create(
                name="Site 1",
                slug="site-1",
            )
            manufacturer = dcim.Manufacturer.objects.create(
                name="Manufacturer 1",
                slug="manufacturer-1",
            )
            dev_type = dcim.DeviceType.objects.create(
                manufacturer=manufacturer,
                model="Device Type 1",
                slug="device-type-1",
                u_height=1,
            )
            dev_role = dcim.DeviceRole.objects.create(
                name="Device Role 1",
                slug="device-role-1",
                color="ff0000",
                vm_role=True,
            )
            devices = [
                dcim.Device(
                    name="Device 1",
                    device_type=dev_type,
                    role=dev_role,
                    site=site,
                ),
                dcim.Device(
                    name="Device 2",
                    device_type=dev_type,
                    role=dev_role,
                    site=site,
                ),
            ]
            interfaces = []
            for obj in devices:
                obj.save()
                interfaces += [
                    dcim.Interface.objects.create(
                        device=obj,
                        name="eth0",
                        type="1000base-t",
                    ),
                    dcim.Interface.objects.create(
                        device=obj,
                        name="eth1",
                        type="1000base-t",
                    ),
                ]

            vms = [
                virtualization.VirtualMachine(
                    name="VM 1",
                ),
                virtualization.VirtualMachine(
                    name="VM 2",
                ),
            ]
            vminterfaces = []
            for obj in vms:
                obj.save()
                vminterfaces += [
                    virtualization.VMInterface.objects.create(
                        virtual_machine=obj,
                        name="eth0",
                    ),
                    virtualization.VMInterface.objects.create(
                        virtual_machine=obj,
                        name="eth1",
                    ),
                ]

            ips[0].assigned_object = interfaces[0]
            ips[1].assigned_object = interfaces[1]
            ips[4].assigned_object = interfaces[2]
            ips[2].assigned_object = vminterfaces[0]
            ips[3].assigned_object = vminterfaces[1]
            ips[5].assigned_object = vminterfaces[2]
            for obj in ips:
                obj.save()

    @property
    def objectaliases(self):
        if not self._objectaliases:
            self.targetobjects

            prefixes = self._prefixes
            ip_ranges = self._ranges
            ip_addresses = self._ips

            self._objectaliases = (
                models.ObjectAlias(
                    name="Object Alias 1",
                    description="Prefixes 1 and 2",
                ),
                models.ObjectAlias(
                    name="Object Alias 2",
                    description="Empty",
                ),
                models.ObjectAlias(
                    name="Object Alias 3",
                    description="Prefix 1 and Range 1",
                ),
                models.ObjectAlias(
                    name="Object Alias 4",
                    description="Device 1 and VM 1",
                ),
                models.ObjectAlias(
                    name="Object Alias 5",
                    description="Device 1 and Device 2",
                ),
                models.ObjectAlias(
                    name="Object Alias 6",
                    description="VM 2",
                ),
                models.ObjectAlias(
                    name="Object Alias 7",
                    description="IP 13 and 14",
                ),
            )
            for obj in self._objectaliases:
                obj.save()

            self._objectaliases[0].prefixes.set(prefixes[0:2])
            self._objectaliases[2].prefixes.set([prefixes[0]])
            self._objectaliases[2].ip_ranges.set([ip_ranges[0]])
            self._objectaliases[3].ip_addresses.set(ip_addresses[0:4])
            self._objectaliases[4].ip_addresses.set(ip_addresses[0:2] + [ip_addresses[4]])
            self._objectaliases[5].ip_addresses.set([ip_addresses[5]])
            self._objectaliases[6].ip_addresses.set(ip_addresses[6:8])

        return self._objectaliases

    @property
    def dataflows(self):
        if not self._dataflows:
            apps = self.applications
            groups = self.dataflowgroups
            aliases = self.objectaliases
            tags = self.tags

            self._dataflows = []
            self._dataflows += [
                models.DataFlow.objects.create(
                    name="Data Flow 1",
                    description="Any from any to any",
                    application=None,
                    group=None,
                    status=choices.DataFlowStatusChoices.STATUS_DISABLED,
                    protocol=choices.DataFlowProtocolChoices.PROTOCOL_ANY,
                    source_ports=None,
                    destination_ports=None,
                    # inherited status = disabled
                    # inherited tags = []
                )
            ]

            self._dataflows += [
                models.DataFlow.objects.create(
                    name="Data Flow 2",
                    description="ICMPv4 Echo Request and Echo Reply from any to any",
                    application=None,
                    group=None,
                    status=choices.DataFlowStatusChoices.STATUS_ENABLED,
                    protocol=choices.DataFlowProtocolChoices.PROTOCOL_ICMPv4,
                    source_ports=None,
                    destination_ports=[choices.ICMPv4TypeChoices.TYPE_ECHO_REPLY, choices.ICMPv4TypeChoices.TYPE_ECHO],
                    # inherited status = enabled
                    # inherited tags = [6]
                )
            ]
            self._dataflows[-1].tags.set(tags[6:7])

            self._dataflows += [
                models.DataFlow.objects.create(
                    name="Data Flow 3",
                    description="TCP/80 from Object Alias 1 to Object Alias 2, inherit disabled",
                    application=apps[0],
                    group=groups[2],
                    status=choices.DataFlowStatusChoices.STATUS_ENABLED,
                    protocol=choices.DataFlowProtocolChoices.PROTOCOL_TCP,
                    source_ports=None,
                    destination_ports=[80],
                    # inherited status = disabled
                    # inherited tags = [0,1,3,4,5]
                )
            ]
            self._dataflows[-1].tags.set(tags[4:6])
            self._dataflows[-1].sources.set([aliases[0]])
            self._dataflows[-1].destinations.set([aliases[1]])

            self._dataflows += [
                models.DataFlow.objects.create(
                    name="Data Flow 4",
                    description="TCP/81 and TCP/82 from Object Alias 1 to Object Alias 2, inherit enabled",
                    application=apps[1],
                    group=groups[6],
                    status=choices.DataFlowStatusChoices.STATUS_ENABLED,
                    protocol=choices.DataFlowProtocolChoices.PROTOCOL_TCP,
                    source_ports=None,
                    destination_ports=[81, 82],
                    # inherited status = enabled
                    # inherited tags = [0,1]
                )
            ]
            self._dataflows[-1].sources.set([aliases[0]])
            self._dataflows[-1].destinations.set([aliases[1]])

            self._dataflows += [
                models.DataFlow.objects.create(
                    name="Data Flow 5",
                    description=(
                        "UDP/81 and UDP/82 from UDP/55, UDP/57 from Object Alias 2 and "
                        "Object Alias 3 to Object Alias 4, inherit enabled but disabled"
                    ),
                    application=apps[1],
                    group=groups[6],
                    status=choices.DataFlowStatusChoices.STATUS_DISABLED,
                    protocol=choices.DataFlowProtocolChoices.PROTOCOL_UDP,
                    source_ports=[55, 57],
                    destination_ports=[81, 82],
                    # inherited status = disabled
                    # inherited tags = [0,1]
                )
            ]
            self._dataflows[-1].sources.set([aliases[1], aliases[2]])
            self._dataflows[-1].destinations.set([aliases[3]])

            self._dataflows += [
                models.DataFlow.objects.create(
                    name="Data Flow 6",
                    description="TCP+UDP/100 from Any to Object Alias 4 and Object Alias 5, inherit enabled",
                    application=apps[1],
                    group=groups[6],
                    status=choices.DataFlowStatusChoices.STATUS_ENABLED,
                    protocol=choices.DataFlowProtocolChoices.PROTOCOL_TCP_UDP,
                    source_ports=None,
                    destination_ports=[100],
                    # inherited status = enabled
                    # inherited tags = [0,1]
                )
            ]
            self._dataflows[-1].destinations.set([aliases[3], aliases[4]])

            self._dataflows += [
                models.DataFlow.objects.create(
                    name="Data Flow 7",
                    description="SCTP/200 from SCTP/200 from Object Alias 5 to Any, inherit enabled",
                    application=None,
                    group=groups[6],
                    status=choices.DataFlowStatusChoices.STATUS_ENABLED,
                    protocol=choices.DataFlowProtocolChoices.PROTOCOL_SCTP,
                    source_ports=[200],
                    destination_ports=[200],
                    # inherited status = enabled
                    # inherited tags = [0,1]
                )
            ]
            self._dataflows[-1].sources.set([aliases[4]])

            self._dataflows += [
                models.DataFlow.objects.create(
                    name="Data Flow 8",
                    description=("TCP/400 from TCP/400 from Object Alias 6 to Object Alias 3"),
                    application=None,
                    group=None,
                    status=choices.DataFlowStatusChoices.STATUS_ENABLED,
                    protocol=choices.DataFlowProtocolChoices.PROTOCOL_TCP,
                    source_ports=[400],
                    destination_ports=[400],
                    # inherited status = enabled
                    # inherited tags = []
                )
            ]
            self._dataflows[-1].sources.set([aliases[5]])
            self._dataflows[-1].destinations.set([aliases[2], aliases[5]])

            self._dataflows = tuple(self._dataflows)

        return self._dataflows

    @property
    def customfields(self):
        if not self._custom_fields:
            apps = self.applications
            self.targetobjects

            def _set_cf(cf, qs, value):
                for instance in qs:
                    instance.custom_field_data[cf] = value
                    instance.save()

            application_type = ObjectType.objects.get_for_model(models.Application)
            cf1 = CustomField.objects.create(
                name="application_single",
                type=CustomFieldTypeChoices.TYPE_OBJECT,
                related_object_type=application_type,
            )
            cf1.object_types.set(
                ObjectType.objects.get_for_models(dcim.Device, virtualization.VirtualMachine, ipam.IPAddress).values()
            )
            # app1 has 7 related objects in 3 models
            _set_cf("application_single", dcim.Device.objects.order_by("?")[0:1], apps[0].pk)
            _set_cf("application_single", virtualization.VirtualMachine.objects.order_by("?")[0:1], apps[0].pk)
            _set_cf("application_single", ipam.IPAddress.objects.order_by("?")[0:5], apps[0].pk)
            # app2 has 3 related objects in 1 models
            _set_cf("application_single", ipam.IPAddress.objects.order_by("?")[0:3], apps[1].pk)

            cf2 = CustomField.objects.create(
                name="application_multi",
                type=CustomFieldTypeChoices.TYPE_MULTIOBJECT,
                related_object_type=application_type,
            )
            cf2.object_types.set(
                ObjectType.objects.get_for_models(dcim.Device, dcim.Site, ipam.VLAN, ipam.Prefix).values()
            )
            # app1 has 5 related objects in 3 models
            # app3 has 2 related objects in 1 models
            # app4 has 7 related objects in 2 models
            _set_cf("application_multi", dcim.Device.objects.all()[0:2], [apps[0].pk, apps[2].pk])
            _set_cf("application_multi", dcim.Site.objects.all()[0:1], [apps[0].pk])
            _set_cf("application_multi", ipam.VLAN.objects.all()[0:2], [apps[0].pk, apps[3].pk])
            _set_cf("application_multi", ipam.Prefix.objects.all()[0:5], [apps[3].pk])

            cf3 = CustomField.objects.create(
                name="not_application",
                type=CustomFieldTypeChoices.TYPE_OBJECT,
                related_object_type=ObjectType.objects.get_for_model(dcim.Device),
            )
            cf3.object_types.set(ObjectType.objects.get_for_models(dcim.Site, ipam.VLAN, ipam.Prefix).values())

            cf4 = CustomField.objects.create(
                name="not_object",
                type=CustomFieldTypeChoices.TYPE_TEXT,
            )
            cf4.object_types.set(ObjectType.objects.get_for_models(dcim.Site).values())

            self._custom_fields = (cf1, cf2, cf3, cf4)

        return self._custom_fields
