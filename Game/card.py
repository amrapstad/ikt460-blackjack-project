from enum import Enum

class Suit(Enum):
    CLUBS = 1
    DIAMONDS = 2
    HEARTS = 3
    SPADES = 4

class Card:
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value
        return

    def get_card(self):
        return self.suit, self.value