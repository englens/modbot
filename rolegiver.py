import discord
from mod import DispatchedBot


class RoleGiver(DispatchedBot):
    def __init__(self, *args, **kwargs):
        self.loli = None
        self.shouta = None
        super().__init__(*args, **kwargs)

    async def on_message(self, client: discord.Client, game_data,
                         message: discord.Message):
        if self.loli is None:
            self.loli = discord.utils.get(message.server.roles, name='loli')
        if self.shouta is None:
            self.shouta = discord.utils.get(message.server.roles, name='shouta')
        if message.content[:6] == '!role ':
            user_roles = message.author.roles
            if not (self.loli in user_roles and self.shouta in user_roles):
                if message.content[6:] == 'loli':
                    await client.add_roles(message.author, self.loli)
                    print(f'User {message.author.name} given role Loli')
                    await client.send_message(message.channel, 'Role given.')
                if message.content[6:] == 'shouta':
                    await client.add_roles(message.author, self.shouta)
                    print(f'User {message.author.name} given role Shouta')
                    await client.send_message(message.channel, 'Role given.')
