import mod
import discord
from meme_upvoter import MemeUpvoter
from karma_checker import KarmaChecker


from pathlib import Path
ADD_IN_FILE = 'add_ins.json'
KEY_PATH = Path('../modkey.txt')
DATA_FILE = 'users.txt'


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


def main():
    client = discord.Client()
    bot = mod.GeneralBot(DATA_FILE, client)

    # ---Start bots here ---
    MemeUpvoter(bot)
    KarmaChecker(bot)
    # ----------------------
    client.run(get_key(KEY_PATH))


if __name__ == "__main__":
    main()