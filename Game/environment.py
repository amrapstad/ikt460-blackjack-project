from Game.game_manager import GameManager

class Environment:
    def __init__(self, deck_count):
        self.game_manager = GameManager(deck_count=deck_count, players=1)
        
    def get_game_state(self):
        return self.game_manager.available_cards, self.game_manager.players, self.game_manager.dealer

    def input(self, player_index, hand_index, action):
        round_history = self.game_manager.play_round(player_index, hand_index, action)
        if round_history is not None:
            return round_history
        for player in self.game_manager.players:
            for hand in player.hands:
                if hand.is_standing is False:
                    return None
            print(f'### Dealer Cards ###')
        for card in self.game_manager.dealer.dealer_cards:
            print(f'    {card.suit}, Value: {card.value}')
        return None