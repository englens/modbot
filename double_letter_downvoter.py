import discord
import re
from mod import DispatchedBot

# Detects messages with double letters or apostrophes and downvotes them
class DoubleLetterDownvoter(DispatchedBot):
    def __init__(self, *args, **kwargs):
        self.downvote = None
        super().__init__(*args, **kwargs)

    # Discovers the downvote emoji from the guild
    def setup_downvote_emoji_if_unset(self, message: discord.message.Message):
        if self.downvote is None:
            self.downvote = discord.utils.get(message.guild.emojis, name='downvote')

    # Checks if message contains double letters (consecutive repeated letters)
    def has_double_letters(self, text: str) -> bool:
        # Pattern to match any letter repeated consecutively (case-insensitive)
        pattern = r'([a-zA-Z])\1'
        return bool(re.search(pattern, text))

    # Checks if message contains apostrophes
    def has_apostrophe(self, text: str) -> bool:
        return "'" in text

    # Reacts with downvote if message has double letters or apostrophes
    async def on_message(self, client, game_data, message):
        # Ignore bot messages
        if message.author.bot:
            return

        # Check if message has double letters or apostrophes
        if self.has_double_letters(message.content) or self.has_apostrophe(message.content):
            self.setup_downvote_emoji_if_unset(message)
            if self.downvote:
                await message.add_reaction(self.downvote)
