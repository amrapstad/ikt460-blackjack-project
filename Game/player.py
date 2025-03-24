from Game.hand import Hand

class Player:
    def __init__(self):
        self.hands = []

    def initial_hand(self, available_cards):
        new_hand = Hand(hand_cards=[])
        for i in range(2):
            new_hand.hit(available_cards)
        self.hands.append(new_hand)

    def get_hands(self):
        return self.hands
