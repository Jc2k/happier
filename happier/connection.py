import asyncio
import json
import ssl

import asyncws

from .exceptions import AuthenticationError, HomeAssistantError

ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE


class Connection:
    def __init__(self, address, port, access_token):
        self.address = address
        self.port = port
        self.access_token = access_token

        self._ws = None
        self._call_count = 0
        self._active_calls = {}
        self._dispatcher_task = None

    async def _recv(self):
        payload = await self._ws.recv()
        if not payload:
            return None
        return json.loads(payload)

    async def _dispatcher(self):
        try:
            msg = await self._recv()
            while msg:
                if msg["type"] == "result":
                    future = self._active_calls.pop(msg["id"], None)
                    if not future:
                        continue
                    if not msg["success"]:
                        future.set_exception(HomeAssistantError(msg["error"]))
                    future.set_result(msg["result"])
                else:
                    print(msg)

                msg = await self._recv()
        except asyncio.CancelledError:
            pass

    async def send(self, **payload):
        await self._ws.send(json.dumps(payload))

    async def call(self, _call_type, **kwargs):
        """Call a WS endpoint and wait for the result."""
        self._call_count += 1
        future = self._active_calls[self._call_count] = asyncio.Future()
        await self.send(id=self._call_count, type=_call_type, **kwargs)
        return await future

    async def connect(self):
        """Connect and authenticate against a WS instance."""
        self._ws = await asyncws.connect(
            f"wss://{self.address}:{self.port}/api/websocket", ssl=ssl_context
        )

        # On connect HA will send auth_required. Can't do anything yet.
        msg = await self._recv()
        assert msg["type"] == "auth_required"

        await self.send(type="auth", access_token=self.access_token)

        msg = await self._recv()
        if msg["type"] == "auth_invalid":
            raise AuthenticationError("Invalid auth token")

        if msg["type"] != "auth_ok":
            raise HomeAssistantError(f"Unexpected message: {msg!r}")

        self._dispatcher_task = asyncio.ensure_future(self._dispatcher())

    async def close(self):
        self._dispatcher_task.cancel()
        await self._dispatcher_task
