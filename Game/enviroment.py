from Game.game_manager import GameManager

class Enviroment:
    def __init__(self, deckCount):
        self.GameManager_ = GameManager(deckCount=deckCount)