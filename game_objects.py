''' Container for objects needed by the coup game '''

class Player:
    alive: bool = False
    balance: int = 0
    card_1 = None
    card_2 = None
    
    def __init__():
        return
    
    #Exchange
    #Tax
    #Foreign Aid
    #Income
    #Assassinate
    #Steal
    #Coup
    
    

class Card:
    """Ambassador, Assassin, Captain, Contessa, Duke"""
    name = None

class Deck:
    deck: list[Card] = None
    #Shuffle, Draw, Reset Game

def start_game(num_players = 3):
    assert 3 <= num_players <= 6, "Game supports 3-6 players currently."
    #Special mode needed for 2 players, expansion required for more players by default
    
    

