import discord
from mod import DispatchedBot
role_names = ['red', 'green', 'yellow', 'brown']


class RoleGiver(DispatchedBot):
    def __init__(self, *args, **kwargs):
        self.roles = None
        super().__init__(*args, **kwargs)

    async def on_message(self, client: discord.Client, game_data,
                         message: discord.Message):
        if message.content[:6] == '!role ':
            if self.roles is None:
                self.roles = {}
                for name in role_names:
                    self.roles[name] = discord.utils.get(message.server.roles, name=name)

            user_roles = message.author.roles
            cmd_name = message.content[6:]
            # Role is valid, and user has no role
            if cmd_name in self.roles and frozenset(self.roles.values()).isdisjoint(frozenset(user_roles)):
                # give the role
                await client.add_roles(message.author, self.roles[cmd_name])
                print(f'User {message.author.name} given role' + cmd_name)
                await client.send_message(message.channel, 'Role given.')
