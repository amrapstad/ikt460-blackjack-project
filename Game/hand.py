from card import Card, Suit

class Hand:
    def __init__(self, hand_cards):
        self.hand_cards = hand_cards
        self.insurance = False
        self.double_down = False

    def hit(self, available_cards):
        # Remove top card from game deck and add to current hand
        self.hand_cards.append(available_cards.pop())
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