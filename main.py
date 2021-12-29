import mod
import discord
from meme_voter import MemeVoter
from karma_checker import KarmaChecker
from freebie_karma import FreebieKarma
from rolegiver import RoleGiver
from manual_mode import ManualMode
from leaderboard import KarmaLeaderboard
from rpsgame import RPSWorld

from music_kirbyer import MusicKirbyer
# ---- Disabled bot imports ----
#from dungeon import Dungeon
#from mccheck import MCCheck
#from killgame import KillGame
#from rolegiver_alternate import RoleGiverAlternate
#from tts import TTSBot

from pathlib import Path
ADD_IN_FILE = './add_ins/add_ins.json'
ADD_IN_PATH = Path('./add_ins/')
KEY_PATH = Path('../modkey.txt')
DATA_FILE = 'users.txt'

# allows us to read member lists
intents = discord.Intents.default()
intents.members = True


# returns the list of add_in classes
# def get_add_ins(path):
#     with open(path, 'r') as f:
#         add_ins =  json.load(f)['add_ins']
#         for add_in in add_ins:
#             exec(f'import {add_in["filename"]}')


# reads the key from the specified key file
def get_key(key_path):
    with open(key_path, 'r') as f:
        key = f.readlines()[0]
    if key[-1] == '\n':
        key = key[:-1]
    return key


if __name__ == "__main__":
    client = discord.Client(intents=intents)
    bot = mod.GeneralBot(DATA_FILE, client)

    # ----- Start bots here -----
    # Command help text is displayed in this order
    MemeVoter(bot)
    KarmaChecker(bot)
    FreebieKarma(bot)
    #RoleGiver(bot)
    ManualMode(bot)
    KarmaLeaderboard(bot)
    MusicKirbyer(bot)
    RPSWorld(bot)
    #TTSBot(bot)
    #MCCheck(bot)
    #Dungeon(bot)
    # ----------------------
    client.run(get_key(KEY_PATH))
