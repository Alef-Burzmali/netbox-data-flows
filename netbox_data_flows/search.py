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


indexes = (
    ApplicationRoleIndex,
    ApplicationIndex,
)
