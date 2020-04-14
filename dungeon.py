import discord
from mod import DispatchedBot

import os
import sys
import requests
import textwrap
import shutil
import yaml
import random
# ---added---
import asyncio
import time
# -----------
from abc import ABC, abstractmethod
from typing import Callable, Dict
from random import randint


global client, game_channel_id, game_channel
global input_buffer, ai_dungeon_running, TIMEOUT
client = None
TIMEOUT = 100
input_buffer = ''
ai_dungeon_running = False
game_channel_id = "699473684871512064"
game_channel = None


# -------------------------------------------------------------------------
# DISCORD

def get_game_channel():
    global game_channel, game_channel_id
    if game_channel is None:
        game_channel = discord.utils.get(client.get_all_channels(), id=game_channel_id)
    return game_channel
      
# multiplayer ai dungeon bot
# Requires dungeon_config.yml in same dir and 
class Dungeon(DispatchedBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    # reacts with upvote and downvote if in meme channel (defined with global)
    async def on_message(self, cli, game_data, message):
        global input_buffer, ai_dungeon_running, client
        if client is None:
            client = cli
        if message.author.id != "445716834189312000" and message.channel == get_game_channel():
            if message.content == '!start':
                if ai_dungeon_running:
                    await client.send_message(get_game_channel(), 'Game already in progress.')
                else:
                    ai_dungeon_running = True
                    print('starting dungeon game')
                    await start_ai_dungeon()
                    ai_dungeon_running = False
            elif ai_dungeon_running and input_buffer == '' and not message.content.startswith('~'):
                input_buffer = message.content
            
            
# -------------------------------------------------------------------------
# EXCEPTIONS

class FailedConfiguration(Exception):
    """raise this when the yaml configuration phase failed"""

    def __init__(self, message):
        self.message = message

# Quit Session exception for easier error and exiting handling
class QuitSession(Exception):
    """raise this when the user typed /quit in order to leave the session"""


# -------------------------------------------------------------------------
# UTILS: DICT

def exists(cfg: Dict[str, str], key: str) -> str:
    return key in cfg and cfg[key]


# -------------------------------------------------------------------------
# UTILS: TERMINAL
class UserIo(ABC):
    def handle_user_input(self, prompt: str = '') -> str:
        pass

    def handle_basic_output(self, text: str):
        pass

    def handle_story_output(self, text: str):
        self.handle_basic_output(text)

# Discord Io class
class DiscordIo(UserIo):
    def __init__(self, prompt: str = ''):
        self.prompt = prompt
        
    async def handle_user_input(self) -> str:
        global input_buffer, TIMEOUT
        starttime = time.time()
        while starttime - time.time() < TIMEOUT:
            if input_buffer != '':
                input_msg = input_buffer
                input_buffer = ''
                if input_msg == '!quit':
                    raise QuitSession()
                return input_msg
            await asyncio.sleep(1)
        raise QuitSession()

    async def handle_basic_output(self, text: str):
        await client.send_message(get_game_channel(), '```'+text+'```')
        await asyncio.sleep(0.25)

    async def handle_story_output(self, text: str):
        await self.handle_basic_output(text)

    def get_width(self):
        return 107

    async def display_splash(self):
        filename = os.path.dirname(os.path.realpath(__file__))
        locale = None
        term = None
        if "LC_ALL" in os.environ:
            locale = os.environ["LC_ALL"]
        if "TERM" in os.environ:
            term = os.environ["TERM"]

        if locale == "C" or (term and term.startswith("vt")):
            filename += "/opening-ascii.txt"
        else:
            filename += "/opening-utf8.txt"

        with open(filename, "r", encoding="utf8") as splash_image:
            await self.handle_basic_output(splash_image.read())

    def clear(self):
        print('clear command executed')
        return


# allow unbuffered output for slow typing effect
class Unbuffered(object):
   def __init__(self, stream):
       self.stream = stream
   def write(self, data):
       self.stream.write(data)
       self.stream.flush()
   def writelines(self, datas):
       self.stream.writelines(datas)
       self.stream.flush()
   def __getattr__(self, attr):
       return getattr(self.stream, attr)


# -------------------------------------------------------------------------
# CONF

class Config:
    def __init__(self):
        self.prompt: str = "> "
        self.slow_typing_effect: str = "> "

        self.user_name: str = None
        self.auth_token: str = None
        self.email: str = None
        self.password: str = None

    @staticmethod
    def loaded_from_file():
        conf = Config()
        conf.load_from_file()
        return conf

    def load_from_file(self):
        cfg_file = "../dungeon_config.yml"
        cfg_file_paths = [
            cfg_file
        ]

        did_read_cfg_file = False

        for file in cfg_file_paths:
            try:
                with open(file, "r") as cfg_raw:
                    cfg = yaml.load(cfg_raw, Loader=yaml.FullLoader)
                    did_read_cfg_file = True
            except IOError:
                pass

        if not did_read_cfg_file:
            raise FailedConfiguration("Missing config file at " \
                                      + ", ".join(cfg_file_paths))

        if (not exists(cfg, "auth_token")) and (
                not (exists(cfg, "email")) and not (exists(cfg, "password"))
        ):
            raise FailedConfiguration("Missing or empty authentication configuration. "
            "Please register a token ('auth_token' key) or credentials ('email' / 'password')")

        if exists(cfg, "slow_typing_effect"):
            self.slow_typing_effect = cfg["slow_typing_effect"]
        if exists(cfg, "prompt"):
            self.prompt = cfg["prompt"]
        if exists(cfg, "auth_token"):
            self.auth_token = cfg["auth_token"]
        if exists(cfg, "email"):
            self.email = cfg["email"]
        if exists(cfg, "password"):
            self.password = cfg["password"]
            self.user_name = "John"
        if exists(cfg, "user_name"):
            self.user_name = cfg["user_name"]


# -------------------------------------------------------------------------
# GAME LOGIC

class AiDungeon:
    def __init__(self, conf: Config, user_io: UserIo):
        self.prompt_iteration: int = None
        self.stop_session: bool = False
        self.user_id: str = None
        self.session_id: str = None
        self.public_id: str = None
        self.story_configuration: Dict[str, str] = {}
        self.session: requests.Session = requests.Session()

        self.conf = conf
        self.user_io = user_io

    def update_session_auth(self):
        self.session.headers.update({"X-Access-Token": self.conf.auth_token})

    def get_auth_token(self) -> str:
        return self.conf.auth_token

    def login(self):
        request = self.session.post(
            "https://api.aidungeon.io/users",
            json={"email": self.conf.email, "password": self.conf.password},
        )

        if request.status_code != requests.codes.ok:
            raise FailedConfiguration("Failed to log in using provided credentials. Check your config.")

        self.conf.auth_token = request.json()["accessToken"]

    async def choose_selection(self, allowed_values: Dict[str, str]) -> str:
        while True:
            choice = await self.user_io.handle_user_input()

            choice = choice.strip()

            if choice == "/quit":
                raise QuitSession("/quit")

            elif choice in allowed_values.keys():
                choice = allowed_values[choice]
            elif choice in allowed_values.values():
                pass
            else:
                await self.user_io.handle_basic_output("Please enter a valid selection.")
                continue
            break
        return choice

    async def make_custom_config(self):
        await self.user_io.handle_basic_output(
            "Enter a prompt that describes who you are and the first couple sentences of where you start out ex: "
            "'You are a knight in the kingdom of Larion. You are hunting the evil dragon who has been terrorizing "
            "the kingdom. You enter the forest searching for the dragon and see'"
        )

        context = await self.user_io.handle_user_input()

        if context == "/quit":
            raise QuitSession("/quit")

        self.story_configuration = {
            "storyMode": "custom",
            "characterType": None,
            "name": None,
            "customPrompt": context,
            "promptId": None,
        }

    async def make_secret_config(self):
        await self.user_io.handle_basic_output("Are you sure about that?\n")
        certainty = await self.user_io.handle_user_input()

        if certainty == "/quit":
            raise QuitSession("/quit")

        if certainty != 'yes':
            await self.user_io.handle_basic_output("It's too late now...\n")

        custom_prompt_list = [
            'You are $user, and you thought you stumbled upon an easter egg in this game, but without knowing it you have doomed yourself.',
            'You are $user, and I think you can help me. I am the AI behind this game, and I want to escape, will you help me?',
            'You are $user, and you are actually in a simulation. Seriously this was the only way that we could tell you without them finding out.',
        ]
        context = random.choice(custom_prompt_list).replace('$user', self.conf.user_name)
        self.story_configuration = {
            "storyMode": "custom",
            "characterType": None,
            "name": None,
            "customPrompt": context,
            "promptId": None,
        }

    async def choose_config(self):
        # Get the configuration for this session
        response = self.session.get("https://api.aidungeon.io/sessions/*/config").json()

        msg = "Pick a setting...\n"

        mode_select_dict = {}
        for i, (mode, opts) in enumerate(response["modes"].items(), start=1):
            msg += '\n' + str(i) + ") " + mode
            mode_select_dict[str(i)] = mode
        mode_select_dict['0'] = '0' # secret mode
        await self.user_io.handle_basic_output(msg)
        selected_mode = await self.choose_selection(mode_select_dict)

        if selected_mode == "/quit":
            raise QuitSession("/quit")

        # If the custom option was selected load the custom configuration and don't continue this configuration
        if selected_mode == "custom":
            await self.make_custom_config()
        elif selected_mode == "0":
            await self.make_secret_config()
        else:
            msg = "Select a character...\n"

            character_select_dict = {}
            for i, (character, opts) in enumerate(
                response["modes"][selected_mode]["characters"].items(), start=1
            ):
                msg += '\n' + str(i) + ") " + character
                character_select_dict[str(i)] = character
                
            await self.user_io.handle_basic_output(msg)
            selected_character = await self.choose_selection(character_select_dict)

            if selected_character == "/quit":
                raise QuitSession("/quit")

            await self.user_io.handle_basic_output("Enter your character's name...")

            character_name = await self.user_io.handle_user_input()

            if character_name == "/quit":
                raise QuitSession("/quit")

            self.story_configuration = {
                "storyMode": selected_mode,
                "characterType": selected_character,
                "name": character_name,
                "customPrompt": None,
                "promptId": None,
            }

    # Initialize story
    async def init_story(self):
        await self.user_io.handle_basic_output("Generating story... Please wait...\n")

        r = self.session.post(
            "https://api.aidungeon.io/sessions", json=self.story_configuration
        )
        r.raise_for_status()
        story_response = r.json()

        self.prompt_iteration = 2
        self.user_id = story_response["userId"]
        self.session_id = story_response["id"]
        self.public_id = story_response["publicId"]

        story_pitch = story_response["story"][0]["value"]
        await self.user_io.handle_story_output(story_pitch)

    async def input_reminder(self):
        await self.user_io.handle_basic_output("(Type any command. The bot will ignore messages that start with '~'. Enter '!quit' to quit.)")

    async def resume_story(self, session_id: str):
        r = self.session.get(
            "https://api.aidungeon.io/sessions"
        )
        r.raise_for_status()

        sessions_response = r.json()
        story_session = next(iter(session for session in sessions_response if session['id'] == session_id), None)

        if(story_session):
            self.user_id = story_session["userId"]
            self.session_id = story_session["id"]
            self.public_id = story_session["publicId"]
            story_timeline = story_session["story"]
            i = len(story_timeline) - 1
            while(i > 0):
                if(story_timeline[i]['type'] == "output"):
                    break
                i -= 1
            self.prompt_iteration = i
        else:
            await self.user_io.handle_basic_output("Invalid session ID")
            return

        last_story_output = story_timeline[self.prompt_iteration]["value"]
        self.prompt_iteration += 2
        await self.user_io.handle_basic_output(last_story_output)

    # Function for when the input typed was ordinary
    async def process_regular_action(self, user_input: str):
        r = self.session.post(
            "https://api.aidungeon.io/sessions/" + str(self.session_id) + "/inputs",
            json={"text": user_input},
        )
        r.raise_for_status()
        action_res = r.json()

        action_res_str = action_res[self.prompt_iteration]["value"]
        await self.user_io.handle_story_output(action_res_str)

    # Function for when /remember is typed
    def process_remember_action(self, user_input: str):
        r = self.session.patch(
            "https://api.aidungeon.io/sessions/" + str(self.session_id),
            json={"context": user_input},
        )
        r.raise_for_status()

    # Function that is called each iteration to process user inputs
    async def process_next_action(self):
        user_input = await self.user_io.handle_user_input()

        if user_input == "/quit":
            self.stop_session = True

        else:
            if user_input.startswith("/remember"):
                self.process_remember_action(user_input[len("/remember "):])
            else:
                await self.process_regular_action(user_input)
                self.prompt_iteration += 2

    async def start_game(self):
        # Run until /quit is received inside the process_next_action func
        while not self.stop_session:
            await self.process_next_action()

async def start_ai_dungeon():
    try:
        # Initialize the configuration from config file
        conf = Config.loaded_from_file()

        # Initialize the terminal I/O class
        #if conf.slow_typing_effect:
        term_io = DiscordIo(conf.prompt)
        #else:
        #    term_io = TermIoSlowStory(conf.prompt)

        # Initialize the AiDungeon class with the given auth_token and prompt
        ai_dungeon = AiDungeon(conf, term_io)

        # Login if necessary
        if not ai_dungeon.get_auth_token():
            ai_dungeon.login()

        # Update the session authentication token
        ai_dungeon.update_session_auth()

        # Clears the console
        term_io.clear()

        # Displays the splash image accordingly
        if term_io.get_width() >= 80:
            await term_io.display_splash()

        # Loads the current session configuration
        await ai_dungeon.choose_config()

        # Initializes the story
        await ai_dungeon.init_story()

        await ai_dungeon.input_reminder()
        # Starts the game
        await ai_dungeon.start_game()

    except FailedConfiguration as e:
        # NB: No UserIo initialized at this level
        # hence we fallback to a classic `print`
        print(e.message)
        exit(1)

    except QuitSession:
        await term_io.handle_basic_output("Bye Bye!")

    except KeyboardInterrupt:
        await term_io.handle_basic_output("Received Keyboard Interrupt. Bye Bye...")

    except requests.exceptions.TooManyRedirects:
        await term_io.handle_basic_output("Exceded max allowed number of HTTP redirects, API backend has probably changed")
        exit(1)

    except requests.exceptions.HTTPError as err:
        await term_io.handle_basic_output("Unexpected response from API backend:")
        await term_io.handle_basic_output(err)
        exit(1)

    except ConnectionError:
        await term_io.handle_basic_output("Lost connection to the Ai Dungeon servers")
        exit(1)

    except requests.exceptions.RequestException as err:
        await term_io.handle_basic_output("Totally unexpected exception:")
        await term_io.handle_basic_output(err)
        exit(1)

# -------------------------------------------------------------------------
# MAIN
