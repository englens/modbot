import discord
from mod import DispatchedBot


# gives memes an 'upvote' and 'downvote' button, using reactions
# tracks karma to game_data[users][user_id][karma]
class KarmaLeaderboard(DispatchedBot):
    def __init__(self, *args, **kwargs):
        self.upvote = None
        self.downvote = None
        super().__init__(*args, **kwargs)

    # reacts with upvote and downvote if in meme channel (defined with global)
    async def on_message(self, client, game_data, message):
        if message.content.startswith('!leaderboard'):
            # Only get users with karma
            members = []
            for i in game_data.get_all_user_ids():
                u = discord.utils.get(message.server.members, id=i)
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
                lines.append(f'{i+1}) {user_scores[i][0]}')
            max_len = max([len(x) for x in lines])
            for i in range(5):
                msg += lines[i] + ' ' + ' '*(max_len - len(lines[i])) + '| ' + str(round(user_scores[i][1], 2)) + '\n'
            msg += '```'
            await client.send_message(message.channel, msg)
