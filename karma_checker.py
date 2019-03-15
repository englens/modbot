import discord
from mod import DispatchedBot


class KarmaChecker(DispatchedBot):
    async def on_message(self, client: discord.Client, game_data,
                         message: discord.Message):
        if message.content[:7] == '!karma ':
            for mentioned_user in message.mentions:
                await client.send_message(message.channel, self.form_karma_string(mentioned_user, game_data))

    @staticmethod
    def form_karma_string(user, data):
        karma = data.grab_user_value(user.id, 'karma')
        return f'Karma for User {user.name}: {karma}'