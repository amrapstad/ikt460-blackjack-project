from Game.environment import Environment
from Game.dealer import Dealer
from Game.card import Card, Suit

environment = Environment(deck_count=1)

def print_environment_state():
    print("### Players ###")
    for player_index, player in enumerate(environment.game_manager.players):  # Track player index
        print(f'- Player {player_index+1}')
        for hand_index, hand in enumerate(player.hands):
            print(f'    - Hand #{hand_index+1}')
            print(f'        STANDING: {hand.is_standing}')
            for card in hand.hand_cards:
                print(f'        {card.suit}, Value: {card.value}')
            print(f'        Possible values: {hand.get_possible_values()}')
            print(f'        Hand stake: {hand.stake}')
    print('### Dealer ###')
    for card in environment.game_manager.dealer.dealer_cards:
            print(f'    {card.suit}, Value: {card.value}')
    print(f'    Possible values: {environment.game_manager.dealer.get_possible_values()}')
    print("### Overviews ###")
    print(f'Total available cards: {len(environment.game_manager.available_cards)}\n')

#Test
def moves():
    for player_index, player in enumerate(environment.game_manager.players):
        for hand_index, hand in enumerate(player.hands):
            if min(10, hand.hand_cards[0].value) == min(10, hand.hand_cards[1].value):
                environment.input(player_index, hand_index, 3)
                environment.input(player_index, hand_index, 0)
            else:
                environment.input(player_index, hand_index, 1)
                environment.input(player_index, hand_index, 0)
moves()
print_environment_state()
