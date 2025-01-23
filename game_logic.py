'''Contains actions possible to be taken by the players and the game logic needed to play coup.'''

from game_objects import Card, Deck, Player, Actions

REQUIRES_TARGET: list[Actions] = [Actions.ASSASSINATE, Actions.COUP, Actions.STEAL]
UNCHALLANGED_ACTIONS: list[Actions] = [Actions.INCOME, Actions.FOREIGN_AID, Actions.COUP]
BLOCKABLE_ACTIONS: list[Actions] = [Actions.FOREIGN_AID, Actions.ASSASSINATE, Actions.STEAL]

CLAIM_MAP: dict[Actions:list[Card]] = {
    Actions.TAX: [Card.DUKE],
    Actions.STEAL: [Card.CAPTAIN],
    Actions.EXCHANGE: [Card.AMBASSADOR],
    Actions.ASSASSINATE: [Card.ASSASSIN],
    Actions.DENY_ASSASSINATION: [Card.CONTESSA],
    Actions.DENY_THEFT: [Card.CAPTAIN,Card.AMBASSADOR], 
    Actions.DENY_AID: [Card.DUKE]
}

BLOCKED_ACTION_MAP: dict[Actions,Actions] = {
    Actions.FOREIGN_AID: Actions.DENY_AID,
    Actions.ASSASSINATE: Actions.DENY_ASSASSINATION,
    Actions.STEAL: Actions.DENY_THEFT
}
SEPERATOR = '**********************'
def run_game(num_players = 3):
    assert 3 <= num_players <= 6, "Game supports 3-6 players currently."
    #Special mode needed for 2 players, expansion required for more players by default
    
    def challenge_loop(defendant: Player, potential_challengers: list[Player], claimed_role: Card) -> bool:
        """Handles the game text input and output when checking for claimed role challenges.
        
        Returns True if the defendant lost the challenge and their turn ends without the action going through. False otherwise.
        """
        print(f'Player {defendant} is claiming they are a {claimed_role.name}.')
        for challenger in potential_challengers:
            choice = validate_response(f'Player {challenger} would you like to challenge (Y/N)?', ['Y','N'])
            if choice.capitalize() == 'Y':
                losing_player = challenge_role_loser(defendant, challenger, claimed_role) 
                if defendant.id == losing_player.id: print(f'Player {defendant} was not a {claimed_role.name}!') #BROADCAST
                else: print(f'Player {defendant} was a {claimed_role.name}! Unfortunate for you Player {challenger}.')
                lose_influence(losing_player)
                # On challenge if main_player does not have the proper role, the turn ends.     
                liar_caught:bool = (defendant.id == losing_player.id) or not defendant.alive
                return liar_caught
        return False
    
    game_deck = Deck()
    game_deck.shuffle_cards()
    all_players: list[Player] = []
    turn_queue: list[Player] = []
    
    # FIXME: Currently this doesn't follow standard card dealing order 
    for i in range(num_players):
        all_players.append(Player(id = str(i+1), first_role=game_deck.draw(), second_role=game_deck.draw()))
        turn_queue = all_players.copy() 
        
    #Main game loop
    while len(turn_queue) > 1:
        main_player:Player = turn_queue.pop(0)

        if not main_player.alive: continue
        challengers: list[Player] = [p for p in turn_queue if p.alive]
            
        #Start turn 
        #TODO: Add a seperate broadcast message function. These represent messages that everyone can see during gameplay if choices were hidden.
        print(f"It is Player {main_player}'s turn! They have {main_player.bal} coins.") # BROADCAST
        
        #Pick Action
        available_actions = main_player.get_available_actions()
        action_str = add_enumerated_options("What would you like to do from the following list:\n", available_actions)          
        desired_action = validate_response(action_str, list(range(len(available_actions))))
        
        action: Actions = available_actions[int(desired_action)]
        target: Player = None
        targets = [p for p in all_players if p.alive and p != main_player]
        #Determine target if needed
        targetted_action:bool = action in REQUIRES_TARGET                           
        if targetted_action:
            target_str = add_enumerated_options("Which player would you like to target: \n", [p.id for p in targets])
            target_player_index:int = validate_response(target_str, list(range(len(targets))))
            target = targets[int(target_player_index)]
        
        # Announce Action 
        announcement = f"Player {main_player} will {action.value} " #FIXME: Change for better action text.
        if targetted_action: announcement += f" from Player {target}!"
        print(announcement) # BROADCAST
            
        # Check for challenges         
        end_turn = False #Flag for premature turn ending
        
        if action not in UNCHALLANGED_ACTIONS:
            claimed_role: Card = CLAIM_MAP[action][0] 
            end_turn = challenge_loop(main_player, challengers, claimed_role)  
        if end_turn: 
            turn_queue = [p for p in turn_queue+[main_player] if p.alive]
            continue #Move to NEXT PLAYER
        
        # Check for blocks if needed
        blocked, blocking_player = False, target
        if target.alive and action in BLOCKABLE_ACTIONS and action != Actions.FOREIGN_AID: #Foreign aid everyone has the chance to block
            choice = validate_response(f'Player {blocking_player} would you like to block the action (Y/N)?',['Y','N']) 
            if choice.capitalize() == 'Y':
                blocked = True
                blocking_action = BLOCKED_ACTION_MAP[action]
                if blocking_action == Actions.DENY_THEFT:
                    claim_choice = validate_response("To block stealing do you claim: 0) Captain or 1) Ambassador?", ['0','1'])
                    claimed_role = CLAIM_MAP[blocking_action][int(claim_choice)] 
                #elif blocking_action == Actions.DENY_AID: Cannot happen with new condition
                #    claimed_role = CLAIM_MAP[blocking_action][0]
                elif blocking_action == Actions.DENY_ASSASSINATION:
                    claimed_role = CLAIM_MAP[blocking_action][0]
                else:
                    pass #TODO: Implement INVALID GAME STATE
        elif target.alive and action == Actions.FOREIGN_AID:
            for blocking_player in targets:
                choice = validate_response(f'Player {blocking_player} would you like to block the action (Y/N)?',['Y','N'])
                if choice.capitalize() == 'Y':
                    blocked = True
                    blocking_action = Actions.DENY_AID
                    claimed_role = CLAIM_MAP[blocking_action][0]
                    break
                        
        if blocked:
            counter_chal_players: list[Player] = [main_player] + [c for c in challengers if c != blocking_player]                     
            blocked = challenge_loop(blocking_player, counter_chal_players, claimed_role)        
                                    
        if not blocked and not end_turn:
            
            #Resolve Action for main player
            match action:
                case Actions.COUP:
                    launch_coup(origin=main_player, target=target)
                case Actions.INCOME:
                    take_income(main_player)
                case Actions.FOREIGN_AID:
                    take_foreign_aid(main_player)
                case Actions.TAX:
                    take_tax(main_player)
                case Actions.STEAL:
                    steal(origin=main_player, target=target)
                case Actions.EXCHANGE:
                    exchange_roles(main_player, game_deck)
                case Actions.ASSASSINATE:
                    assassinate(origin=main_player, target=target)
                case _:
                    pass
                    #Raise Exception      
                          
        turn_queue = [p for p in turn_queue+[main_player] if p.alive]
    
    print('**************************')
    print(f'Player {turn_queue.pop()} is the winner!')
    print('**************************')

