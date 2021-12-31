import asyncio
from asyncio.exceptions import CancelledError
import random

import discord
import trueskill
from py2neo import Graph, Node, Relationship
from py2neo import RelationshipMatcher, NodeMatcher

from mod import DispatchedBot
### Setup graph enviroment stuff
uri = "neo4j+s://c73aae9b.databases.neo4j.io"

passwordfile = '../rps_password.txt'
with open(passwordfile) as f:
    password = f.read()
    if password[-1] == '\n':
        password = password[:-1]

throw_graph = Graph(uri, auth=("neo4j", password))
nm = NodeMatcher(throw_graph)
rm = RelationshipMatcher(throw_graph)
BEATS = Relationship.type("BEATS")

### Graph functions

# Returns node object or None if throw not in db
def get_node(throw: str) -> Node:
    return nm.match(name=throw).first()

def add_throw_to_db(throw: str):
    # Dont run me if throw already in db!
    newnode = Node("Throw", name=throw)
    throw_graph.create(newnode)
    return newnode

# returns name of winner or None if no winner defined
def get_winner(throwA: Node, throwB: Node):
    # both throws expected to be in db; error otherwise
    if rm.match((throwA,throwB)).exists():
        return throwA
    elif rm.match((throwB,throwA)).exists():
        return throwB
    else:
        return None

def set_winner(throwW: Node, throwL: Node):
    # Relationship expected to not already exist (the converse too)
    throw_graph.create(BEATS(throwW, throwL))
    

