import pandas as pd
import time


def get_action_from_csv(csv_table, player_card_value, face_up_card):
    # Format:
    ## First row : Face up card value
    ## First column: Hand total (each card value in split case)

    # Soft/hard total return values:
    ## S - Stand
    ## H - Hit
    ## D - Double down

    # Split return values:
    # Y - Yes, do split
    # N, No, don't do split

    # First column name is '0'
    row = csv_table[csv_table['0'] == player_card_value]

    value = row[str(face_up_card)].values[0]

    return value


class OptimalAgent:
    def __init__(self):
        self.hard_total_table = pd.read_csv("hard_total.csv")
        self.soft_total_table = pd.read_csv("soft_total.csv")
        self.split_table = pd.read_csv("split.csv")

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
        # Get player hand
        # Is it splittable?
        ## Y: Perform split and end.
        ## N: Continue
        # Is the hand hard or soft?
        ## Soft: Perform action from soft table
        ## Hard: Perform action from hard table

        card_list = player_hand.hand_cards
        face_up_card_value = dealer_face_up_card.value

        current_action = -1

        # Check for split
        if len(card_list) == 2:
            card1_value = min(card_list[0].value, 10)
            card2_value = min(card_list[1].value, 10)
            if card1_value == card2_value:
                result = get_action_from_csv(self.split_table, card1_value, face_up_card_value)  # Y or N
                current_action = self.action_dictionary[result]

        if current_action < 0:
            player_hand.calculate_hand_values()
            soft_hand = len(player_hand.possible_values) > 1 # True: Soft hand, False: Hard hand

            if soft_hand:
                hand_total = max(player_hand.possible_values)
                result = get_action_from_csv(self.soft_total_table, hand_total, face_up_card_value)
                current_action = self.action_dictionary[result]
            else:
                hand_total = player_hand.possible_values[0]
                result = get_action_from_csv(self.hard_total_table, hand_total, face_up_card_value)
                current_action = self.action_dictionary[result]

        return current_action
