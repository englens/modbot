import discord
from mod import DispatchedBot


class KarmaChecker(DispatchedBot):
    def __init__(self, *args, **kwargs):
        help = "!karma <@user> -- fetches the current karma of a user"
        super().__init__(helpstr=help, *args, **kwargs)
    async def on_message(self, client: discord.Client, game_data,
                         message: discord.Message):
        if message.content[:7] == '!karma ':
            for mentioned_user in message.mentions:
                await message.channel.send(self.form_karma_string(mentioned_user, game_data))

    @staticmethod
    def form_karma_string(user, data):
        karma = round(data.grab_user_value(user.id, 'karma'), 2)
        return f'Karma for user *{user.name}*: {karma}'
