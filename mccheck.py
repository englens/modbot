import discord
import socket
from mod import DispatchedBot

IP_FILE = "../mc_server_ip.txt"

# Checks to see if the minecraft server is up
class MCCheck(DispatchedBot):
    def __init__(self, *args, **kwargs):
        self.help = "!server - check MC server status"
        self.server_ip = self.get_ip()
        super().__init__(*args, **kwargs)
    
    async def on_message(self, client, game_data, message):
        if message.content == '!server':
            try:
                with Client(SERVER_IP, 25565, timeout=1.5) as client:
                    fullstats = client.stats(full=True)
                if len(fullstats.players) > 0:
                    playerstr = "Players: " + ', '.join(fullstats.players)
                else:
                    playerstr = "No Players Online"
                infostr = "Server Online -- " + playerstr
            except socket.timeout as timeout:
                infostr = "Server Offline"

    def get_ip(self):
        with open(IP_FILE) as f:
            return str(f.read()) # idk if str is needed but dont feel like testing

