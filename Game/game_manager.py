from Game.card import Card
from Game.dealer import Dealer
import random

class GameManager:

    # On initialize
    def __init__(self, deck_count):
        self.availalbe_cards = []
        self.dealer = Dealer()
        self.players = []

        # Creates the stack of cards based on deck_count
        self.create_decks(deck_count=deck_count)

        # Shuffles the deck at random
        self.shuffle()

        # Sets up initial game setup, i.e Dealer gets 2 cards and player(s) get 2 cards
        self.initialSetup():

        # # For testing
        # for card in self.availalbe_cards:
        #     suit, value = card.get_card()
        #     print(f"Suit: {suit}, Value: {value}")
        # print("####### AFTER SHUFFLE #######")
        # # For testing
        # for card in self.availalbe_cards:
        #     suit, value = card.get_card()
        #     print(f"Suit: {suit}, Value: {value}")

    def shuffle(self):
        random.shuffle(self.availalbe_cards)

    def create_decks(self, deck_count):
        for i in range(deck_count):
            for suit in ["S", "D", "C", "H"]:
                self.availalbe_cards.extend(Card(suit, n+1) for n in range(13))
            return

    def initialSetup():
        return

    def get_dealer_cards(self):
        return self.dealer.get_dealer_cards()

    def get_available_cards(self):
        return self.availalbe_cards

    def get_player_cards(self):
        return self.players

