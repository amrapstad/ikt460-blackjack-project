from dealer import Dealer
from card import Card, Suit

deck = [Card(Suit.CLUBS, 10), Card(Suit.HEARTS, 2), Card(Suit.DIAMONDS, 7), Card(Suit.SPADES, 7),
        Card(Suit.DIAMONDS, 1), Card(Suit.CLUBS, 1), Card(Suit.HEARTS, 1)]

dealer = Dealer()
dealer.hit(deck)
dealer.hit(deck)

result = dealer.deal_algorithm(deck)

print(f"Final value: {list(result)[0]}")
