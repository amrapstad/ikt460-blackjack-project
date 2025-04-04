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
        self.history = []

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

        self.check_blackjack_win()
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

    def blackjack(self, values, cards):
        if 21 in values and len(cards) < 3:
            return True
        return False

    def check_blackjack_win(self):
        for player_index, player in enumerate(self.players):
            for hand_index, hand in enumerate(player.get_hands()):
                if self.blackjack(hand.get_possible_values(), hand.get_hand_cards()) and self.blackjack(self.dealer.get_possible_values(), self.dealer.get_dealer_cards()) is False:
                    print(f'WINNER: Player #{player_index+1} with hand #{hand_index+1} wins with blackjack!')
                    continue

    "TEMPORARY CODE"
    def check_busted(self):
        # Check if player or dealer are busted (over 21) and return loser
        for player_index, player in enumerate(self.players):
            for hand_index, hand in enumerate(player.get_hands()):
                if min(hand.get_possible_values()) > 21:
                    print(f'Busted: Player #{player_index+1} with hand #{hand_index+1} busted!')
                    continue

        
    def check_winner(self):
        # Check all max(possible_values) that is not higher than 21 for each hand for each player to see which hand won against dealer card values
        for player_index, player in enumerate(self.players):
            for hand_index, hand in enumerate(player.get_hands()):
                # Highest valid value for the player (<= 21)
                player_max_valid = max((value for value in hand.get_possible_values() if value <= 21), default=None)

                # Highest valid value for the dealer (<= 21)
                dealer_max_valid = max((value for value in self.dealer.get_possible_values() if value <= 21), default=None)

                # If both the player and dealer have busted (no valid hand <= 21), handle that
                if player_max_valid is None:
                    print(f'LOSER: Player #{player_index+1} with hand #{hand_index+1} lost!')
                    return True
                elif dealer_max_valid is None:
                    return True

                # Compare the max valid values
                if player_max_valid > dealer_max_valid:
                    print(f'WINNER: Player #{player_index+1} with hand #{hand_index+1} wins!')
                    return True
                elif player_max_valid < dealer_max_valid:
                    print(f'LOSER: Player #{player_index+1} with hand #{hand_index+1} lost!')
                    return True
                elif player_max_valid == dealer_max_valid:
                    print(f'TIE: Player #{player_index+1} with hand #{hand_index+1} ties with dealer!')
                    continue
        return False

    def play_episode(self, player_index, hand_index, action):

        print(f'INPUT: Player #{player_index+1} does action #{action} on hand #{hand_index+1}')
        self.get_players()[player_index].action_input(hand_index, action, self.get_available_cards())

        # Check if player hand is blackjack (21) and dealer hand is not blackjack (21)
        self.check_blackjack_win()

        "TEMPORARY CODE"
        self.check_busted()

        # Check if all hand for each player is is_standing
        for player_index, player in enumerate(self.players):
            for hand_index, hand in enumerate(player.get_hands()):
                if hand.is_standing is False:
                    return False
        
        # Dealer does his actions
        self.dealer.deal_algorithm(self.available_cards)


        "TEMPORARY CODE"
        if min(self.dealer.get_possible_values()) > 21:
            print('LOSER: Dealer busted!')
            return True

        self.check_winner()
        
