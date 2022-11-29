from graphene import ObjectType

from netbox.graphql.fields import ObjectField, ObjectListField

from .applications import *
from .dataflows import *
from .groups import *
from .objectaliases import *


class Query(ObjectType):
    application_role = ObjectField(ApplicationRoleType)
    application_role_list = ObjectListField(ApplicationRoleType)

    application = ObjectField(ApplicationType)
    application_list = ObjectListField(ApplicationType)

    dataflow = ObjectField(DataFlowType)
    dataflow_list = ObjectListField(DataFlowType)

    dataflowgroup = ObjectField(DataFlowGroupType)
    dataflowgroup_list = ObjectListField(DataFlowGroupType)

    objectalias = ObjectField(ObjectAliasType)
    objectalias_list = ObjectListField(ObjectAliasType)

    objectaliastarget = ObjectField(ObjectAliasTargetType)
    objectaliastarget_list = ObjectListField(ObjectAliasTargetType)


schema = Query
