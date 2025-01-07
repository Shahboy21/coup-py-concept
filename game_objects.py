'''Defines the objects needed by the game coup.'''
from enum import Enum
from random import shuffle

class Card(Enum):
    """Provides the standard roles used in the game of Coup. 
    
    Numeric values are assigned in alphabetical order.
    """
    AMBASSADOR = 0
    ASSASSIN = 1
    CAPTAIN = 2
    CONTESSA = 3
    DUKE = 4

class Actions(Enum):
    INCOME = "take income"
    FOREIGN_AID = "take foreign aid"
    TAX = "collect taxes"
    STEAL = "steal money"
    EXCHANGE = "exchange roles"
    ASSASSINATE = "assassinate an opponent"
    COUP = "launch a coup"
    DENY_ASSASSINATION = 'block the assissination'
    DENY_THEFT = 'block the steal'
    DENY_AID = 'block the claim to foreign aid'

class Deck:
    """The deck of cards for the running game. Top of the deck is defined as the last index. 
    
    Consists of 3 of each type of card. Methods to draw, shuffle, and reset the status of the deck.
    """
    deck: list[Card] = []
    #Shuffle, Draw, Reset Game
    def __init__(self):
        self.reset_deck()
    
    def draw(self) -> Card:
        '''Draws the top card from the deck of cards and returns it.'''
        try:
            return self.deck.pop()
        except IndexError as e:
            raise IndexError("The deck of cards is empty before drawing. This is an impossible gamestate for normal gameplay. Something went wrong")
        
    def shuffle_cards(self):
        '''Shuffles the deck of cards in place.'''
        if len(self.deck) > 0:
            shuffle(self.deck)
    
    def reset_deck(self):
        self.deck = []
        self.deck.extend([Card.AMBASSADOR]*3)
        self.deck.extend([Card.ASSASSIN]*3)
        self.deck.extend([Card.CAPTAIN]*3)
        self.deck.extend([Card.CONTESSA]*3)
        self.deck.extend([Card.DUKE]*3)
        self.shuffle_cards()
        

class Player:
    #Hidden information
    _active_roles: list[Card] = []
    
    #Public information    
    _alive: bool = False # If the player is still in the game value is True. 
    # Alive status is only set during initialization and role reveals.
    _bal: int = 0
    _revealed_roles: list[Card] = [] 
    
    def __init__(self, id:str, first_role:Card, second_role:Card):
        self._id = id
        self._bal = 2
        self._active_roles = [first_role, second_role]
        self._alive = True
    
    @property
    def id(self) -> str:
        return self._id
    
    @property
    def alive(self) -> bool:
        return self._alive
    
    @property
    def bal(self) -> int:
        return self._bal
    
    @property
    def active_roles(self) -> list[Card]:
        return self._active_roles
    
    @property
    def revealed_roles(self) -> list[Card]:
        return self._revealed_roles
       
    def increment_bal(self, increment:int) -> int:
        '''Increments the balance by the given parameter and returns the final balance.'''
        self._bal += int(increment)
        return self._bal
    
    def find_claim(self, claim:Card) -> int:
        '''Checks if the player has the card they claimed to have. 
        Returns the position if true (0 or 1), -1 otherwise.'''
        if claim in self.active_roles:
            return 0 if claim == self.active_roles[0] else 1
        return -1
    
    def reveal_role(self, pos:int) -> Card:
        '''Returns the role in position provided. That role is no longer active and added to the revealed roles.
        
        If there are no active_roles the player is out of the game, but their roles are still revealed to everyone else in the game.
        '''
        assert pos < len(self.active_roles), "Invalid position for the number of active roles."
        role = self._active_roles.pop(pos)
        self._revealed_roles.append(role)
        if len(self.active_roles) == 0:
            self._alive = False
        return role 
    
    def replace_role(self, pos:int, new_role:Card):
        '''Replaces the role in the provided position with the new role.'''
        assert pos < len(self.active_roles), "Invalid replacement with the current number of active roles."
        self._active_roles[pos] = new_role
    
    def get_available_actions(self) -> list[Actions]:
        base_actions = [Actions.INCOME, Actions.FOREIGN_AID, Actions.TAX, Actions.STEAL, Actions.EXCHANGE]
        #If more than 10 coins must launch a coup!
        if self.bal >= 10:
            return [Actions.COUP]
        if self.bal > 3: 
            base_actions.append(Actions.ASSASSINATE)
        if self.bal > 7:
            base_actions.append(Actions.COUP)
        return base_actions
    
    

