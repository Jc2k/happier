import asyncclick as click

from .resource import Resource


class Area(Resource):

    kind = "Area"
    version = "v1"
    short_names = ["area"]

    @property
    def description(self):
        name = self.manifest["name"]
        return f"{self.kind}/{name}"

    async def get_remote(self):
        area_list = await self.connection.call("config/area_registry/list")
        for area in area_list:
            if area["name"] == self.manifest["name"]:
                return area
        return None

    async def create(self):
        await self.connection.call(
            "config/area_registry/create", name=self.manifest["name"]
        )

    async def delete(self):
        remote = await self.get_remote()
        if not remote:
            # Already deleted
            return
        await self.connection.call(
            "config/area_registry/delete", area_id=remote["area_id"]
        )
        click.secho(f"{self.kind}/{self.description} was deleted.", fg="green")
