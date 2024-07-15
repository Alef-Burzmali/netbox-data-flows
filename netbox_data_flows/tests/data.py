import itertools

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
    _targets = None

    def get_applicationroles(self):
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

    def get_applications(self):
        if not self._applications:
            roles = self.get_applicationroles()

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

    def get_dataflowgroups(self):
        if not self._dataflowgroups:
            apps = self.get_applications()

            group1 = models.DataFlowGroup(
                application=None,
                parent=None,
                name="Group 1",
                slug="group-1",
                description="foobar1",
                status=choices.DataFlowStatusChoices.STATUS_ENABLED,
            )
            group11 = models.DataFlowGroup(
                application=apps[0],
                parent=group1,
                name="Group 1.1",
                slug="group-1-1",
                description="foobar11",
                status=choices.DataFlowStatusChoices.STATUS_DISABLED,
            )
            group111 = models.DataFlowGroup(
                application=apps[0],
                parent=group11,
                name="Group 1.1.1",
                slug="group-1-1-1",
                description="foobar111",
                status=choices.DataFlowStatusChoices.STATUS_ENABLED,
            )
            group112 = models.DataFlowGroup(
                application=apps[1],
                parent=group11,
                name="Group 1.1.2",
                slug="group-1-1-2",
                description="foobar112",
                status=choices.DataFlowStatusChoices.STATUS_DISABLED,
            )
            group113 = models.DataFlowGroup(
                application=apps[0],
                parent=group11,
                name="Group 1.1.3",
                slug="group-1-1-3",
                description="foobar113",
                status=choices.DataFlowStatusChoices.STATUS_ENABLED,
            )
            group12 = models.DataFlowGroup(
                application=apps[2],
                parent=group1,
                name="Group 1.2",
                slug="group-1-2",
                description="foobar12",
                status=choices.DataFlowStatusChoices.STATUS_ENABLED,
            )
            group121 = models.DataFlowGroup(
                application=None,
                parent=group12,
                name="Group 1.2.1",
                slug="group-1-2-1",
                description="foobar121",
                status=choices.DataFlowStatusChoices.STATUS_ENABLED,
            )
            group122 = models.DataFlowGroup(
                application=apps[3],
                parent=group12,
                name="Group 1.2.2",
                slug="group-1-2-2",
                description="foobar122",
                status=choices.DataFlowStatusChoices.STATUS_DISABLED,
            )
            group2 = models.DataFlowGroup(
                application=apps[4],
                parent=None,
                name="Group 2",
                slug="group-2",
                description="foobar2",
                status=choices.DataFlowStatusChoices.STATUS_ENABLED,
            )
            group3 = models.DataFlowGroup(
                application=None,
                parent=None,
                name="Group 3",
                slug="group-3",
                description="foobar3",
                status=choices.DataFlowStatusChoices.STATUS_ENABLED,
            )

            self._dataflowgroups = (
                group1,
                group11,
                group111,
                group112,
                group113,
                group12,
                group121,
                group122,
                group2,
                group3,
            )
            for obj in self._dataflowgroups:
                obj.save()

        return self._dataflowgroups

    def get_objectaliastargets(self):
        if not self._targets:
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

            # Targets
            # 0-2: Prefix
            # 3-4: Prefix with VLAN
            # 5-6: IP Ranges
            # 7-8: IP of device 1
            # 9-10: IP of vm 1
            # 11-11: IP of device 2
            # 12-12: IP of vm 2
            # 13-14: IPs
            self._targets = []
            for obj in itertools.chain(prefixes, ranges, ips):
                t = models.ObjectAliasTarget.get_or_create(obj)
                t.save()
                self._targets += [t]

            self._targets = tuple(self._targets)

        return self._targets

    def get_objectaliases(self):
        if not self._objectaliases:
            self.get_objectaliastargets()

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

            targets = models.ObjectAliasTarget.objects.order_by("pk")
            self._objectaliases[0].targets.set(targets[0:2])
            self._objectaliases[1].targets.set([])
            self._objectaliases[2].targets.set([targets[0], targets[5]])
            self._objectaliases[3].targets.set(targets[7:11])
            self._objectaliases[4].targets.set([targets[7], targets[8], targets[11]])
            self._objectaliases[5].targets.set([targets[12]])
            self._objectaliases[6].targets.set(targets[13:15])

        return self._objectaliases

    def get_dataflows(self):
        if not self._dataflows:
            apps = self.get_applications()
            groups = self.get_dataflowgroups()
            aliases = self.get_objectaliases()

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
                )
            ]
            self._dataflows += [
                models.DataFlow.objects.create(
                    name="Data Flow 2",
                    description="ICMP from any to any",
                    application=None,
                    group=None,
                    status=choices.DataFlowStatusChoices.STATUS_ENABLED,
                    protocol=choices.DataFlowProtocolChoices.PROTOCOL_ICMP,
                    source_ports=None,
                    destination_ports=None,
                )
            ]
            self._dataflows += [
                models.DataFlow.objects.create(
                    name="Data Flow 3",
                    description=("TCP/80 from Object Alias 1 to Object Alias 2, " "inherit disabled"),
                    application=apps[0],
                    group=groups[2],
                    status=choices.DataFlowStatusChoices.STATUS_ENABLED,
                    protocol=choices.DataFlowProtocolChoices.PROTOCOL_TCP,
                    source_ports=None,
                    destination_ports=[80],
                )
            ]
            self._dataflows[-1].sources.set([aliases[0]])
            self._dataflows[-1].destinations.set([aliases[1]])

            self._dataflows += [
                models.DataFlow.objects.create(
                    name="Data Flow 4",
                    description=("TCP/81 and TCP/82 from Object Alias 1 to Object Alias 2, " "inherit enabled"),
                    application=apps[1],
                    group=groups[6],
                    status=choices.DataFlowStatusChoices.STATUS_ENABLED,
                    protocol=choices.DataFlowProtocolChoices.PROTOCOL_TCP,
                    source_ports=None,
                    destination_ports=[81, 82],
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
                )
            ]
            self._dataflows[-1].sources.set([aliases[1], aliases[2]])
            self._dataflows[-1].destinations.set([aliases[3]])

            self._dataflows += [
                models.DataFlow.objects.create(
                    name="Data Flow 6",
                    description=("TCP+UDP/100 from Any to Object Alias 4 and Object Alias 5, " "inherit enabled"),
                    application=apps[1],
                    group=groups[6],
                    status=choices.DataFlowStatusChoices.STATUS_ENABLED,
                    protocol=choices.DataFlowProtocolChoices.PROTOCOL_TCP_UDP,
                    source_ports=None,
                    destination_ports=[100],
                )
            ]
            self._dataflows[-1].destinations.set([aliases[3], aliases[4]])

            self._dataflows += [
                models.DataFlow.objects.create(
                    name="Data Flow 7",
                    description=("SCTP/200 from SCTP/200 from Object Alias 5 to Any, " "inherit enabled"),
                    application=None,
                    group=groups[6],
                    status=choices.DataFlowStatusChoices.STATUS_ENABLED,
                    protocol=choices.DataFlowProtocolChoices.PROTOCOL_SCTP,
                    source_ports=[200],
                    destination_ports=[200],
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
                )
            ]
            self._dataflows[-1].sources.set([aliases[5]])
            self._dataflows[-1].destinations.set([aliases[2], aliases[5]])

            self._dataflows = tuple(self._dataflows)

        return self._dataflows
