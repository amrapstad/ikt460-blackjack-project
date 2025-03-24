from Game.enviroment import Enviroment
from Game.dealer import Dealer
from Game.card import Card, Suit

enviroment = Enviroment(deck_count=1)

def print_enviroment_state():
    available_cards, players, dealer = enviroment.get_game_state()
    print(f'Total available cards: {len(available_cards)}')
    print("### Players ###")
    for player_index, player in enumerate(players):  # Track player index
        print(f'- Player {player_index+1}')
        for hand_index, hand in enumerate(player.get_hands()):
            print(f'    - Hand #{hand_index+1}')
            for card in hand.get_hand_cards():
                print(f'        {card.suit}, Value: {card.value}')
            print(f'        Possible values: {hand.get_possible_values()}')
    print('### Dealer ###')
    for card in dealer.get_dealer_cards():
            print(f'    {card.suit}, Value: {card.value}')
    print(f'    Possible values: {dealer.get_possible_values()}')

def action_round()

print_enviroment_state()

    




