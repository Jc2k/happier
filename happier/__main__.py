import logging

import asyncclick as click
import confuse

from .connection import Connection
from .exceptions import ApplicationError, HomeAssistantError, ManifestError
from .manifests import load_manifests
from .resources import Resource

logger = logging.getLogger(__name__)


async def get_connection(config):
    host = config["default"]["host"].get(str)
    port = config["default"]["port"].get(int)
    access_token = config["default"]["access_token"].get(str)

    connection = Connection(host, port, access_token)
    await connection.connect()

    return connection


@click.group()
@click.option("--debug/--no-debug", default=False)
@click.pass_context
async def main(ctx, debug):
    if debug:
        logging.basicConfig(level=logging.DEBUG)

    config = confuse.Configuration("happier", __name__)
    logger.debug("Config directory is: %s", config.config_dir())

    ctx.ensure_object(dict)
    ctx.obj["config"] = config


@main.command()
@click.argument("kind")
@click.argument("name")
@click.pass_context
async def get(ctx, kind, name):
    """Describe a Home Assistant resource as a manifest."""
    resource_cls = Resource.class_for_kind(kind)
    if not resource_cls:
        click.secho(f"Unknown kind {kind!r}", fg="red")
        return

    connection = await get_connection(ctx.obj["config"])

    try:
        area = resource_cls(connection, {})

        state = await area.get_remote()

        if not state:
            click.secho(f"Object {type}/{name} could not be found", fg="red")
            return
        click.echo(state)

    finally:
        await connection.close()


@main.command()
@click.argument("manifest", type=click.File("r"))
@click.pass_context
async def apply(ctx, manifest):
    """Apply a Home Assistant manifest"""
    connection = await get_connection(ctx.obj["config"])

    resources = load_manifests(connection, manifest)

    try:
        for resource in resources:
            await resource.apply()
    finally:
        await connection.close()


@main.command()
@click.argument("manifest", type=click.File("r"))
@click.pass_context
async def delete(ctx, manifest):
    """Delete a Home Assistant resource"""
    connection = await get_connection(ctx.obj["config"])

    resources = load_manifests(connection, manifest)

    try:
        for resource in resources:
            await resource.delete()
    finally:
        await connection.close()


if __name__ == "__main__":
    try:
        main(_anyio_backend="asyncio")

    except KeyboardInterrupt:
        pass

    except ManifestError as e:
        click.secho("Exiting due to an error with the supplied manifest", fg="red")
        click.echo(str(e))

    except HomeAssistantError as e:
        click.secho(
            "Exiting due to an error communicating with the Home Assistant instance",
            fg="red",
        )
        click.echo(str(e))

    except ApplicationError as e:
        click.secho("Exiting due to an error", fg="red")
        click.echo(str(e))
