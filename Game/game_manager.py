from Game.card import Card
from Game.card import Suit
from Game.dealer import Dealer
from Game.player import Player
import random


class GameManager:
    # On initialize
    def __init__(self, deck_count, players):
        self.players = []
        self.available_cards = []
        self.dealer = Dealer()
        self.initial_player_count = players

        # Sets up initial game setup, i.e Dealer gets 2 cards and player(s) get 2 cards
        self.initial_setup(deck_count)

    def initial_setup(self, deck_count):
        # Create deck of cards, based on the amount of decks (deck_count) you want
        self.create_decks(deck_count=deck_count)

        # Shuffles the deck at random
        self.shuffle()

        # Initial player and hand with 2 cards for initial player
        for i in range(self.initial_player_count):
            new_player = Player()
            new_player.initial_hand(self.available_cards)
            self.players.append(new_player)

        # Initial 2 cards for dealer
        self.dealer.initial_hand(self.available_cards)
    
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

    def next_round(self):
        self.players = []
        self.dealer = Dealer()
        
        # Initial player and hand with 2 cards for initial player
        for i in range(self.initial_player_count):
            new_player = Player()
            new_player.initial_hand(self.available_cards)
            self.players.append(new_player)

        # Initial 2 cards for dealer
        self.dealer.initial_hand(self.available_cards)
        
    def check_winner(self):
        # Check all max(possible_values) that is not higher than 21 for each hand for each player to see which hand won against dealer card values
        for player_index, player in enumerate(self.players):
            for hand_index, hand in enumerate(player.hands):
                # Highest valid value for the player (<= 21)
                player_max_valid = max((value for value in hand.get_possible_values() if value <= 21), default=0)

                # Highest valid value for the dealer (<= 21)
                dealer_max_valid = max((value for value in self.dealer.get_possible_values() if value <= 21), default=0)

                # If player hand is busted (no valid hand <= 21)
                if player_max_valid == 0:
                    print(f'Busted: Player #{player_index+1} with hand #{hand_index+1} with minimum value {min(hand.get_possible_values())} lost!')
                    # Check if all hand for each player is busted
                    for player_index, player in enumerate(self.players):
                        for hand_index, hand in enumerate(player.hands):
                            if hand.busted_hand is False:
                                continue
                    return

                if dealer_max_valid == 0:
                    print('LOSER: Dealer busted!')
                    return True

                # Compare the max valid values
                if player_max_valid > dealer_max_valid:
                    if self.blackjack(hand.get_possible_values(), hand.hand_cards) and self.blackjack(self.dealer.get_possible_values(), self.dealer.dealer_cards) is False:
                        print(f'WINNER: Player #{player_index+1} with hand #{hand_index+1} wins with blackjack, Dealer has {dealer_max_valid}!')
                        continue
                    print(f'WINNER: Player #{player_index+1} with hand #{hand_index+1} wins, Dealer has {dealer_max_valid}!')
                    continue
                elif player_max_valid < dealer_max_valid:
                    print(f'LOSER: Player #{player_index+1} with hand #{hand_index+1} lost, Dealer has {dealer_max_valid}!')
                    continue
                elif player_max_valid == dealer_max_valid:
                    print(f'TIE: Player #{player_index+1} with hand #{hand_index+1} ties with dealer!')
                    continue
        return True

    def play_round(self, player_index, hand_index, action):
        print("")
        if (self.players[player_index].hands[hand_index].busted_hand is False):
            print(f'INPUT: Player #{player_index+1} does action #{action} on hand #{hand_index+1}')
            self.players[player_index].action_input(hand_index, action, self.available_cards)

            # Check if all hand for each player is is_standing
            for player_index, player in enumerate(self.players):
                for hand_index, hand in enumerate(player.hands):
                    if hand.is_standing is False:
                        return False
            
            # Dealer does his actions
            self.dealer.deal_algorithm(self.available_cards)

            self.check_winner()

            print("\n ### Next round! ### \n")
            self.next_round()
