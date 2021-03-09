import discord
from mod import DispatchedBot
MEME_CHANNELS = [433344731930689536]
# TEST_MEME_CHANNEL_ID = 448495055532195850
DOWNVOTE_BLOCKED_USERS = [192786036743602176]
UPVOTE_BLOCKED_USERS = []

# gives memes an 'upvote' and 'downvote' button, using reactions
# tracks karma to game_data[users][user_id][karma]
class MemeVoter(DispatchedBot):
    def __init__(self, *args, **kwargs):
        self.upvote = None
        self.downvote = None
        super().__init__(*args, **kwargs)

    # discovers the correct upvote and downvote emoji
    def setup_vote_emoji(self, message: discord.message.Message):
        if self.upvote is None:
            self.upvote = discord.utils.get(message.guild.emojis, name='upvote')
        if self.downvote is None:
            self.downvote = discord.utils.get(message.guild.emojis, name='downvote')

    # reacts with upvote and downvote if in meme channel (defined with global)
    async def on_message(self, client, game_data, message):
        if message.channel.id in MEME_CHANNELS:
            self.setup_vote_emoji(message)
            await message.add_reaction(self.downvote)
            await message.add_reaction(self.upvote)

    # gives 1 karma to the user who posted the meme, -1 if downvote
    async def on_reaction_add(self, client, game_data, reaction, user):
        if reaction.message.channel.id in MEME_CHANNELS and not user.bot and user.id != reaction.message.author.id:
            self.setup_vote_emoji(reaction.message)
            if reaction.emoji == self.upvote:
                if user.id not in UPVOTE_BLOCKED_USERS:
                    game_data.add_to_user_value(reaction.message.author.id, 'karma', 1)
                else:
                    await reaction.remove(user)
                    print(user.name, "blocked from upvoting")
            if reaction.emoji == self.downvote:
                if user.id not in DOWNVOTE_BLOCKED_USERS:
                    await game_data.add_to_user_value(reaction.message.author.id, 'karma', -1)
                else:
                    reaction.remove(user)
                    print(user.name, "blocked from downvoting")
    # gives -1 karma to the user who posted the meme, 1 if downvote
    # doesnt block banned users, cause removing their reactions is what we want anyway
    async def on_reaction_remove(self, client, game_data, reaction, user):
        if reaction.message.channel.id in MEME_CHANNELS and not user.bot and user.id != reaction.message.author.id:
            self.setup_vote_emoji(reaction.message)
            if reaction.emoji == self.upvote:
                game_data.add_to_user_value(reaction.message.author.id, 'karma', -1)
            if reaction.emoji == self.downvote:
                game_data.add_to_user_value(reaction.message.author.id, 'karma', 1)
