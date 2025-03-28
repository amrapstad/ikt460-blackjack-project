from Game.enviroment import Enviroment
from Game.dealer import Dealer
from Game.card import Card, Suit

enviroment = Enviroment(deck_count=1)

def print_enviroment_state():
    print("### Players ###")
    for player_index, player in enumerate(enviroment.get_game_manager().get_players()):  # Track player index
        print(f'- Player {player_index+1}')
        for hand_index, hand in enumerate(player.get_hands()):
            print(f'    - Hand #{hand_index+1}')
            for card in hand.get_hand_cards():
                print(f'        {card.suit}, Value: {card.value}')
            print(f'        Possible values: {hand.get_possible_values()}')
            print(f'        Hand stake: {hand.get_hand_stake()}')
            print('### Dealer ###')
    for card in enviroment.get_game_manager().get_dealer().get_dealer_cards():
            print(f'    {card.suit}, Value: {card.value}')
    print(f'    Possible values: {enviroment.get_game_manager().get_dealer().get_possible_values()}')
    print("### Overviews ###")
    print(f'Total available cards: {len(enviroment.get_game_manager().get_available_cards())}')

#Test
def moves():
    for player_index, player in enumerate(enviroment.get_game_manager().get_players()): 
        for hand_index, hand in enumerate(player.get_hands()):
            if (min(10, hand.get_hand_cards()[0].value) == min(10, hand.get_hand_cards()[1].value)):
                player.action_input(hand_index, 3, enviroment.get_game_manager().get_available_cards())


print_enviroment_state()
moves()
print_enviroment_state()
    




