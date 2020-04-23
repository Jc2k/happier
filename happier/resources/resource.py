class Resource:

    def __init__(self, connection, **kwargs):
        self.connection = connection
        for key, value in kwargs.items():
            setattr(self, key, value)

    def remote_to_dict(self):
        return {
            "kind": self.kind,
            "version": self.vesion,
            "name": self.get_name(),
            "spec": self.get_spec(),
        }

