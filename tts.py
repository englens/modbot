import discord
from mod import DispatchedBot

import os
import random
import re
import urllib.request
import urllib.parse

regex = r"\s*!voice -(angry|whispering|conversational|flirty|flustered|happy|narriation|sad|scared) (.+)"
styles=['angry', 'whispering', 'conversational', 'flirty', 'flustered', 
        'happy', 'narriation', 'sad', 'scared']

# gives memes an 'upvote' and 'downvote' button, using reactions
# tracks karma to game_data[users][user_id][karma]
class TTSBot(DispatchedBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    async def form_url(self, text, style):
        url = r'https://www.voicery.com/api/generate?text='
        url += urllib.parse.quote(text)
        url += f'&speaker=katie&style={style}&ssml=false'
        return url
    
    async def download_file(self, url):
        return urllib.request.urlretrieve(url, filename='./generate.mp3')
        
    # reacts with upvote and downvote if in meme channel (defined with global)
    async def on_message(self, client, game_data, message):
        if message.content[:7] == '!voice ':
            if message.content in ['!voice -h', '!voice -help']:
                await message.channel.send('"!voice [-style] message"\nStyles: angry, whispering, conversational, flirty, flustered, happy, narriation, sad, scared')
                return
            if match := re.fullmatch(regex, message.content):
                txt = match.groups()[1]
                emote = match.groups()[0]
            else:
                txt = message.content[7:]
                emote = random.choice(styles)
            url = await self.form_url(txt, emote)
            try:
                filename, _ = await self.download_file(url)
            except urllib.error.HTTPError:
                await message.channel.send('Error: HTTP Failed (server mad at us?)')
                working = False
                return
            await message.channel.send(file=discord.File(filename))
            os.remove(filename)  # no reason to keep it around


