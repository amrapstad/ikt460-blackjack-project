from Game.game_manager import GameManager

class Environment:
    def __init__(self, deck_count, players):
        self.game_manager = GameManager(deck_count=deck_count, players=players)
        
    def get_game_state(self):
        return self.game_manager.available_cards, self.game_manager.players, self.game_manager.dealer

    def input(self, player_index, hand_index, action):
        player = self.game_manager.players[player_index]
        hand = player.hands[hand_index]
        dealer_card = self.game_manager.dealer.face_up_card

        # Action Validation
        if action == 2 and len(hand.hand_cards) != 2:
            print("Invalid: Double Down only allowed on 2-card hands.")
            return None

        if action == 3:
            if len(hand.hand_cards) != 2:
                print("Invalid: Split only allowed on 2-card hands.")
                return None
            v1 = min(hand.hand_cards[0].value, 10)
            v2 = min(hand.hand_cards[1].value, 10)
            if v1 != v2:
                print("Invalid: Split only allowed on same-value cards.")
                return None

        if action == 4 and dealer_card.value != 1:
            print("Invalid: Insurance only allowed when dealer shows Ace.")
            return None

        round_history = self.game_manager.play_round(player_index, hand_index, action)

        if round_history is not None:
            return round_history

        for player in self.game_manager.players:
            for hand in player.hands:
                if hand.is_standing is False:
                    return None
        return None
