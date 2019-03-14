import discord
from mod import DispatchedBot
MEME_CHANNELS = ['433344731930689536', '555510883887874050']
# TEST_MEME_CHANNEL_ID = '448495055532195850'


# gives memes an 'upvote' and 'downvote' button, using reactions
# tracks karma to game_data[users][user_id][karma]
class MemeUpvoter(DispatchedBot):
    def __init__(self, *args, **kwargs):
        self.upvote = None
        self.downvote = None
        super().__init__(*args, **kwargs)

    # discovers the correct upvote and downvote emoji
    def setup_vote_emoji(self, message: discord.message.Message):
        if self.upvote is None:
            self.upvote = discord.utils.get(message.server.emojis, name='upvote')
        if self.downvote is None:
            self.downvote = discord.utils.get(message.server.emojis, name='downvote')

    # reacts with upvote and downvote if in meme channel (defined with global)
    async def on_message(self, client, game_data, message):
        if message.channel.id in MEME_CHANNELS:
            self.setup_vote_emoji(message)
            await client.add_reaction(message, self.downvote)
            await client.add_reaction(message, self.upvote)

    # gives 1 karma to the user who posted the meme, -1 if downvote
    async def on_reaction_add(self, client, game_data, reaction, user):
        if reaction.message.channel.id in MEME_CHANNELS and not user.bot and user.id != reaction.message.author.id:
            self.setup_vote_emoji(reaction.message)
            if reaction.emoji == self.upvote:
                game_data.add_to_user_value(reaction.message.author.id, 'karma', 1)
            if reaction.emoji == self.downvote:
                game_data.add_to_user_value(reaction.message.author.id, 'karma', -1)

    # gives -1 karma to the user who posted the meme, 1 if downvote
    async def on_reaction_remove(self, client, game_data, reaction, user):
        if reaction.message.channel.id in MEME_CHANNELS and not user.bot and user.id != reaction.message.author.id:
            self.setup_vote_emoji(reaction.message)
            if reaction.emoji == self.upvote:
                game_data.add_to_user_value(reaction.message.author.id, 'karma', -1)
            if reaction.emoji == self.downvote:
                game_data.add_to_user_value(reaction.message.author.id, 'karma', 1)