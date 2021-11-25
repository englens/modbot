import discord
from mod import DispatchedBot


# Displays a list of the top highest karma users
class KarmaLeaderboard(DispatchedBot):
    def __init__(self, *args, **kwargs):
        self.upvote = None
        self.downvote = None
        help = '!leaderboard -- Display the 5 users with the highest karma'
        super().__init__(helpstr=help, *args, **kwargs)

    # reacts with upvote and downvote if in meme channel (defined with global)
    async def on_message(self, client, game_data, message):
        if message.content.startswith('!leaderboard'):
            # Only get users with karma
            members = []
            for i in game_data.get_all_user_ids():
                u = discord.utils.get(message.guild.members, id=i)
                if u is not None:
                    members.append(u)

            # get tuples of (name, karma)
            user_scores = []
            for user in members:
                if user.nick is None:
                    nam = user.name
                else:
                    nam = user.nick
                user_scores.append((nam, game_data.grab_user_value(user.id, 'karma')))

            # order by karma
            user_scores = sorted(user_scores, key=lambda x: -x[1])

            # make the msg, add the top 5
            msg = '```----------Karma Leaderboard----------\n'
            lines = []
            for i in range(5):
                try:
                    lines.append(f'{i+1}) {deEmojify(user_scores[i][0])}')
                except IndexError:
                    print(f"Less than 5 users. Stopping at {i}")
                    if i == 0:
                        message.channel.send("Error: No users with karma currently!")
                        return
            max_len = max([len(x) for x in lines])
            for i, line in enumerate(lines):
                msg += line + ' ' + ' '*(max_len - len(line)) + '| ' + str(round(user_scores[i][1], 2)) + '\n'
            msg += '```'
            await message.channel.send(msg)


def deEmojify(inputString):
    """from https://stackoverflow.com/questions/33404752/removing-emojis-from-a-string-in-python"""
    return inputString.encode('ascii', 'ignore').decode('ascii')

