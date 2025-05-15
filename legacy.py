def print_environment_state_true(environment):
    print("")
    print("### Players ###")
    for player_index, player in enumerate(environment.game_manager.players):  # Track player index
        print(f'- Player {player_index + 1}')
        for hand_index, hand in enumerate(player.hands):
            print(f'    - Hand #{hand_index + 1}')
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
        print(f'- Player {player_index + 1}')
        for hand_index, hand in enumerate(player.hands):
            print(f'    - Hand #{hand_index + 1}')
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