def validate_response(msg:str, valid_responses: list[str]) -> str:
    """ Takes an input message and continues taking inputs until a response from valid_responses is given."""
    str_valid_responses = [str(resp) for resp in valid_responses]
    output:str = input(msg.strip()+'\n')
    while output not in str_valid_responses:
        print(f'Please enter a valid response from one of: {str_valid_responses}...')
        output = input(msg.strip()+'\n')
    return output
  
    
def print_board_status(): #TODO: Finish me
    pass

def lose_influence(target:Player) -> None:
    if not target.alive:
        print(f'Player {target} is already dead... was this an error?')
        return None
    elif len(target.active_roles) == 1:
        lost_role_num = 0
    else:
        message = add_enumerated_options(f'Player {target} which of your cards will you give up?\n', target.active_roles) 
        lost_role_num = validate_response(message, valid_responses=['0','1'])
    lost_role = target.reveal_role(int(lost_role_num))
    print(f'Player {target} was a {lost_role}!')
    if not target.alive:
        print(f'Unfortunately, that was Player {target}\'s last role and they are now out of the game!')
    
    
def launch_coup(origin:Player, target: Player) -> None:
    """ The origin player causes the target player to lose influence after paying 7 coins.
    Target player gets to chose which card they lose if they have more than one role.
    
    origin: Player launching the coup and paying 7 coins
    target: Player deciding which role to lose.
    """
    origin.increment_bal(-7)
    lose_influence(target)


