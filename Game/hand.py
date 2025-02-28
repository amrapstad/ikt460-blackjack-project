class Hand:
    def __init__(self, hand_cards):
        self.hand_cards = hand_cards
        self.insurance = False
        self.double_down = False

    def hit(self):
        # logic for hitting
        return

    def stand(self):
        # Logic for standing
        return

    def double_down(self):
        # Logic for doubling down
        return

    def split(self):
        # Logic for splitting
        return

    def insurance(self):
        # Logic for taking insurance
        return

    def get_hand_cards(self):
        return self.hand_cards