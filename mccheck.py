import discord
import re
import requests
from mod import DispatchedBot

SERVER_URL_FILE = "../mc_server_ip.txt"

# Checks to see if the minecraft server is up
class MCCheck(DispatchedBot):

    def replace_brs(self, txt: str) -> str:
        return re.sub('<[^<]+?>', '', txt)

    def __init__(self, *args, **kwargs):
        self.help = "!server - check MC server status"
        self.server_url = self.read_server_file()
        super().__init__(*args, **kwargs)
    
    async def on_message(self, client, game_data, message):
        if message.content == '!server':
            try:
                print('calling to server:', self.server_url)
                r = requests.get(self.server_url)
                response_text = self.replace_brs(r.text)
                await message.channel.send('```'+response_text+'```')
            except requests.exceptions.ConnectionError as timeout:
                await message.channel.send("```Err: Server status URL failed to respond.```")
            

    def read_server_file(self):
        with open(SERVER_URL_FILE) as f:
            return str(f.read()) # idk if str is needed but dont feel like testing

