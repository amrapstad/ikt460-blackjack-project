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
        self.original_deck = []
        self.dealer = Dealer()
        self.shuffle_percent_rule = True
        self.initial_player_count = players
        self.round_history_output = []

        # Sets up initial game setup, i.e Dealer gets 2 cards and player(s) get 2 cards
        self.initial_setup(deck_count)

    def initial_setup(self, deck_count):
        # Create deck of cards, based on the amount of decks (deck_count) you want
        self.create_decks(deck_count=deck_count)
        self.original_deck = self.available_cards.copy()

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

        output = self.round_history_output.copy()

        self.round_history_output = []

        if self.shuffle_percent_rule:
            if len(self.available_cards) < len(self.original_deck) * 0.4:
                print("Shuffling deck...")
                self.available_cards = self.original_deck.copy()
                self.shuffle()
        else:
            self.available_cards = self.original_deck.copy()
            self.shuffle()

        self.players = []
        self.dealer = Dealer()
        
        for i in range(self.initial_player_count):
            new_player = Player()
            new_player.initial_hand(self.available_cards)
            self.players.append(new_player)

        self.dealer.initial_hand(self.available_cards)

        return output

        
    def check_winner(self):
        all_players_busted = True

        for player_index, player in enumerate(self.players):
            for hand_index, hand in enumerate(player.hands):
                player_values = hand.get_possible_values()
                dealer_values = self.dealer.get_possible_values()

                player_max_valid = max((v for v in player_values if v <= 21), default=0)
                dealer_max_valid = max((v for v in dealer_values if v <= 21), default=0)

                if player_max_valid == 0:
                    print(f'BUSTED: Player #{player_index+1} Hand #{hand_index+1} busted with minimum value {min(player_values)}!')
                    continue  # No point comparing busted hand

                all_players_busted = False  # At least one hand is valid

                if dealer_max_valid == 0:
                    print(f'WINNER: Player #{player_index+1} Hand #{hand_index+1} wins because dealer busted!')
                    continue

                if player_max_valid > dealer_max_valid:
                    if self.blackjack(player_values, hand.hand_cards) and not self.blackjack(dealer_values, self.dealer.dealer_cards):
                        print(f'BLACKJACK WIN: Player #{player_index+1} Hand #{hand_index+1} wins with Blackjack! Dealer has {dealer_max_valid}')
                    else:
                        print(f'WINNER: Player #{player_index+1} Hand #{hand_index+1} wins with {player_max_valid} against dealers {dealer_max_valid}')
                elif player_max_valid < dealer_max_valid:
                    print(f'LOSER: Player #{player_index+1} Hand #{hand_index+1} lost with {player_max_valid} vs dealers {dealer_max_valid}')
                else:
                    print(f'TIE: Player #{player_index+1} Hand #{hand_index+1} tied with the dealer at {player_max_valid}')

        if all_players_busted:
            print("ROUND OVER: All player hands busted. Dealer wins by default.")
            self.create_histyory_output()
            return False
        self.create_histyory_output()

        return True

    def create_histyory_output(self):
        dealer_values = self.dealer.get_possible_values()
        dealer_max_valid = max((v for v in dealer_values if v <= 21), default=0)

        for player_index, player in enumerate(self.players):
            for hand_index, hand in enumerate(player.hands):
                player_values = hand.get_possible_values()
                player_max_valid = max((v for v in player_values if v <= 21), default=0)

                if player_max_valid == 0:
                    outcome = "LOSE"
                elif dealer_max_valid == 0:
                    outcome = "WIN"
                elif player_max_valid > dealer_max_valid:
                    outcome = "WIN"
                elif player_max_valid < dealer_max_valid:
                    outcome = "LOSE"
                else:
                    outcome = "TIE"
                
                hand_history = [(cards.copy(), stake, action) for cards, stake, action in hand.hand_history]
                self.round_history_output.append((hand_history, outcome, self.dealer.face_up_card))



    def play_round(self, player_index, hand_index, action):
        print("")
        if (self.players[player_index].hands[hand_index].busted_hand is False):
            print(f'INPUT: Player #{player_index+1} does action #{action} on hand #{hand_index+1}')
            self.players[player_index].action_input(hand_index, action, self.available_cards)

            # Check if all hand for each player is is_standing
            for player_index, player in enumerate(self.players):
                for hand_index, hand in enumerate(player.hands):
                    if hand.is_standing is False:
                        return None
            
            # Dealer does his actions
            self.dealer.deal_algorithm(self.available_cards)

            self.check_winner()

            print("\n ### Next round! ### \n")
            output = self.next_round()
            return output
