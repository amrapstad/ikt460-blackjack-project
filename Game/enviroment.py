from Game.game_manager import GameManager

class Enviroment:
    def __init__(self, deck_count):
        self.game_manager = GameManager(deck_count=deck_count)

    def get_game_manager(self):
        return self.game_manager

    def get_game_state(self):
        return self.game_manager.get_available_cards(), self.game_manager.get_players(), self.game_manager.get_dealer()