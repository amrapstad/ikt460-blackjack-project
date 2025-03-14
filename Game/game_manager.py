from Game.card import Card
import random
from Game.card import Suit
from Game.dealer import Dealer

class GameManager:
    # On initialize
    def __init__(self, deck_count):
        self.players = []
        self.available_cards = []
        self.dealer = Dealer()

        # Sets up initial game setup, i.e Dealer gets 2 cards and player(s) get 2 cards
        self.initial_setup(deck_count)

    def initialSetup(self, deck_count):
        # Create deck of cards, based on the amount of decks (deck_count) you want
        self.create_decks(deck_count=deck_count)

        # Shuffles the deck at random
        self.shuffle()
        return

    def get_dealer_cards(self):
        return self.dealer.get_dealer_cards()

    def get_available_cards(self):
        return self.availalbe_cards

    def get_player_cards(self):
        return self.players
    
    def create_decks(self, deck_count):
        for i in range(deck_count):
            for suit in [1, 2, 3, 4]:
                self.available_cards.extend(Card(Suit(suit), n+1) for n in range(13))
            return
        
    def shuffle(self):
        random.shuffle(self.availalbe_cards)
