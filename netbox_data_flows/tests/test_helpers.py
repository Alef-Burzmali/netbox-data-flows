from django.test import SimpleTestCase

from netbox_data_flows.utils.helpers import object_list_to_string


class DummyObject:
    def __init__(self, url, label):
        self.url = url
        self.label = label

    def get_absolute_url(self):
        return self.url

    def __str__(self):
        return self.label


class ObjectListToStringTestCase(SimpleTestCase):
    def test_linkify_escapes_object_labels(self):
        payload = "<img src=x onerror=alert(1)>"
        result = object_list_to_string(
            [DummyObject("/plugins/netbox-data-flows/object-aliases/1/", payload)],
            linkify=True,
        )

        self.assertIn('<a href="/plugins/netbox-data-flows/object-aliases/1/">', result)
        self.assertIn("&lt;img src=x onerror=alert(1)&gt;", result)
        self.assertNotIn(payload, result)
