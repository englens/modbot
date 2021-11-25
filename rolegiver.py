import discord
from mod import DispatchedBot

# Allows users to give themselves a role based on the list of allowed roles
# Optionaly they arn't allowed to change their role once they have one
class RoleGiver(DispatchedBot):
    allow_replace = True
    role_names = ['cringe', 'based']

    def __init__(self, *args, **kwargs):
        self.roles = None
        help = '!role <rolename> --- assign yourself a role from the list'
        help += f'    current valid roles: {RoleGiver.role_names}'
        super().__init__(helpstr=help, *args, **kwargs)

    # Checks if user has a role on the role list, and gives them the role and replaces it if necessary
    async def on_message(self, client: discord.Client, game_data,
                         message: discord.Message):
        if message.content[:6] == '!role ':
            self.setup_roles(message)

            cmd_name = message.content[6:]
            try:
                new_role = self.roles[cmd_name]
            except KeyError:
                await message.channel.send('Invalid Role.')
                return

            non_game_roles = [role for role in message.author.roles if role not in self.roles.values()]
            non_game_roles.append(new_role)

            # Role is valid
            if cmd_name in self.role_names:
                if self.allow_replace or frozenset(self.roles.values()).isdisjoint(frozenset(message.author.roles)):
                    await message.author.edit(roles=non_game_roles)
                    await message.channel.send('Role given.')

    def setup_roles(self, message):
        if self.roles is None:
            self.roles = {}
            for name in self.role_names:
                self.roles[name] = discord.utils.get(message.guild.roles, name=name)