from .resources import Resource
import yaml

def load_manifests(connection, manifest):
    resources = []
    for record in yaml.safe_load_all(manifest):
        if not record:
            # Ignore empty records
            continue

        if "kind" not in record:
            raise RuntimeError("Invalid manifest")

        resource_cls = Resource.class_for_kind(record["kind"])
        if not resource_cls:
            raise RuntimeError("Invalid manifest")

        resource = resource_cls(connection, record)
        resources.append(resource)
    return resources
