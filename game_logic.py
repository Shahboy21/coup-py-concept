'''Contains actions possible to be taken by the players and the game logic needed to play coup.'''

from game_objects import Card, Deck, Player

def start_game(num_players = 3):
    assert 3 <= num_players <= 6, "Game supports 3-6 players currently."
    #Special mode needed for 2 players, expansion required for more players by default
    pass
    
def launch_coup(origin:Player, target: Player):
    pass

def take_income(origin:Player):
    pass

def take_foreign_aid(origin:Player):
    pass

#Claiming Duke
def take_tax(origin:Player):
    pass

#Claiming Duke, origin is the player that is blocking the aid. Target is the one attempting to take foreign aid.
def block_foreign_aid(origin:Player, target:Player): 
    pass

#Claiming Captain
def steal(origin:Player, target:Player):
    pass

#Claiming Captain or Ambassador
def block_theft(origin:Player, target:Player, claim: Card):
    pass

#Claiming Assassin
def assassinate(origin:Player, target:Player):
    pass

#Claiming Contessa
def block_assination(origin:Player):
    pass

#Claim Ambassador
def exchange_roles(origin:Player):
    pass

def challenge_last_action(origin:Player, target:Player):
    pass



