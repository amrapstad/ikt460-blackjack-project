from Game.game_manager import GameManager

class Enviroment:
    def __init__(self, deck_count):
        self.GameManager_ = GameManager(deck_count=deck_count)