from card import Card, Suit

class Hand:
    def __init__(self, hand_cards):
        self.hand_cards = hand_cards # Array of cards
        self.insurance = False
        self.is_standing = False
        self.value = 0
        self.stake = 0

    def hit(self, available_cards):
        if self.is_standing:
            raise Exception("Hit not allowed on standing hand")

        # Remove top card from game deck and add to current hand
        self.hand_cards.append(available_cards.pop())

        # TODO: Update hand value
        return

    def stand(self):
        self.is_standing = True
        return

    def double_down(self, available_cards):
        if self.is_standing:
            raise Exception("Hit not allowed on standing hand")
        elif len(self.hand_cards) != 2:
            raise Exception("Double down not allowed on a non-2-card hand")

        # Hit and then stand
        self.hit(available_cards)
        self.stand()
        return

    def split(self, available_cards):
        if self.is_standing:
            raise Exception("Hit not allowed on standing hand")
        elif len(self.hand_cards) != 2:
            raise Exception("Split not allowed on a non-2-card hand")
        elif self.hand_cards[0].value != self.hand_cards[1].value:
            raise Exception("Split not allowed on cards of non-equal value")

        # Split two cards into two separate hands
        split_card = self.hand_cards.pop() # Array of 2 cards
        new_hand = Hand([split_card])

        # Add extra card to old hand
        self.hit(available_cards)

        # Add extra card to new hand
        new_hand.hit(available_cards)
        return new_hand

    def insurance(self):
        # Logic for taking insurance
        return

    def get_hand_cards(self):
        return self.hand_cards

"""
# Test for hitting

deck = [Card(Suit.CLUBS, 10), Card(Suit.HEARTS, 2), Card(Suit.DIAMONDS, 7), Card(Suit.SPADES, 7)]
current_hand = Hand([])

print("Available cards before:")
for i in range(len(deck)):
    suit, value = deck[i].get_card()
    print(f"Card {i}: {suit.name}, {value}")

current_hand.hit(deck)
current_hand.hit(deck)
current_hand.hit(deck)

print("\nAvailable cards after:")
for i in range(len(deck)):
    suit, value = deck[i].get_card()
    print(f"Card {i}: {suit.name}, {value}")

print("\nFinal hand:")
for i in range(len(current_hand.get_hand_cards())):
    suit, value = current_hand.get_hand_cards()[i].get_card()
    print(f"Card {i}: {suit.name}, {value}")

"""


# Test for splitting

deck = [Card(Suit.CLUBS, 10), Card(Suit.HEARTS, 2), Card(Suit.DIAMONDS, 7), Card(Suit.SPADES, 7)]
hand_1 = Hand([Card(Suit.CLUBS, 9), Card(Suit.CLUBS, 9)])

print("Available cards before:")
for i in range(len(deck)):
    suit, value = deck[i].get_card()
    print(f"Card {i}: {suit.name}, {value}")

hand_2 = hand_1.split(deck)

print("\nAvailable cards after:")
for i in range(len(deck)):
    suit, value = deck[i].get_card()
    print(f"Card {i}: {suit.name}, {value}")

print("\nFinal hand 1:")
for i in range(len(hand_1.get_hand_cards())):
    suit, value = hand_1.get_hand_cards()[i].get_card()
    print(f"Card {i}: {suit.name}, {value}")

print("\nFinal hand 2:")
for i in range(len(hand_2.get_hand_cards())):
    suit, value = hand_2.get_hand_cards()[i].get_card()
    print(f"Card {i}: {suit.name}, {value}")