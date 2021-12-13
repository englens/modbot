import discord
from mod import DispatchedBot
MEME_CHANNELS = [433344731930689536]
# TEST_MEME_CHANNEL_ID = 448495055532195850
#DOWNVOTE_BLOCKED_USERS = [192786036743602176]  # cav
DOWNVOTE_BLOCKED_USERS = []
UPVOTE_BLOCKED_USERS = []

# gives memes an 'upvote' and 'downvote' button, using reactions
# tracks karma to game_data[users][user_id][karma]
class MemeVoter(DispatchedBot):
    def __init__(self, *args, **kwargs):
        self.upvote = None
        self.downvote = None
        super().__init__(*args, **kwargs)

    # discovers the correct upvote and downvote emoji
    def setup_vote_emoji_if_unset(self, message: discord.message.Message):
        if self.upvote is None:
            self.upvote = discord.utils.get(message.guild.emojis, name='upvote')
        if self.downvote is None:
            self.downvote = discord.utils.get(message.guild.emojis, name='downvote')

    # reacts with upvote and downvote if in meme channel (defined with global)
    async def on_message(self, client, game_data, message):
        if message.channel.id in MEME_CHANNELS:
            self.setup_vote_emoji_if_unset(message)
            await message.add_reaction(self.downvote)
            await message.add_reaction(self.upvote)
    """
    # gives 1 karma to the user who posted the meme, -1 if downvote
    async def on_reaction_add(self, client, game_data, reaction, user):
        if reaction.message.channel.id in MEME_CHANNELS and not user.bot and user.id != reaction.message.author.id:
            self.setup_vote_emoji_if_unset(reaction.message)
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
                    await reaction.remove(user)
                    print(user.name, "blocked from downvoting")
                    
    # gives -1 karma to the user who posted the meme, 1 if downvote
    # doesnt block banned users, cause removing their reactions is what we want anyway
    async def on_reaction_remove(self, client, game_data, reaction, user):
        if reaction.message.channel.id in MEME_CHANNELS and user.id != client.id and user.id != reaction.message.author.id:
            self.setup_vote_emoji_if_unset(reaction.message)
            if reaction.emoji == self.upvote:
                game_data.add_to_user_value(reaction.message.author.id, 'karma', -1)
            if reaction.emoji == self.downvote:
                game_data.add_to_user_value(reaction.message.author.id, 'karma', 1)
    """

    # Payload: 
    """discord.RawReactionActionEvent : 
            channel_id
            emoji
            event_type
            guild_id
            member
            message_id
            user_id"""

    async def get_message_object_from_payload(client: discord.Client, payload: discord.RawReactionActionEvent):
        msg_id = payload.message_id
        channel_id = payload.channel_id
        channel: discord.TextChannel = await client.fetch_channel(channel_id)
        return await channel.fetch_message(msg_id)


    async def on_raw_reaction_add(self, client, game_data, payload: discord.RawReactionActionEvent):
        print('got reaction event')
        user = payload.member
        msg : discord.Message = await self.get_message_object_from_payload(client, payload)
        if msg.channel.id in MEME_CHANNELS and user.id != client.id and user.id != msg.author.id:
            if payload.emoji == self.upvote:
                if user.id not in UPVOTE_BLOCKED_USERS:
                    game_data.add_to_user_value(msg.author.id, 'karma', 1)
                else:
                    await msg.remove_reaction(user)
                    print(user.name, "blocked from upvoting")
            if payload.emoji == self.downvote:
                if user.id not in DOWNVOTE_BLOCKED_USERS:
                    await game_data.add_to_user_value(msg.author.id, 'karma', -1)
                else:
                    await msg.remove_reaction(user)
                    print(user.name, "blocked from downvoting")


    async def on_raw_reaction_remove(self, client, game_data, payload: discord.RawReactionActionEvent):
        user = payload.member
        msg : discord.Message = await self.get_message_object_from_payload(client, payload)
        
        if msg.channel.id in MEME_CHANNELS and user.id != client.id and user.id != msg.author.id:
            self.setup_vote_emoji_if_unset(msg)
            if payload.emoji == self.upvote:
                game_data.add_to_user_value(msg.author.id, 'karma', -1)
            if payload.emoji == self.downvote:
                game_data.add_to_user_value(msg.author.id, 'karma', 1)