from .registry import Registry
import asyncclick as click

short_names = {}
long_names = {}

class Resource:

    kind = None
    version = None
    short_names = []
    update_policy = "create_only"

    def __init__(self, connection, manifest):
        self.connection = connection
        self.manifest = manifest

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        if not cls.kind:
            raise RuntimeError(f"{cls} does not have a kind attribute set")

        if not cls.version:
            raise RuntimeError(f"{cls} does not have a version attribute set")

        if cls.kind in long_names:
            raise RuntimeError(f"{cls} is a duplicate of resource kind {cls.kind}")

        long_names[cls.kind] = cls

        for short_name in cls.short_names:
            if short_name in short_names:
                raise RuntimeError(f"{cls} is a duplicate of short name {short_name}")

            short_names[short_name] = cls

    @classmethod
    def class_for_kind(cls, kind_or_short_name):
        if kind_or_short_name in long_names:
            return long_names[kind_or_short_name]
        if kind_or_short_name in short_names:
            return short_names[kind_or_short_name]
        print("Hi", kind_or_short_name)
        return None

    @property
    def description(self):
        raise NotImplementedError

    def remote_to_dict(self):
        return {
            "kind": self.kind,
            "version": self.vesion,
            "name": self.get_name(),
            "spec": self.get_spec(),
        }

    async def update(self):
        """Update an existing object in place."""
        pass

    async def apply(self):
        """Apply target state to a resource in Home Assistant, creating it if it doesn't exist."""
        remote = await self.get_remote()

        if remote and self.update_policy == "recreate":
            await self.delete()
            remote = None

        if not await self.get_remote():
            click.secho(f"Creating {self.description}", fg="green")
            await self.create()
            return

        await self.update()
