import discord, asyncio, json
from pathlib import Path
client = discord.Client()
MEME_CHANNEL_ID = '433344731930689536'
upvote = None
downvote = None
userfile = "users.txt"   
KEY_PATH = Path('../key.txt')

def init_user_in_dic(dic, userid):
    dic['users'][userid] = {}
    dic['users'][userid]['points'] = 0
    return dic

def get_userdata():
    with open(userfile, 'r') as f:
        return json.load(f)

def write_userdata(dic):
    with open(userfile, 'w') as f:
        json.dump(dic, f)

def add_user_point(userid, point):
    dic = get_userdata()
    if userid not in dic:
        dic = init_user_in_dic(dic, userid)
    dic['users'][userid]['points'] += point
    write_userdata(dic)

def get_user_points(dic, userid):
    dic = get_userdata()
    if userid not in dic:
        dic = init_user_in_dic(dic, userid)
    return dic['users'][userid]['points']

def setup_vote_emoji(message):
    global upvote, downvote
    if upvote == None:
            upvote = discord.utils.get(message.server.emojis, name='upvote')
    if downvote == None:
        downvote = discord.utils.get(message.server.emojis, name='downvote')

@client.event
async def on_ready():
    print('Online.')     

@client.event
async def on_message(message):
    setup_vote_emoji(message)
    if message.channel.id == MEME_CHANNEL_ID:
        await client.add_reaction(message, downvote)
        await client.add_reaction(message, upvote)

@client.event
async def on_reaction_add(reaction, user):
    if reaction.message.channel.id == MEME_CHANNEL_ID and not user.bot and user.id != reaction.message.author.id:
        setup_vote_emoji(reaction.message)
        if reaction.emoji == upvote:
            add_user_point(user.id, 1)
        if reaction.emoji == downvote:
            add_user_point(user.id, -1)

@client.event
async def on_reaction_remove(reaction, user):
    if reaction.message.channel.id == MEME_CHANNEL_ID and not user.bot and user.id != reaction.message.author.id:
        setup_vote_emoji(reaction.message)
        if reaction.emoji == upvote:
            add_user_point(reaction.message.author.id, -1)
        if reaction.emoji == downvote:
            add_user_point(reaction.message.author.id, 1)
with open(KEY_PATH, 'r') as f:
            key = f.readlines()[0]
            if key[-1] == '\n':
                key = key[:-1]
client.run(key)

