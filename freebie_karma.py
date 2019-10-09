import discord
from mod import DispatchedBot, GameData
message_freebie_amt = 0.1
reaction_freebie_amt = 0.1


# gives users small amounts of karma for doing things
class FreebieKarma(DispatchedBot):
    async def on_message(self, client: discord.Client, game_data,
                         message: discord.Message):
        game_data.add_to_user_value(message.author.id, "karma", message_freebie_amt)

    async def on_reaction_add(self, client: discord.Client, game_data: GameData,
                              reaction: discord.Reaction, user: discord.User):
        game_data.add_to_user_value(user.id, "karma", reaction_freebie_amt)

    async def on_reaction_remove(self, client: discord.Client, game_data: GameData,
                                 reaction: discord.Reaction, user: discord.User):
        game_data.add_to_user_value(user.id, "karma", -reaction_freebie_amt)
