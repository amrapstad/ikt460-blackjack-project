import random

class RandomAgent:
    def choose_action(self, player_hand, dealer_face_up_card):
        return self.get_random_valid_action(player_hand.hand_cards, dealer_face_up_card)

    def get_random_valid_action(self, cards, dealer_card):
        valid_actions = [0, 1]

        if len(cards) == 2:
            valid_actions.append(2) 
            val1 = min(cards[0].value, 10)
            val2 = min(cards[1].value, 10)
            if val1 == val2:
                valid_actions.append(3) 

        if dealer_card.value == 1:
            valid_actions.append(4)

        return random.choice(valid_actions)
