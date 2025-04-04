from Game.hand import Hand

class Player:
    def __init__(self):
        self.hands = []
        self.default_bet = 10

    def initial_hand(self, available_cards):
        new_hand = Hand(hand_cards=[], initial_bet=self.default_bet)
        for i in range(2):
            new_hand.hit(available_cards)
        self.hands.append(new_hand)

    def action_input(self, hand, action, available_cards):
        if action == 0:
            self.hands[hand].stand()
        if action == 1:
            self.hands[hand].hit(available_cards)
        if action == 2:
            self.hands[hand].double_down(available_cards)
        if action == 3:
            new_hand = self.hands[hand].split(available_cards)
            print("New hand added to player hands")
            self.hands.append(new_hand)
        if action == 4:        
            self.hands[hand].insurance()
        return
