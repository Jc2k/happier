from .resource import Resource
import asyncclick as click


class Dashboard(Resource):

    kind = "Dashboard"
    version = "v1"
    short_names = ["dashboard"]

    @property
    def description(self):
        name = self.manifest["title"]
        return f"{self.kind}/{name}"

    async def get_remote(self):
        dashboard_list = await self.connection.call("lovelace/dashboards/list")
        for dashboard in dashboard_list:
            if dashboard["url_path"] == self.manifest["url_path"]:
                return dashboard
        return None

    async def create(self):
        await self.connection.call("lovelace/dashboards/create", title=self.manifest["title"], url_path=self.manifest["url_path"])
        await self.update()
        click.secho(f"{self.kind}/{self.description} was created.", fg="green")

    async def update(self):
        config = {
            "title": self.manifest["title"],
            "views": self.manifest["views"],
        }

        await self.connection.call("lovelace/config/save", config=config, url_path=self.manifest["url_path"])

        return True

    async def delete(self):
        if self.manifest["url_path"] is None:
            click.secho(f"Cannot delete root dashboard", fg="red")
            return

        remote = await self.get_remote()
        if not remote:
            # Already deleted
            return

        await self.connection.call("lovelace/dashboards/delete", dashboard_id=remote["id"])
        click.secho(f"{self.kind}/{self.description} was deleted.", fg="green")