def take_income(origin:Player):
    """ Origin player gains one coin."""
    origin.increment_bal(increment=1)


def take_foreign_aid(origin:Player):
    """ Origin player gains two coins.
    This action is BLOCKABLE by someone claiming DUKE.
    """
    origin.increment_bal(increment=2)


#Claiming Duke
def take_tax(origin:Player) -> None:
    """ Origin player gains three coins.
    This can only be done if the origin player is claiming they are a DUKE.
    """
    origin.increment_bal(increment=3)


#Claiming Captain
def steal(origin:Player, target:Player):
    """ Origin player takes two coins from the target player.
    This can only be done if the origin player is claiming they are a CAPTAIN.
    This action is BLOCKABLE by someone claiming CAPTAIN or AMBASSADOR.
    """
    if target.bal >= 2:
        origin.increment_bal(2)
        target.increment_bal(-2)
    else:
        origin.increment_bal(target.bal)
        target.increment_bal(-1*target.bal)


#Claiming Assassin
def assassinate(origin:Player, target:Player):
    """ Origin player pays 3 coins to cause target player to lose influence.
    This can only be done if the origin player is claiming they are an ASSASSIN.
    This action is BLOCKABLE by someone claiming CONTESSA.
    """
    try: origin.increment_bal(-3)
    except ValueError as e:
        raise ValueError(f"Player {origin} cannot afford to assissinate. Illegal game action taken.") from e
    lose_influence(target)


#Claim Ambassador
def exchange_roles(origin:Player, game_deck:Deck):
    """ Origin player draws two roles from the deck and returns any two that they have to the deck. The deck is then shuffled.
    This action can only be done if the origin player is claiming they are an AMBASSADOR.
    
    Revealed roles cannot be exchanged (except when revealed to confirm a challenge). 
    """
    origin.active_roles.append(game_deck.draw())
    origin.active_roles.append(game_deck.draw())
    for i in [0,1]:
        message = add_enumerated_options(f'Player {origin} which role would you like to return?', origin.active_roles)
        selected_role_num = validate_response(message, list(range(len(origin.active_roles))))
        game_deck.return_card(origin.remove_role(int(selected_role_num)))
    game_deck.shuffle_cards()


def challenge_role_loser(defendant:Player, prosecutor:Player, role:Card) -> Player:
    """ Returns the losing player of the challenge based on if the defendant has the input role. 
    If the defendant has the input role, the prosecutor is the losing player. 
    If not, the defendant is the losing player.
    """
    pos = defendant.find_claim(role) #TODO: FINISH Functionality
    if pos > -1: return prosecutor
    else: return defendant

    
def add_enumerated_options(message:str, options:list[str]) -> str:
    """ Given an input message, adds all items in a user friendly selection format and returns the resulting string.
    Format is as follows:
    index) Item
    index2) Item 2
    etc...
    """
    output = message.rstrip() + '\n'
    for index, item in enumerate(options):
        output += f'{index}) {item}\n'
    return output

if __name__ == '__main__':
    run_game(3)