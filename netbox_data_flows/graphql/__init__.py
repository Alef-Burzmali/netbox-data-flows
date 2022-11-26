from graphene import ObjectType

from netbox.graphql.fields import ObjectField, ObjectListField

from .applications import *
from .dataflows import *
from .objectaliases import *


class Query(ObjectType):
    application_role = ObjectField(ApplicationRoleType)
    application_role_list = ObjectListField(ApplicationRoleType)

    application = ObjectField(ApplicationType)
    application_list = ObjectListField(ApplicationType)

    dataflow = ObjectField(DataFlowType)
    dataflow_list = ObjectListField(DataFlowType)

    dataflow_template = ObjectField(DataFlowTemplateType)
    dataflow_template_list = ObjectListField(DataFlowTemplateType)

    objectalias = ObjectField(ObjectAliasType)
    objectalias_list = ObjectListField(ObjectAliasType)


schema = Query
