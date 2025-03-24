from Game.card import Card
from Game.card import Suit
from Game.dealer import Dealer
from Game.player import Player
import random


class GameManager:
    # On initialize
    def __init__(self, deck_count):
        self.players = []
        self.available_cards = []
        self.dealer = Dealer()

        # Sets up initial game setup, i.e Dealer gets 2 cards and player(s) get 2 cards
        self.initial_setup(deck_count)

    def initial_setup(self, deck_count):
        # Create deck of cards, based on the amount of decks (deck_count) you want
        self.create_decks(deck_count=deck_count)

        # Shuffles the deck at random
        self.shuffle()

        # Initial player and hand with 2 cards for initial player
        new_player = Player()
        new_player.initial_hand(self.available_cards)
        self.players.append(new_player)

        # Initial 2 cards for dealer
        for i in range(2):
            self.dealer.hit(self.available_cards)
        return

    def get_dealer(self):
        return self.dealer

    def get_available_cards(self):
        return self.available_cards

    def get_players(self):
        return self.players
    
    def create_decks(self, deck_count):
        for i in range(deck_count):
            for suit in [1, 2, 3, 4]:
                self.available_cards.extend(Card(Suit(suit), n+1) for n in range(13))
            return
        
    def shuffle(self):
        random.shuffle(self.available_cards)
