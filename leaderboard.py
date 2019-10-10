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
            user_scores = []
            for user in message.server.members:
                user_scores.append((user.name, game_data.grab_user_value(user.id, 'karma')))
            user_scores = sorted(user_scores, key=lambda x: x[1])
            msg = '```----------Karma Leaderboard----------\n'
            lines = []
            for i in range(5):
                lines.append(f'{i}) {user_scores[i][0]} - ')
            max_len = max([len(x) for x in lines])
            for i in range(5):
                msg += ' '*(max_len - len(lines[i])) + str(user_scores[i][1]) + '\n'
            msg.append('```')
            print(msg)

    def get_all_karma(self, message, data):
