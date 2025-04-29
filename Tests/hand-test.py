from Game.card import Card, Suit
from Game.hand import Hand

# Test for hitting
def test_for_hitting():
    deck = [Card(Suit.CLUBS, 10), Card(Suit.HEARTS, 2), Card(Suit.DIAMONDS, 7), Card(Suit.SPADES, 7)]
    current_hand = Hand([])
    
    print("Available cards before:")
    for i in range(len(deck)):
        suit, value = deck[i].get_card()
        print(f"Card {i}: {suit.name}, {value}")

    print("\nHitting three times...")
    current_hand.hit(deck)
    current_hand.hit(deck)
    current_hand.hit(deck)
    
    print("\nAvailable cards after:")
    for i in range(len(deck)):
        suit, value = deck[i].get_card()
        print(f"Card {i}: {suit.name}, {value}")
    
    print("\nFinal hand:")
    for i in range(len(current_hand.hand_cards)):
        suit, value = current_hand.hand_cards[i].get_card()
        print(f"Card {i}: {suit.name}, {value}")
    
    return

# Test for splitting
def test_for_splitting():
    deck = [Card(Suit.CLUBS, 10), Card(Suit.HEARTS, 2), Card(Suit.DIAMONDS, 7), Card(Suit.SPADES, 7), Card(Suit.DIAMONDS, 10), Card(Suit.CLUBS, 12)]
    hand_1 = Hand([])
    
    print("Available cards before:")
    for i in range(len(deck)):
        suit, value = deck[i].get_card()
        print(f"Card {i}: {suit.name}, {value}")

    print("\nHitting two times...")
    hand_1.hit(deck)
    hand_1.hit(deck)

    print("\nCurrent hand:")
    for i in range(len(hand_1.hand_cards)):
        suit, value = hand_1.hand_cards[i].get_card()
        print(f"Card {i}: {suit.name}, {value}")

    print("\nSplitting current hand...")
    hand_2 = hand_1.split(deck)
    
    print("\nAvailable cards after:")
    for i in range(len(deck)):
        suit, value = deck[i].get_card()
        print(f"Card {i}: {suit.name}, {value}")
    
    print("\nFinal hand 1:")
    for i in range(len(hand_1.hand_cards)):
        suit, value = hand_1.hand_cards[i].get_card()
        print(f"Card {i}: {suit.name}, {value}")
    
    print("\nFinal hand 2:")
    for i in range(len(hand_2.hand_cards)):
        suit, value = hand_2.hand_cards[i].get_card()
        print(f"Card {i}: {suit.name}, {value}")
    
    return

# Test for hand values
def test_for_hand_values():
    #hand = Hand([Card(Suit.CLUBS, 9), Card(Suit.HEARTS, 1), Card(Suit.SPADES, 1), Card(Suit.CLUBS, 2)])
    hand = Hand([Card(Suit.CLUBS, 2), Card(Suit.HEARTS, 3), Card(Suit.SPADES, 1)])

    print("\nHand:")
    for i in range(len(hand.hand_cards)):
        suit, value = hand.hand_cards[i].get_card()
        print(f"Card {i}: {suit.name}, {value}")

    print(hand.get_possible_values())

    return

# test_for_hitting()
# test_for_splitting()
# test_for_hand_values()
