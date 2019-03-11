import mod
from meme_upvoter import MemeUpvoter
import discord
from pathlib import Path
KEY_PATH = Path('../modkey.txt')
DATA_FILE = "users.txt"


def get_key(key_path):
    with open(key_path, 'r') as f:
        key = f.readlines()[0]
    if key[-1] == '\n':
        key = key[:-1]
    return key


def main():
    client = discord.Client()
    bot = mod.GeneralBot(DATA_FILE, client)
    MemeUpvoter(bot)
    client.run(get_key(KEY_PATH))


if __name__ == "__main__":
    main()
