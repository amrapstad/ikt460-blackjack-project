import random

class Q_Learning:
    def __init__(self):
        self.q_tables = {}
        self.q_value_changes = []  # Track Q-value deltas over time

    def process_round_history_for_q_values(self, round_history_output, learning_rate=0.05, discount_factor=0.9):
        delta_sum = 0.0
        delta_count = 0

        for player_index, hand_index, hand_history, outcome, dealer_face_up_card in round_history_output:
            dealer_info = (dealer_face_up_card.value, dealer_face_up_card.suit.name)

            if player_index not in self.q_tables:
                self.q_tables[player_index] = {}

            q_table = self.q_tables[player_index]

            for i, (cards, stake, action) in enumerate(hand_history):
                player_possible_values = self.get_possible_values_from_cards(cards)
                state = (tuple(sorted(player_possible_values)), dealer_face_up_card.value)
                action_key = action

                if outcome == "WIN":
                    reward = stake if i == len(hand_history) - 1 else 0.5 * stake
                elif outcome == "LOSE":
                    reward = -stake if i == len(hand_history) - 1 else 0.5 * stake
                else:
                    reward = 0

                if action == 3:
                    reward *= 2

                valid_actions = self.get_valid_actions_from_cards(cards, dealer_face_up_card)
                if action not in valid_actions:
                    print(f"Penalty: Invalid action {action} taken.")
                    reward = -5 * stake

                if (state, action_key) not in q_table:
                    q_table[(state, action_key)] = 0.0

                if i + 1 < len(hand_history):
                    next_cards, _, _ = hand_history[i + 1]
                    next_hand_repr = tuple(sorted((card.value, card.suit.name) for card in next_cards))
                    next_state = (next_hand_repr, dealer_info)
                    future_qs = [q_table.get((next_state, a), 0.0) for a in [0, 1, 2, 3, 4]]
                    max_future_q = max(future_qs)
                else:
                    max_future_q = 0.0

                old_q = q_table[(state, action_key)]
                new_q = old_q + learning_rate * (reward + discount_factor * max_future_q - old_q)
                q_table[(state, action_key)] = new_q

                delta_sum += abs(new_q - old_q)
                delta_count += 1

        if delta_count > 0:
            avg_delta = delta_sum / delta_count
            self.q_value_changes.append(avg_delta)

    def get_possible_values_from_cards(self, cards):
        total_values = [0]

        for card in cards:
            card_value = card.value

            if card_value > 1:
                add_value = min(card_value, 10)
                for i in range(len(total_values)):
                    total_values[i] += add_value
            else:
                max_value = max(total_values)
                for i in range(len(total_values)):
                    total_values[i] += 1
                total_values.append(max_value + 11)

        return total_values

    def choose_action(self, player_index, player_hand, dealer_face_up_card, epsilon=0.1):
        dealer_info = (dealer_face_up_card.value, dealer_face_up_card.suit.name)
        player_possible_values = self.get_possible_values_from_cards(player_hand.hand_cards)
        state = (tuple(sorted(player_possible_values)), dealer_face_up_card.value)

        if player_index not in self.q_tables:
            self.q_tables[player_index] = {}

        q_table = self.q_tables[player_index]

        valid_actions = self.get_valid_actions_from_cards(player_hand.hand_cards, dealer_face_up_card)
        if not valid_actions:
            return 0

        if random.random() < epsilon:
            return random.choice(valid_actions)

        q_values = {action: q_table.get((state, action), 0.0) for action in valid_actions}
        best_action = max(q_values, key=q_values.get)
        return best_action

    def get_valid_actions_from_cards(self, cards, dealer_card):
        valid_actions = [0, 1]

        if len(cards) == 2:
            valid_actions.append(2)

            val1 = min(cards[0].value, 10)
            val2 = min(cards[1].value, 10)
            if val1 == val2:
                valid_actions.append(3)

        if dealer_card.value == 1:
            if len(cards) < 3:
                valid_actions.append(4)

        return valid_actions

    def print_q_tables(self):
        if not self.q_tables:
            print("No Q-tables available.")
            return

        action_names = {0: "STAND", 1: "HIT", 2: "DOUBLE", 3: "SPLIT", 4: "INSURANCE"}

        for player_index, q_table in self.q_tables.items():
            print(f"\n# Q-Table for Player #{player_index + 1} #\n")
            for (state, action), q_value in q_table.items():
                player_hand_repr, dealer_info = state
                dealer_value, dealer_suit = dealer_info
                action_label = action_names.get(action, f"UNKNOWN({action})")

                player_hand_str = ', '.join(f"{val} of {suit}" for val, suit in player_hand_repr)
                dealer_card_str = f"{dealer_value} of {dealer_suit}"

                print(f"State -> Player Hand: [{player_hand_str}], Dealer: {dealer_card_str}")
                print(f"  Action: {action_label} ({action})")
                print(f"  Q-Value: {q_value:.4f}\n")
