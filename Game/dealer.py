from Game.card import Card
import random

class Dealer:
    def __init__(self):
        self.dealer_cards = []
        self.possible_values = []
        self.calculate_hand_values()

        return

    def hit(self, available_cards):
        hit_card = available_cards.pop()
        self.dealer_cards.append(hit_card)
        self.calculate_hand_values()
        return hit_card

    def stand(self):
        return

    def get_dealer_cards(self):
        return self.dealer_cards
        
    def get_possible_values(self):
        self.calculate_hand_values()
        return self.possible_values


    def calculate_hand_values(self):
        total_values = [0]
        for card in self.dealer_cards:
            # Get last element which is the card value
            card_value = card.get_card()[-1] 

            # NOT ACE: Simply add card value to all possible total values of hand
            if card_value > 1:
                add_value = min(card_value, 10)
                for i in range(len(total_values)):
                    total_values[i] += add_value
                continue

            # ACE: Add 1 to all possible total values of hand, and add a new entry with the highest of the values + 11
            max_value = max(total_values)
            for i in range(len(total_values)):
                total_values[i] += 1
            total_values.append(max_value + 11)

        self.possible_values = total_values
        return