from Game.environment import Environment
from Game.dealer import Dealer
from Game.card import Card, Suit
from Agent.q_learning import Q_Learning



def print_environment_state_true():
    print("")
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


def print_environment_state_player_view(environment):
    print("")
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
    card = environment.game_manager.dealer.face_up_card
    print(f'    {card.suit}, Value: {card.value}')
    print("### Overviews ###")
    print(f'Total available cards: {len(environment.game_manager.available_cards)}')

def loop():
    print("Welcome to the Blackjack game!")
    deck_count = int(input("Enter number of decks: "))
    if deck_count < 1:
        print("Deck count must be at least 1.")
        return
    environment = Environment(deck_count=deck_count)
    q_learning_agent = Q_Learning()
    while True:
        for player_index, player in enumerate(environment.game_manager.players):
            for hand_index, hand in enumerate(player.hands):
                while True:
                    print_environment_state_player_view(environment)
                    print("")
                    print(f'### Actions for Player #{player_index+1} Hand #{hand_index+1} ###')
                    print("0 - Stand")
                    print("1 - Hit")
                    print("2 - Double Down")
                    print("3 - Split")
                    print("4 - Insurance")
                    print("### Other Actions ###")
                    print("5 - Reset")
                    print("6 - Overview")
                    action = int(input("Enter action: "))
                    if action < 0 or action > 6:
                        print("Invalid action. Please try again.")
                        continue
                    if action == 5:
                        print("Game reset.")
                        loop()
                        continue

                    round_history_output = environment.input(player_index, hand_index, action=action)
                    if round_history_output is None:
                        continue
                    

                    print("### Round History ###")

                    for hand_index, (hand_history, outcome, dealer_face_up_card) in enumerate(round_history_output):
                        print(f'Player #{player_index + 1} Hand #{hand_index + 1} history:')
                        print(f'  Outcome: {outcome}')
                        print(f'  Dealer Face-Up Card: {dealer_face_up_card.suit.name}, Value: {dealer_face_up_card.value}')

                        for entry_index, (cards, stake, next_action) in enumerate(hand_history):
                            print(f'    Iteration {entry_index + 1}: Action = {next_action}, Stake = {stake}')
                            print(f'      Cards:')
                            for card in cards:
                                print(f'        {card.suit.name}, Value: {card.value}')
                    


                    if action == 0 or 2:
                        break
    return

loop()

