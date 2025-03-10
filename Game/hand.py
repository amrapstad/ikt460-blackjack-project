class Hand:
    def __init__(self, hand_cards, initial_bet = 0):
        self.hand_cards = hand_cards # Array of cards
        self.insurance = False
        self.is_standing = False
        self.possible_values = [] # Array of possible values a hand can be (because of ace)
        self.calculate_hand_values()
        self.stake = initial_bet

    def hit(self, available_cards):
        if self.is_standing:
            raise Exception("Hit not allowed on standing hand")

        # Remove top card from game deck and add to current hand
        self.hand_cards.append(available_cards.pop())

        # Update hand value on new card
        self.calculate_hand_values()
        return

    def stand(self):
        self.is_standing = True
        self.calculate_hand_values()
        return

    def double_down(self, available_cards):
        if self.is_standing:
            raise Exception("Hit not allowed on standing hand")
        elif len(self.hand_cards) != 2:
            raise Exception("Double down not allowed on a non-2-card hand")

        # Hit and then stand, doubling the current stake on the hand
        self.hit(available_cards)
        self.stand()
        self.stake *= 2
        return

    def split(self, available_cards):
        if self.is_standing:
            raise Exception("Hit not allowed on standing hand!")
        elif len(self.hand_cards) != 2:
            raise Exception(f"Split not allowed on hand with {len(self.hand_cards)} cards!")
        elif self.hand_cards[0].value != self.hand_cards[1].value:
            raise Exception("Split not allowed on cards of non-equal value")

        # Split two cards into two separate hands
        split_card = self.hand_cards.pop() # Array of 2 cards
        new_hand = Hand([split_card], self.stake)

        # Add extra card to old hand
        self.hit(available_cards)

        # Add extra card to new hand
        new_hand.hit(available_cards)
        return new_hand

    def insurance(self):
        # Logic for taking insurance
        # TODO: Implement insurance

        
        return

    def get_hand_cards(self):
        return self.hand_cards

    def calculate_hand_values(self):
        total_values = [0]

        for card in self.hand_cards:
            card_value = card.get_card()[-1] # Get last element which is the card value

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
