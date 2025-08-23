from django.urls import include, path

from utilities.urls import get_model_urls

from . import views  # noqa F401


APP_LABEL = "netbox_data_flows"


def get_urls(model_name, url_prefix, *, pk="<int:pk>"):
    return (
        path(f"{url_prefix}/", include(get_model_urls(APP_LABEL, model_name, detail=False))),
        path(f"{url_prefix}/{pk}/", include(get_model_urls(APP_LABEL, model_name))),
    )


urlpatterns = (
    *get_urls("application", "applications"),
    *get_urls("applicationrole", "application-roles"),
    *get_urls("dataflow", "dataflows"),
    *get_urls("dataflowgroup", "dataflow-groups"),
    *get_urls("objectalias", "aliases"),
)
