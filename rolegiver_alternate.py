import discord, traceback
from mod import DispatchedBot
role_names = ['red', 'green', 'yellow', 'brown']


class RoleGiverAlternate(DispatchedBot):
    def __init__(self, *args, **kwargs):
        self.roles = None
        super().__init__(*args, **kwargs)

    async def on_message(self, client: discord.Client, game_data,
                         message: discord.Message):
        try:
            if message.content[:10] == '!giverole ':
                self.check_and_setup_roles(message)
                cmds = message.content.split(' ')[1:]
                if len(cmds) == 2 and cmds[1] in role_names:
                    #check if ping
                    if len(message.mentions) == 1:
                        target = message.mentions[0]
                        if target is not message.author:
                            await self.replace_game_role(client, target, self.roles[cmds[1]])
                        return
                    member = discord.utils.get(message.server.members, id=cmds[0])
                    if member is not None and member is not message.author:
                        await self.replace_game_role(client, member, self.roles[cmds[1]])
                        return
        except Exception as e:
            traceback.print_exc()

    async def replace_game_role(self, client, player, new_role):
        non_game_roles = [role for role in player.roles if role not in self.roles]
        await client.replace_roles(player, non_game_roles.append(new_role))
        print(f'Player {player.nick} given role {new_role}')

    def check_and_setup_roles(self, message):
        if self.roles is None:
            self.roles = {}
            for name in role_names:
                self.roles[name] = discord.utils.get(message.server.roles, name=name)