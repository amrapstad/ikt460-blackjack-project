from Agents.q_agent import QAgent
import random
from Game.hand import Hand
from Game.card import Card


class MbveQAgent(QAgent):
    def __init__(self, rollout_depth=3):
        super().__init__()
        self.rollout_depth = rollout_depth

    def process_round_history_for_q_values(self, round_history_output, learning_rate=0.05, discount_factor=0.9):
        for player_index, hand_index, hand_history, outcome, dealer_face_up_card in round_history_output:
            if player_index not in self.q_tables:
                self.q_tables[player_index] = {}
            q_table = self.q_tables[player_index]

            for i, (cards, stake, action) in enumerate(hand_history):
                state = (tuple(sorted(self.get_possible_values_from_cards(cards))), dealer_face_up_card.value)
                action_key = action

                # MBVE target using short simulated rollouts
                mbve_target = self.simulate_rollout(cards, action, dealer_face_up_card, q_table, discount_factor)

                # Q-learning update
                if (state, action_key) not in q_table:
                    q_table[(state, action_key)] = 0.0
                old_q = q_table[(state, action_key)]
                new_q = old_q + learning_rate * (mbve_target - old_q)
                q_table[(state, action_key)] = new_q

    def simulate_rollout(self, cards, action, dealer_card, q_table, discount_factor):
        hand = Hand(cards.copy())
        deck = [Card(suit, value) for suit in range(1, 5) for value in range(1, 14)]
        random.shuffle(deck)

        reward_sum = 0.0
        gamma = 1.0

        self.simulated_action(hand, action, deck)

        if hand.busted_hand:
            return -hand.stake

        for step in range(1, self.rollout_depth):
            state = (tuple(sorted(self.get_possible_values_from_cards(hand.hand_cards))), dealer_card.value)
            valid_actions = self.get_valid_actions_from_cards(hand.hand_cards, dealer_card)
            if not valid_actions:
                break

            best_action = max(valid_actions, key=lambda a: q_table.get((state, a), 0.0))
            self.simulated_action(hand, best_action, deck)

            if hand.busted_hand:
                return reward_sum + gamma * -hand.stake

            gamma *= discount_factor

        # Final value bootstrapping
        final_state = (tuple(sorted(self.get_possible_values_from_cards(hand.hand_cards))), dealer_card.value)
        final_qs = [q_table.get((final_state, a), 0.0) for a in range(5)]
        reward_sum += gamma * max(final_qs)
        return reward_sum

    def simulated_action(self, hand, action, deck):
        try:
            if action == 0:
                hand.stand()
            elif action == 1:
                hand.hit(deck)
            elif action == 2:
                hand.double_down(deck)
            elif action == 3:
                hand.split(deck)
            elif action == 4:
                hand.do_insurance()
        except Exception:
            pass  # Ignore invalid actions in simulation
