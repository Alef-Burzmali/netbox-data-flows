from netbox_data_flows import models, choices


class TestData:
    _applicationsroles = []
    _applications = []
    _dataflows = []
    _dataflowgroups = []
    _objectaliases = []

    @classmethod
    def create_applicationroles(cls):
        if not cls._applicationsroles:
            cls._applicationsroles = (
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
            for obj in cls._applicationsroles:
                obj.save()

        return cls._applicationsroles

    @classmethod
    def create_applications(cls):
        if not cls._applications:
            roles = cls.create_applicationroles()

            cls._applications = (
                models.Application(
                    name="Application 1", description="barfoo 1", role=roles[0]
                ),
                models.Application(
                    name="Application 2", description="barfoo 2", role=roles[1]
                ),
                models.Application(
                    name="Application 3", description="barfoo 3", role=roles[1]
                ),
                models.Application(
                    name="Application 4", description="barfoo 4", role=roles[2]
                ),
                models.Application(
                    name="Application 5", description="barfoo 5", role=None
                ),
                models.Application(
                    name="Application 6", description="barfoo 6", role=None
                ),
            )
            for obj in cls._applications:
                obj.save()

        return cls._applications

    @classmethod
    def create_dataflowgroups(cls):
        if not cls._dataflowgroups:
            apps = cls.create_applications()

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

            cls._dataflowgroups = [
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
            ]
            for obj in cls._dataflowgroups:
                obj.save()

        return cls._dataflowgroups
