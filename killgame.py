import discord, traceback
from mod import DispatchedBot
role_names = ['liv', 'ded', 'liv inactive', 'ded inactive']


class KillGame(DispatchedBot):
    def __init__(self, *args, **kwargs):
        self.roles = None
        super().__init__(*args, **kwargs)

    async def on_message(self, client: discord.Client, game_data,
                         message: discord.Message):
        try:
            if message.content.startswith('!shoot '):
                self.check_and_setup_roles(message)
                cmds = message.content.split(' ')
                if len(cmds) == 2 and len(message.mentions) == 1:
                    target = message.mentions[0]
                    await self.kill(client, message, game_data, message.author, target)
                else:
                    await client.send_message(message.channel, 'Proper usage: "!shoot @<name>"')
        except Exception as e:
            traceback.print_exc()

    async def replace_game_role(self, client, player, new_role, message):

        non_game_roles = [role for role in player.roles if role not in self.roles.values()]
        non_game_roles.append(new_role)

        await client.send_message(message.channel, f"```Successfully given user {str(player)} role {str(new_role)}.```")
        await client.delete_message(message)  # Done first to remove it asap
        await client.replace_roles(player, *non_game_roles)
        print(f'Player {player.nick} given role {new_role}')

    async def kill(self, client, message, game_data, killer, killed):

        if not self.roles['liv'] in killer.roles or self.roles['liv inactive'] in killer.roles:
            await client.send_message(message.channel, f"You're already dead -- you cant kill anyone.")
            return

        if not game_data.grab_user_value(killer.id, 'has_bullet'):
            await client.send_message(message.channel, 'You have already used your bullet.')
            return

        if not self.roles['liv'] in killed.roles or self.roles['liv inactive'] in killed.roles:
            await client.send_message(message.channel, f'{killed.nick} already dead.')
            return

        inactive = self.roles['liv inactive'] in killed.roles
        game_data.set_user_value(killer.id, 'has_bullet', False)
        non_game_roles = [role for role in killed.roles if role not in self.roles.values()]
        if inactive:
            non_game_roles.append(discord.utils.get(message.server.roles, name='ded inactive'))
        else:
            non_game_roles.append(discord.utils.get(message.server.roles, name='ded'))
        await client.replace_roles(killed, *non_game_roles)
        await client.send_message(message.channel, f'{killer.nick} has killed {killed.nick}.')

    def check_and_setup_roles(self, message):
        if self.roles is None:
            self.roles = {}
            for name in role_names:
                self.roles[name] = discord.utils.get(message.server.roles, name=name)
