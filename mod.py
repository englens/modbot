import json
import discord

# handles getting of user information, and storing updates automatically
# if called for a unregistered user, init them
class GameData:
    def __init__(self, data_file_path):
        self.file = data_file_path
        self.dic = {}
        self.update()  # updates self.dic

    # read data from file. Only do this when class created.
    def update(self):
        with open(self.file, 'r') as f:
            self.dic = json.load(f)

    # save data to file
    def save(self):
        with open(self.file, 'w') as f:
            json.dump(self.dic, f)

    # returns the value of given user value
    def grab_user_value(self, user_id, value_name):
        if user_id not in self.dic['users']:
            self.init_user(user_id)
        return self.dic['users'][user_id][value_name]

    # creates game data for user, based on dic[users][default]
    def init_user(self, user_id):
        self.dic['users'][user_id] = self.dic['users']['default'].copy()
        self.save()

    def add_to_user_value(self, user_id, value_name, amount):
        try:
            self.dic['users'][user_id][value_name] += amount
        except KeyError:
            self.dic['users'][user_id][value_name] = amount
        print(f'user {user_id} gained {amount} {value_name}.')
        self.save()


# General bot that holds a discord bot client.
# holds a data file, and handles custom bot events.
class GeneralBot:
    def __init__(self, game_data_file, client):
        super().__init__()
        self.client = client  # discord.py bot client
        self.game_data = GameData(game_data_file)
        self.handler_dispatcher = GameEventHandlerDispatcher()

        # --- client events ---
        @client.event
        async def on_ready():
            print('Online.')
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


# Allows for multiple copies of events, so I can write multiple mod functions for the same bot.
# for each event, calls each event handler with client, game_data, and event-specific params.
class GameEventHandlerDispatcher:
    def __init__(self):
        self.handlers = {"on_message": [],
                         "on_ready": [],
                         "on_reaction_add": [],
                         "on_reaction_remove": []}

    # runs each handler for a given event
    # *kwargs always has same args as
    async def dispatch_event(self, event_name, client, game_data, *event_args, **event_kwargs):
        for handler in self.handlers[event_name]:
            await handler(client, game_data, *event_args, **event_kwargs)

    # adds new handler to dispatcher
    def add_handler(self, handler, event_name: str):
        self.handlers[event_name].append(handler)


# a """discord bot""" that contains event handlers.
# register with a GeneralBot to run the code
# (subclass me)
class DispatchedBot:
    def __init__(self, bot: GeneralBot):
        bot.register_event_handler('on_ready', self.on_ready)
        bot.register_event_handler('on_message', self.on_message)
        bot.register_event_handler('on_reaction_add', self.on_reaction_add)
        bot.register_event_handler('on_reaction_remove', self.on_reaction_remove)

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
