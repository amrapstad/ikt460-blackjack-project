from dealer import Dealer
from card import Card, Suit


def deal_algorithm():
    deck = [Card(Suit.CLUBS, 10), Card(Suit.HEARTS, 2), Card(Suit.DIAMONDS, 7), Card(Suit.SPADES, 7),
            Card(Suit.DIAMONDS, 1), Card(Suit.CLUBS, 1), Card(Suit.HEARTS, 1)]

    dealer = Dealer()
    dealer.hit(deck)
    dealer.hit(deck)

    result = dealer.deal_algorithm(deck)

    print(f"Final value: {list(result)[0]}")

    return

def face_up_test():
    deck = [Card(Suit.CLUBS, 10), Card(Suit.HEARTS, 2), Card(Suit.DIAMONDS, 7), Card(Suit.SPADES, 7),
            Card(Suit.DIAMONDS, 1)]

    dealer = Dealer()
    dealer.initial_hand(deck)
    face_up = dealer.get_face_up_card().get_card()
    print("Dealer hand:")
    print(f"- Card 1: {face_up[0].name}, {face_up[1]}")
    print("- Card 2: ?")

# deal_algorithm()
face_up_test()