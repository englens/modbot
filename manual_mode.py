import discord
from mod import DispatchedBot
command_channel_id = '599484428296650772'
send_to_channel_id = '184877960694726656'


class ManualMode(DispatchedBot):
    def __init__(self, *args, **kwargs):
        self.roles = None
        super().__init__(*args, **kwargs)
        self.command_channel = None
        self.send_to_channel = None
        self.roles_filled = False

    async def get_channels(self, client):
        if self.command_channel is None:
            self.command_channel = await discord.utils.get(client.get_all_channels, id=command_channel_id)
        if self.send_to_channel is None:
            self.send_to_channel = await discord.utils.get(client.get_all_channels, id=send_to_channel_id)
        self.roles_filled = True
    async def on_message(self, client: discord.Client, game_data,
                         message: discord.Message):
        if not self.roles_filled:
            await self.get_channels(client)
        if message.channel == self.command_channel:
            await client.send_message(self.send_to_channel, message.content)

