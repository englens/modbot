import re
import discord
from mod import DispatchedBot
MUSIC_CHANNEL = [451068243235307532]


def is_valid_music_link(msg):
    return re.match(r'.*https:\/\/www\.youtube\.com\/watch.*', msg) is not None
    
    
class MusicKirbyer(DispatchedBot):
    def __init__(self, *args, **kwargs):
        self.kirby = None
        super().__init__(*args, **kwargs)
        
    # discovers the correct upvote and downvote emoji
    def setup_kirby(self, message: discord.message.Message):
        if self.kirby is None:
            self.kirby = discord.utils.get(message.guild.emojis, name='kirbyjam')
            
    # reacts with upvote and downvote if in meme channel (defined with global)
    async def on_message(self, client, game_data, message):
        if message.channel.id in MUSIC_CHANNEL and is_valid_music_link(message.content):
            self.setup_kirby(message)
            await message.add_reaction(self.kirby)
            print(f"User {message.user.id} posted new music.")

    # gives 1 music point to the user who posted the song
    async def on_reaction_add(self, client, game_data, reaction, user):
        if reaction.message.channel.id in MUSIC_CHANNEL and not user.bot and user.id != reaction.message.author.id:
            self.setup_kirby(reaction.message)
            if reaction.emoji == self.kirby:
                game_data.add_to_user_value(reaction.message.author.id, 'music points', 1)

    # gives -1 music point to the user who posted the song
    async def on_reaction_remove(self, client, game_data, reaction, user):
        if reaction.message.channel.id in MUSIC_CHANNEL and not user.bot and user.id != reaction.message.author.id:
            self.setup_kirby(reaction.message)
            if reaction.emoji == self.kirby:
                game_data.add_to_user_value(reaction.message.author.id, 'music points', -1)