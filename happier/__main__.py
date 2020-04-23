import asyncio
import ssl
import json
import logging

import asyncws
import confuse
import asyncclick as click

from .connection import Connection
from .resources.area import Area

logger = logging.getLogger(__name__)

from functools import wraps

def coro(f):
    # Click doesn't support async properly, which is annoying
    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper


async def get_connection(config):
    host = config["default"]["host"].get(str)
    port = config["default"]["port"].get(int)
    access_token = config["default"]["access_token"].get(str)

    connection = Connection(host, port, access_token)
    await connection.connect()

    return connection


@click.group()
@click.pass_context
async def main(ctx):
    logging.basicConfig(level=logging.DEBUG)

    config = confuse.Configuration("happier", __name__)
    logger.debug("Config directory is: %s", config.config_dir())

    ctx.ensure_object(dict)
    ctx.obj['config'] = config


@main.command()
@click.argument("type")
@click.argument("name")
@click.pass_context
async def get(ctx, type, name):
    """Describe a Home Assistant resource as a manifest."""
    connection = await get_connection(ctx.obj['config'])
    try:
        area = Area(connection, name=name)
        state = await area.get_remote()
        if not state:
            click.secho(f"Object {type}/{name} could not be found", fg="red")
            return
        click.echo(state)

    finally:
        await connection.close()


@main.command()
@click.pass_context
async def apply(ctx):
    """Apply a Home Assistant manifest"""
    connection = await get_connection(ctx.obj['config'])
    try:
        area = Area(connection, name="Test 1")

        if not await area.get_remote():
            logger.info("Creating area %s", "Test 1")
            await area.create()
    finally:
        await connection.close()


@main.command()
@click.argument("type")
@click.argument("name")
@click.pass_context
async def delete(ctx, type, name):
    """Delete a Home Assistant resource"""
    connection = await get_connection(ctx.obj['config'])
    try:
        area = Area(connection, name=name)
        if await area.delete():
            click.secho(f"{type}/{name} was removed.", fg="green")
            return
    finally:
        await connection.close()


if __name__ == "__main__":
    main(_anyio_backend="asyncio")
