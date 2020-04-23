import yaml

from .exceptions import ManifestError
from .resources import Resource


def load_manifests(connection, manifest):
    resources = []
    for record in yaml.safe_load_all(manifest):
        if not record:
            # Silently ignore empty records
            continue

        if "kind" not in record:
            raise ManifestError("Manifest does not specify a 'kind' for a resource")

        resource_cls = Resource.class_for_kind(record["kind"])
        if not resource_cls:
            raise ManifestError(
                "Manifest specifies a 'kind' that is incorrect or not supported"
            )

        resource = resource_cls(connection, record)
        resources.append(resource)

    return resources
