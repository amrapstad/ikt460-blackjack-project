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

        self.action_dictionary = {
            'S': 0,
            'H': 1,
            'D': 2,
            'Y': 3,
            'N': -1
        }

        return

    def choose_action(self, player_hand, dealer_face_up_card):
        return


"""
Actions:
0 - Stand
1 - Hit
2 - Double down
3 - Split
4 - Insurance
"""

start_time = time.time()




print("--- %s seconds ---" % (time.time() - start_time))