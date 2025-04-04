class Dealer:
    def __init__(self):
        self.dealer_cards = []
        self.possible_values = []
        self.face_up_card = None

        self.busted_hand = False
        self.is_standing = False

        self.calculate_hand_values()

    # Get two cards for the initial hand and make the first card dealt the face up card
    def initial_hand(self, available_cards):
        face_up_card = available_cards.pop()
        hole_card = available_cards.pop()

        self.face_up_card = face_up_card

        self.dealer_cards.append(face_up_card)
        self.dealer_cards.append(hole_card)

        self.calculate_hand_values()

    def get_possible_values(self):
        self.calculate_hand_values()
        return self.possible_values

    def hit(self, available_cards):
        if self.is_standing:
            raise Exception("Hit not allowed on standing hand")

        hit_card = available_cards.pop()
        self.dealer_cards.append(hit_card)
        self.calculate_hand_values()
        return hit_card

    def stand(self):
        self.is_standing = True
        self.calculate_hand_values()
        return

    def calculate_hand_values(self):
        total_values = [0]
        for card in self.dealer_cards:
            # Get last element which is the card value
            card_value = card.get_card()[-1]

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

        # Check for busted hand by checking the lowest hand value
        if min(total_values) > 21:
            self.busted_hand = True

        self.possible_values = total_values
        return

    # Maybe change this name?
    def deal_algorithm(self, available_cards):
        """
        Performs the predefined dealer actions when dealing to itself.

        :param available_cards: Card array. The deck used in this round of Blackjack.
        :return: Dictionary (int: Card array). Group of the final value and the final hand after deal algorithm.
        """
        # Update hand and its values
        self.calculate_hand_values()
        ace_present = len(self.possible_values) > 1
        play_value = self.calculate_play_value() # The value being used to determine the final score

        # If play value is below 17 or is 17 with an ace, hit. Else stand
        while play_value < 17 or (play_value == 17 and ace_present):
            self.hit(available_cards) # Hit to get new card

            # Then update hand and values
            self.calculate_hand_values()
            ace_present = len(self.possible_values) > 1
            play_value = self.calculate_play_value()

        final_value = play_value
        final_hand = self.dealer_cards
        final = { final_value: final_hand} # Dictionary. Key --> hand value, Value --> card array

        return final

    def calculate_play_value(self):
        number_of_values = len(self.possible_values)
        index = number_of_values - 1
        play_value = self.possible_values[index]

        while index > 0 and play_value > 21:
            index -= 1
            play_value = self.possible_values[index]

        return play_value
