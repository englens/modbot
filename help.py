import discord
from mod import DispatchedBot

# Shows a list of all the commands and their descriptions
class Help(DispatchedBot):
    def __init__(self, *args, **kwargs):
        help = "!help - displays this message"
        super().__init__(helpstr=help, *args, **kwargs)
    
    async def on_message(self, client, game_data, message):
        if message.content == '!help':
            help = await self.get_help_string()
            await message.channel.send(help)
