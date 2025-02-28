from Game.card import Card
import random

class Dealer:
    def __init__(self):
        self.dealer_cards = []
        return

    def hit(self, availalbe_cards):
        hit_card = availalbe_cards.pop()
        self.dealer_cards.append(hit_card)
        return hit_card

    def stand(self):
        return

    def get_dealer_cards(self):
        return self.dealer_cards