# Users can !challenge other users, then dm the bot their throw
# Throws can be anything, and if a winner is not yet defined, its defined at runtime
# throw graph is stored in remote neo4j database
# 5 Winner gets elo
class RPSWorld(DispatchedBot):
    CHALLENGE_TIMEOUT = 60  # seconds
    FIGHT_TIMEOUT = 60  # seconds
    def __init__(self, *args, **kwargs):
        self.state = 'default'
        self.challenge_response = None
        self.response_timeout_task = None
        self.fighterA = None
        self.fighterB = None
        self.fight_channel = None
        self.fighterA_response = None
        self.fighterB_response = None
        help = '!challenge @<name> --- send a request to begin a game of RPSWorld.'
        help += "\n!elo @<name> --- check mentioned user's elo."
        #help += f'    current valid roles: {RoleGiver.role_names}'
        super().__init__(helpstr=help, *args, **kwargs)
        #super().__init__(*args, **kwargs)

    # Checks if user has a role on the role list, and gives them the role and replaces it if necessary
    async def on_message(self, client: discord.Client, game_data,
                         message: discord.Message):
        # ignore bot's own msgs
        if message.author.id == client.user.id:
            return
        
        if self.state == 'wait_for_accept':
            if message.author == self.fighterB and message.channel == self.fight_channel:
                # Correct author and in fight channel; proceed
                if message.content == 'accept':
                    # Fight accepted; cancel timeout task and ask both players for response
                    self.response_timeout_task.cancel()   
                    self.fighterA_response = None
                    self.fighterB_response = None
                    msg = '======== MATCH BEGUN ========\n'
                    msg += f'Each player, please DM this bot a single word with only english letters. This will be your throw.\n(You have {RPSWorld.FIGHT_TIMEOUT} seconds).'
                    await self.fight_channel.send(msg)
                    # Set new state
                    self.state = 'wait_for_throws'
                    # Start timeout task
                    self.response_timeout_task = asyncio.create_task(self.wait_for_figher_response())
                    
                elif message.content == 'deny':
                    # cancel match, return to default
                    self.response_timeout_task.cancel()   
                    await self.fight_channel.send("Match denied.")
                    self.state = 'default'
                else:
                    # Improper message
                    await self.fight_channel.send("Please respond with 'accept' or 'deny'.")

        if self.state == 'wait_for_throws':
            # Test 1: make sure this was dm'd
            if not isinstance(message.channel, discord.DMChannel):
                return
            
            # Test 2: make sure this is one of the two fighters
            if not message.author.id in [self.fighterA.id, self.fighterB.id]:
                return
            # Test 3: Make sure this fighter didnt already send a response
            if message.author.id == self.fighterA.id and self.fighterA_response is not None:
                await message.channel.send("Response already recived.")
                return
            if message.author.id == self.fighterB.id and self.fighterB_response is not None:
                await message.channel.send("Response already recived.")
                return
            # Test 4: make sure its a valid throw
            tokens = message.content.split()
            if len(tokens) != 1:
                await message.channel.send("Please send only a single word throw.")
                return
            throw = tokens[0].lower()
            if not throw.isalpha():
                await message.channel.send("Plase make sure your throw only contains alphabetic characters.")
                return

            # All checks passed, record throw
            if message.author.id == self.fighterA.id:
                await self.got_fighterA_throw(game_data, throw)
            elif message.author.id == self.fighterB.id:
                await self.got_fighterB_throw(game_data, throw)
            else:
                # This shouldnt happen
                await self.fight_channel.send('Error: got throw that improperly passed tasks; aborting')
                self.state = 'default'

        ## Otherwise, check for commands

        if self.state == 'default':
            tokens = message.content.split()
            #  Ignore empty
            if len(tokens) == 0:
                return
            cmd = tokens[0]
            if cmd == '!challenge':
                await self.challenge(client, message)           

            if cmd == '!elo':
                await self.display_elo(client, game_data, message)

    # gets the elo of given user from the gamedatabase
    async def display_elo(self, client, game_data, message):
        if len(message.mentions) != 1:
            await message.channel.send('Error: please mention (@) a single other user.\nSyntax: `!elo @<name>`')
            return
        other: discord.Member = message.mentions[0]
        rating = self.get_user_rating(game_data, other)
        await message.channel.send(f"{other.display_name}'s Elo: {round(rating.mu, 2)}")


    # Called when !challenge is called during default state
    async def challenge(self, client, message):
        if isinstance(message.channel, discord.DMChannel):
            await message.channel.send('Matches must be started in a server.')
            return
        # Need exactly one mention
        if len(message.mentions) != 1:
            await message.channel.send('Error: please mention (@) a single other user to start a match.\nSyntax: `!challenge @<name>`')
            return
        other: discord.Member = message.mentions[0]

        if other.id == message.author.id:
            await message.channel.send("Error: You can't challenge yourself.")
            return

        # Set fight parameters for this match
        self.fight_channel = message.channel
        self.fighterA = message.author
        self.fighterB = other
        self.state = 'wait_for_accept'
        # At this point we're clear -- in public channel, 
        # Now, we notify other and wait for accept or deny
        # Also start callback to cancel if 60 seconds pass

        # Create task and set it. This is so we can gracefully cancel the callback if the accept or deny happens
        await message.channel.send(f"{other.display_name}, please respond with 'accept' or 'deny'.")
        self.response_timeout_task = asyncio.create_task(self.wait_for_challenge_accept(message))
    
    # get the winner from the throw database, or create a new matchup if none exists
    async def calc_winner(self, throwA, throwB):
        if throwA == throwB:
            return throwA, throwB, True, False

        # Get node objects
        nodeA = get_node(throwA)
        if nodeA is None:
            nodeA = add_throw_to_db(throwA)
        nodeB = get_node(throwB)
        if nodeB is None:
            nodeB = add_throw_to_db(throwB)
        # fetch the winner (or None if not defined)
        winner = get_winner(nodeA, nodeB)
        # TODO: implement ties?
        
        if winner is None:
            is_matchup_new = True
            # not yet defined
            # we need to define one
            winner = random.choice((nodeA, nodeB))
            if winner is nodeA:
                set_winner(nodeA, nodeB)
            else:
                set_winner(nodeB, nodeA)
        else:
            is_matchup_new = False
        # fetch and return the names of the winner, loser
        if winner['name'] == throwA:
            return throwA, throwB, False, is_matchup_new
        elif winner['name'] == throwB:
            return throwB, throwA, False, is_matchup_new
        else:
            raise NotImplementedError()  # TODO


    # Get a trueskill rating object for given user (from gamedata)
    def get_user_rating(self, gamedata, user: discord.Member):
        elo_mu = gamedata.grab_user_value(user.id, 'elo_mu')
        elo_sigma = gamedata.grab_user_value(user.id, 'elo_sigma')
        if elo_mu is None:
            return trueskill.Rating()
        else:
            return trueskill.Rating(float(elo_mu), float(elo_sigma))

    # Get the new elo for this match, and record it to gamedata
    async def calc_elo(self, gamedata, winner, loser, is_tie=False):
        # we say elo, but its actually trueskill
        winner_rating = self.get_user_rating(gamedata, winner)
        loser_rating = self.get_user_rating(gamedata, loser)
        
        new_winner_rating, new_loser_rating = trueskill.rate_1vs1(winner_rating, loser_rating, is_tie)
        gamedata.set_user_value(winner.id, 'elo_mu', new_winner_rating.mu)
        gamedata.set_user_value(winner.id, 'elo_sigma', new_winner_rating.sigma)
        gamedata.set_user_value(loser.id, 'elo_mu', new_loser_rating.mu)
        gamedata.set_user_value(loser.id, 'elo_sigma', new_loser_rating.sigma)
        return new_winner_rating.mu, new_loser_rating.mu

    # With both throws prepared, 
    # 1) Calc a winner
    # 2) Display Results
    # 3) Record new throw relationship; record new elo
    async def finish_match(self, gamedata):
        await self.fight_channel.send('Both throws accepted!')
        await asyncio.sleep(4)
        await self.fight_channel.send(f"{self.fighterA.display_name}'s throw is...")
        await asyncio.sleep(2)
        await self.fight_channel.send(f"**{self.fighterA_response}**!")
        await asyncio.sleep(2)
        await self.fight_channel.send(f"{self.fighterB.display_name}'s throw is...")
        await asyncio.sleep(2)
        await self.fight_channel.send(f"**{self.fighterB_response}**!")
        await asyncio.sleep(3)
        winner_throw, loser_throw, is_tie, is_matchup_new = await self.calc_winner(self.fighterA_response, self.fighterB_response)
        if winner_throw == self.fighterA_response:
            winner = self.fighterA
            loser = self.fighterB
        else:
            winner = self.fighterB
            loser = self.fighterA
        await self.fight_channel.send("And the winner is...")
        await asyncio.sleep(1)
        if is_tie:
            msg = '**Its a tie!!**'
        else:
            msg = f'**{winner.display_name}!!**'
        winner_new_elo, loser_new_elo = await self.calc_elo(gamedata, winner, loser, is_tie)
        msg += '\n==========================='
        msg += f'\n{winner.display_name} new elo: {round(winner_new_elo, 2)}\n{loser.display_name} new elo: {round(loser_new_elo,2)}'
        if is_matchup_new:
            mid = '    ' + str(winner_throw) + ' BEATS ' + str(loser_throw) + '    '
            top = '\n' + max(int((len(mid)-13)/2), 2)*'=' + ' New matchup ' + max(int((len(mid)-13)/2), 2)*'='
            bot = len(mid)*'='
            msg += top + '\n' + mid + '\n' + bot
        await self.fight_channel.send(msg)
        self.state = 'default'

    # Called when fighterA sends a throw during wait_for_throw
    async def got_fighterA_throw(self, gamedata, throw: str):
        self.fighterA_response = throw
        await self.fight_channel.send(f"Got {self.fighterA.display_name}'s throw.")
        # If both now ready, start match result printout
        if self.fighterB_response != None:
            self.response_timeout_task.cancel()
            self.state = 'print_results'
            await self.finish_match(gamedata)

    # Called when fighterB sends a throw during wait_for_throw
    async def got_fighterB_throw(self, gamedata, throw: str):
        self.fighterB_response = throw
        await self.fight_channel.send(f"Got {self.fighterB.display_name}'s throw.")
        # If both now ready, start match result printout
        if self.fighterA_response != None:
            self.response_timeout_task.cancel()
            self.state = 'print_results'
            await self.finish_match(gamedata)

    # Timeout task when a challenge is sent. If not canceled, reverts state to default after timeout
    async def wait_for_challenge_accept(self, message):
        # Times out if no response by sender
        try:
            await asyncio.sleep(RPSWorld.CHALLENGE_TIMEOUT)
            # After waiting for response, timeout if none found
            await self.fight_channel.send('No response found; challenge timed out.')
            self.state = 'default'
        except asyncio.CancelledError:
            pass  # challege was responded to; no msg printed
    
    # Timeout task when a challenge is sent. If not canceled, reverts state to default after timeout
    # Awards winner if one fighter responded but not the other
    async def wait_for_figher_response(self):
        try:
            await asyncio.sleep(RPSWorld.FIGHT_TIMEOUT)
            if self.fighterA_response is None and self.fighterB_response is None:
                    await self.fight_channelsend('Neither player responded; match aborted.')
            elif self.fighterA_response is None:
                # player B wins by default
                # TODO: award elo
                await self.fight_channel.send(f"{self.fighterB.display_name} wins by default, but cark hasn't implemented this changing elo yet so it doesn't matter!")
            elif self.fighterB_response is None:
                # player A wins by default
                # TODO: award elo
                await self.fight_channel.send(f"{self.fighterA.display_name} wins by default, but cark hasn't implemented this changing elo yet so it doesn't matter!")
            else: 
                print("Something wrong happened!")
            self.state = 'default'
        except asyncio.CancelledError:
            pass  # both fighers responded in time; no msg printed
