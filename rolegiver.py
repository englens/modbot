import discord
from mod import DispatchedBot
loliname = 'reddit'
shoutaname = '4chan'


class RoleGiver(DispatchedBot):
    def __init__(self, *args, **kwargs):
        self.loli = None
        self.shouta = None
        super().__init__(*args, **kwargs)

    async def on_message(self, client: discord.Client, game_data,
                         message: discord.Message):
        if self.loli is None:
            self.loli = discord.utils.get(message.server.roles, name=loliname)
        if self.shouta is None:
            self.shouta = discord.utils.get(message.server.roles, name=shoutaname)
        if message.content[:6] == '!role ':
            user_roles = message.author.roles
            if not (self.loli in user_roles and self.shouta in user_roles):
                if message.content[6:] == loliname:
                    await client.add_roles(message.author, self.loli)
                    print(f'User {message.author.name} given role' + loliname)
                    await client.send_message(message.channel, 'Role given.')
                if message.content[6:] == shoutaname:
                    await client.add_roles(message.author, self.shouta)
                    print(f'User {message.author.name} given role' + shoutaname)
                    await client.send_message(message.channel, 'Role given.')
