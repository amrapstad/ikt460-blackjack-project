import pandas as pd
import os
from definitions import TABLES_DIR

def get_split_action_from_csv(csv_table, player_card_value, face_up_card):
    # Make jack, queen and king equal 10
    player_card_value = min(player_card_value, 10)
    face_up_card = min(face_up_card, 10)

    # First column name is '0'
    row = csv_table[csv_table['0'] == player_card_value]

    value = row[str(face_up_card)].values[0]

    return value

def get_total_action_from_csv(csv_table, hand_total, face_up_card):
    # Make jack, queen and king equal 10
    face_up_card = min(face_up_card, 10)

    # First column name is '0'
    row = csv_table[csv_table['0'] == hand_total]

    value = row[str(face_up_card)].values[0]

    return value


class OptimalAgent:
    def __init__(self):
        self.agent_label = "optimal"
        self.hard_total_table = pd.read_csv(os.path.join(TABLES_DIR, "hard_total.csv"))
        self.soft_total_table = pd.read_csv(os.path.join(TABLES_DIR, "soft_total.csv"))
        self.split_table = pd.read_csv(os.path.join(TABLES_DIR, "split.csv"))

        """
        Actions:
        0 - Stand
        1 - Hit
        2 - Double down
        3 - Split
        4 - Insurance
        """
        self.action_dictionary = {
            'S': 0,
            'H': 1,
            'D': 2,
            'Y': 3,
            'N': -1
        }

        return

    def choose_action(self, player_hand, dealer_face_up_card):
        face_up_card_value = dealer_face_up_card.value

        current_action = -1

        # Check for split
        if len(player_hand.hand_cards) == 2:
            card1_value = min(player_hand.hand_cards[0].value, 10)
            card2_value = min(player_hand.hand_cards[1].value, 10)
            if card1_value == card2_value:
                result = get_split_action_from_csv(self.split_table, card1_value, face_up_card_value)  # Y or N
                current_action = self.action_dictionary[result]

        # When not splitting, whether possible or not
        if current_action < 0:
            player_hand.calculate_hand_values()
            soft_hand = len(player_hand.possible_values) > 1 # True: Soft hand, False: Hard hand

            if soft_hand:
                hand_total = max(player_hand.possible_values)
                result = get_total_action_from_csv(self.soft_total_table, hand_total, face_up_card_value)
                current_action = self.action_dictionary[result]
            else:
                hand_total = player_hand.possible_values[0]
                result = get_total_action_from_csv(self.hard_total_table, hand_total, face_up_card_value)
                current_action = self.action_dictionary[result]

        # Lastly, convert DD to hit if more than 2 cards in hand
        if len(player_hand.hand_cards) > 2 and current_action == 2:
            current_action = 1

        if current_action < 0 or current_action > 3:
            raise Exception("Invalid action from optimal agent!")

        return current_action
