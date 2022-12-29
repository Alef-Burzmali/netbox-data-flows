from netbox.search import SearchIndex

from . import models


class ApplicationRoleIndex(SearchIndex):
    model = models.ApplicationRole
    fields = (
        ("name", 100),
        ("slug", 110),
        ("description", 500),
    )


class ApplicationIndex(SearchIndex):
    model = models.Application
    fields = (
        ("name", 100),
        ("description", 500),
        ("comments", 5000),
    )


class DataFlowIndex(SearchIndex):
    model = models.DataFlow
    fields = (
        ("name", 100),
        ("description", 500),
        ("comments", 5000),
    )


class DataFlowGroupIndex(SearchIndex):
    model = models.DataFlowGroup
    fields = (
        ("name", 100),
        ("slug", 110),
        ("description", 500),
        ("comments", 5000),
    )


class ObjectAliasIndex(SearchIndex):
    model = models.ObjectAlias
    fields = (
        ("name", 100),
        ("description", 500),
    )


indexes = (
    ApplicationRoleIndex,
    ApplicationIndex,
    DataFlowIndex,
    DataFlowGroupIndex,
    ObjectAliasIndex,
)
