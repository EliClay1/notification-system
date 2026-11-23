import pytest
from channels.testing import WebsocketCommunicator

from project.asgi import application


@pytest.mark.asyncio
class TestWebsocket:
    async def test_connection(self):
        communicator = WebsocketCommunicator(application, "/ws/notifications/")

        try:
            connected, _subprotocol = await communicator.connect()
            assert connected is True

            welcome_message = await communicator.receive_from()
            assert welcome_message == "[Welcome Anonymous!]"
        finally:
            await communicator.disconnect()
