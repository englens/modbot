import discord
from mod import DispatchedBot


class TestBot(DispatchedBot):
    async def on_message(self, client: discord.Client, game_data,
                         message: discord.Message):
        print(message.content)
