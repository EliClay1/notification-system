"""
Websocket Consumer
"""

import logging

from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.username = "Anonymous"
        await self.accept()
        await self.send(text_data=f"[Welcome {self.username}!]")

    async def receive(self, text_data=None, bytes_data=None):
        receival_message = "Recieved: "
        if text_data:
            receival_message += f"text => {text_data} "
        if bytes_data:
            receival_message += f"data => {bytes_data} "

        logger.info(receival_message)

    async def disconnect(self, close_code):
        # Called when connection is closed.
        logger.info(
            f"Connection closed: {close_code}" if close_code else "Connection closed."
        )
