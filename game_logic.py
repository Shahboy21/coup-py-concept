'''Contains actions possible to be taken by the players and the game logic needed to play coup.'''

from game_objects import Card, Deck, Player, Actions

REQUIRES_TARGET: list[Actions] = [Actions.ASSASSINATE, Actions.COUP, Actions.STEAL]
UNCHALLANGED_ACTIONS: list[Actions] = [Actions.INCOME, Actions.COUP]
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

def start_game(num_players = 3):
    assert 3 <= num_players <= 6, "Game supports 3-6 players currently."
    #Special mode needed for 2 players, expansion required for more players by default
    
    game_deck = Deck()
    game_deck.shuffle_cards()
    all_players: list[Player] = []
    turn_queue: list[Player] = []
    
    # FIXME: Currently this doesn't follow standard card dealing order 
    num_alive = num_players
    for i in range(num_players):
        all_players.append(Player(id = i+1, first_role=game_deck.draw(), second_role=game_deck.draw()))
        turn_queue = all_players.copy() 
    
    
    #Main game loop
    while num_alive > 1:
        main_player:Player = turn_queue.pop(0)
        challengers: list[Player] = [p for p in turn_queue if p.alive]
        if main_player.alive:
            
            #Start turn 
            #TODO: Add a seperate broadcast message function. These represent messages that everyone can see during gameplay if choices were hidden.
            print(f"It is Player {main_player.id}'s turn! They have {main_player.bal} coins.") # BROADCAST
            
            #Pick Action
            action_str = f"What would you like to do from the following list:\n"
            action_map: dict[int,Actions] = dict(enumerate(main_player.get_available_actions()))
            for key,action in action_map:
                action_str += f"{key}) {action.value}\n"
                desired_action = validate_response(action_str, list(action_map.keys()))
            
            action:Actions = action_map(desired_action)
            
            #Determine target if needed
            targetted_action:bool = action in REQUIRES_TARGET                           
            if targetted_action:
                valid_targets: dict[int, Player] = dict(enumerate(challengers))
                target_str = "Which player would you like to target from: \n"
                for target_index,target in valid_targets:
                    target_str += f"{target_index}) Player {target.id}\n"
                target_player_index:int = validate_response(target_str, list(valid_targets.keys()))
                target = valid_targets[target_player_index]
            
            # Announce Action 
            announcement = f"Player {main_player.id} will {action.value} "
            if targetted_action: announcement += f" from Player {target.id}!"
            print(announcement) # BROADCAST
                     
            end_turn = False
            # Check for challenges
            if action not in UNCHALLANGED_ACTIONS:
                claimed_role: Card = CLAIM_MAP[action][0] 
                for p in challengers:
                    choice = validate_response(f'Player {p.id} would you like to challenge (Y/N)?', ['Y','N'])
                    if choice.capitalize == 'Y':
                        end_turn = challenge_last_action(main_player, p, claimed_role) # On challenge if main_player does not have the proper role, the turn ends.                         
                        break # After the first challenge no more challenges need to be checked
            
            # Check for blocks if needed
            blocked, successfully_blocked = False, False
            if action in BLOCKABLE_ACTIONS and (not end_turn):
                for p in challengers:
                    choice = validate_response(f'Player {p.id} would you like to block the action (Y/N)?',['Y','N']) 
                    if choice.capitalize == 'Y':
                        blocking_action = BLOCKED_ACTION_MAP[action]
                        claimed_role = CLAIM_MAP(blocking_action)[0] 
                        if blocking_action == Actions.DENY_THEFT:
                            claim_choice = validate_response("To block stealing do you claim: 0) Captain or 1) Ambassador?", ['0','1'])
                            claimed_role = CLAIM_MAP[blocking_action][claim_choice] 
                        blocked = True
                        
                        # Check for block counter challenges
                        counter_players: list[Player] = [main_player] + [c for c in challengers if c != p]
                        for counter_p in counter_players:
                            counter = validate_response(f'Player {counter_p.id}, player {p.id} is claiming they are a {claimed_role}! would you like to challenge the block (Y/N)?', ['Y','N'])
                            
                            if counter.capitalize =='Y':
                                #TODO: Complete CHALLENGE function
                                successfully_blocked = not challenge_last_action(p, counter_p,claimed_role)
                                if not successfully_blocked: blocked = False
                                break  # After the first challenge no more challenges need to be checked
                        
                        if successfully_blocked:
                            break # No need to go check if other players want to block
                        
            if not blocked and not successfully_blocked:
                #Resolve Action
                pass #TODO: Call appropriate function based on action
            
            turn_queue.append(main_player)
            
    
    #Create deck
    #Create Players
    #Start turn 1
    # Declare Action
    # Check for Challenges and Resolve
    # If no challenges or Proven Valid correct
    # Check for Blocks
    # Check for Blocker Challenges and Resolve
    # If no blockers or valid blocker Resolve action
    
    #Next Turn
    #Check if player is alive, remove from queues if dead
    
    pass

def validate_response(msg:str, valid_responses: list[str]) -> str:
    """Takes an input message continues asking until a response from valid_responses is given."""
    output:str = input(msg)
    while output not in valid_responses:
        print(f'Please enter a valid response from one of: {valid_responses}...')
        output = input(msg)
    return output
    

def print_board_status():
    pass

def lose_influence(subject:Player):
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

def challenge_last_action(defendant:Player, prosecutor:Player, role:Card) -> bool:
    """ Returns true if the defending player does not have the role required for their claimed action. 
    
    When the defendant does have the correct role. The prosecutor loses an influence and the dendant replaces that role.
    """
    pos = defendant.find_claim(role)
    if  pos > -1: 
        print(f'Player {defendant.id} was an {role.name}! Player {prosecutor.id} lost the challenge...') #BROADCAST
        
        #Replace the revealed role
        
        #prosecutor chooses a card to reveal and broadcast that information.
        return False
    else:
        print(f'Player {defendant.id} was not an {role.name}!') #BROADCAST
        #Choose card to reveal and broad cast that info
        return True
    



