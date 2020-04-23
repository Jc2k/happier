import asyncio
import ssl
import json
import logging

import asyncws
import confuse

from .connection import Connection
from .resources.area import Area

logger = logging.getLogger(__name__)


async def main():
    logging.basicConfig(level=logging.DEBUG)

    config = confuse.Configuration("happier", __name__)
    logger.debug("Config directory is: %s", config.config_dir())

    host = config["default"]["host"].get(str)
    port = config["default"]["port"].get(int)
    access_token = config["default"]["access_token"].get(str)

    connection = Connection(host, port, access_token)
    await connection.connect()

    area = Area(connection, name="Test 1")
    await area.delete()

    print(await area.get_remote())
    await area.create()
    print(await area.get_remote())
    await area.delete()
    print(await area.get_remote())

    await connection.close()


if __name__ == "__main__":
    asyncio.run(main())

