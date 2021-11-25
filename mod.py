import json
import discord
import sqlite3


# handles getting of user information, and storing updates automatically
# if called for a unregistered user, init them
class GameData:
    def __init__(self, data_file_path):
        self.file = data_file_path
        self.dic = {}
        self.load_from_file()  # updates self.dic

    # read userdata from file. Only do this when class created.
    def load_from_file(self):
        with open(self.file, 'r') as f:
            self.dic = json.load(f)

    # save userdata to file
    # this is called after every change
    def save(self):
        with open(self.file, 'w') as f:
            json.dump(self.dic, f)

    # creates game data for user, based on dic[users][default]
    def init_user(self, user_id_str):
        self.dic['users'][user_id_str] = self.dic['users']['default'].copy()
        self.save()
        
    # internal function to create a new value for a user who doesnt have it filled yet
    def init_val(self, user_id_str, valname):
        try:
            self.dic['users'][user_id_str][valname] = self.dic['users']['default'][valname]
        except Exception:
            self.init_user(user_id_str)
        self.save()
        
    # returns list of all ids present in userdata
    def get_all_user_ids(self):
        ids = [int(k) for k in self.dic['users'].keys() if k != 'default']
        return ids
        
    # returns the value of given user value
    def grab_user_value(self, user_id, value_name):
        id_str = str(user_id)
        if id_str not in self.dic['users']:
            self.init_user(id_str)
        try:
            return self.dic['users'][id_str][value_name]
        except KeyError:
            self.init_val(id_str, value_name)
            return self.dic['users'][id_str][value_name]
    
    # Add value to (rather than replace) a user value
    def add_to_user_value(self, user_id, value_name, amount):
        id_str = str(user_id)
        try:
            self.dic['users'][id_str][value_name] += amount
        except KeyError:
            if id_str not in self.dic['users']:
                self.init_user(id_str)
            self.dic['users'][id_str][value_name] = amount
        print(f'user {user_id} gained {amount} {value_name}. Now {self.dic["users"][id_str][value_name]}.')
        self.save()
        
    # replace the value of a user value -- inits it if needed
    def set_user_value(self, user_id, value_name, new_val):
        id_str = str(user_id)
        try:
            self.dic['users'][id_str][value_name] = new_val
        except KeyError:
            if id_str not in self.dic['users']:
                self.init_user(id_str)
            self.dic['users'][id_str][value_name] = new_val
        print(f'{value_name} set to {new_val} for {id_str}.')
        self.save()


# General bot that holds a discord bot client.
# holds a data file, and handles custom bot events.
class GeneralBot:
    def __init__(self, game_data_file, client):
        super().__init__()
        self.client = client  # discord.py bot client
        self.game_data = GameData(game_data_file)
        self.handler_dispatcher = GameEventHandlerDispatcher()
        self.help = '---- Command List ----\n'

        # --- client events ---
        @client.event
        async def on_ready():
            print('Connected.')
            await self.call_event('on_ready')

        @client.event
        async def on_message(message):
            await self.call_event('on_message', message)

        @client.event
        async def on_reaction_add(reaction, user):
            await self.call_event('on_reaction_add', reaction, user)

        @client.event
        async def on_reaction_remove(reaction, user):
            await self.call_event('on_reaction_remove', reaction, user)
            
    # runs code for event
    async def call_event(self, event_name: str, *event_args, **event_kwargs):
        await self.handler_dispatcher.dispatch_event(event_name, self.client, self.game_data,
                                                     *event_args, **event_kwargs)

    # adds new handler to dispatcher
    def register_event_handler(self, event_name: str, handler):
        self.handler_dispatcher.add_handler(handler, event_name)

    # adds to the help msg, displayed when !help is callled
    def add_help_line(self, newline):
        self.help += '\n' + newline

# Allows for multiple copies of events, so I can write multiple mod functions for the same bot.
# for each event, calls each event handler with client, game_data, and event-specific params.
class GameEventHandlerDispatcher:
    def __init__(self):
        self.handlers = {"on_message": [],
                         "on_ready": [],
                         "on_reaction_add": [],
                         "on_reaction_remove": []}

    # runs each handler for a given event
    async def dispatch_event(self, event_name, client, game_data, *event_args, **event_kwargs):
        for handler in self.handlers[event_name]:
            await handler(client, game_data, *event_args, **event_kwargs)

    # adds new handler to dispatcher
    def add_handler(self, handler, event_name: str):
        self.handlers[event_name].append(handler)


# a """discord bot""" that contains event handlers.
# register with a GeneralBot to run the code
# (subclass me)
# Todo: may want to make subclasses with shared functionality
class DispatchedBot:
    def __init__(self, bot: GeneralBot, helpstr: str = ''):
        if helpstr != '':
            bot.add_help_line(helpstr)
        bot.register_event_handler('on_ready', self.on_ready)
        bot.register_event_handler('on_message', self.on_message)
        bot.register_event_handler('on_reaction_add', self.on_reaction_add)
        bot.register_event_handler('on_reaction_remove', self.on_reaction_remove)
        self.bot = bot

    async def get_help_string(self) -> str:
        return self.bot.help

    async def on_ready(self, client: discord.Client, game_data: GameData):
        pass

    async def on_message(self, client: discord.Client, game_data,
                         message: discord.Message):
        pass

    async def on_reaction_add(self, client: discord.Client, game_data: GameData,
                              reaction: discord.Reaction, user: discord.User):
        pass

    async def on_reaction_remove(self, client: discord.Client, game_data: GameData,
                                 reaction: discord.Reaction, user: discord.User):
        pass
