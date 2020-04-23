from .resource import Resource


class Area(Resource):

    kind = "Area"
    version = "v1"

    async def get_remote(self):
        area_list = await self.connection.call("config/area_registry/list")
        for area in area_list:
            if area["name"] == self.name:
                return area
        return None

    async def get_name(self):
        return self.name

    async def get_spec(self):
        return {}

    async def update(self):
        pass

    async def create(self):
        await self.connection.call("config/area_registry/create", name=self.name)

    async def delete(self):
        remote = await self.get_remote()
        if not remote:
            # Already deleted
            return
        await self.connection.call("config/area_registry/delete", area_id=remote["area_id"])

