from dealer import Dealer
from card import Card, Suit

deck = [Card(Suit.CLUBS, 10), Card(Suit.HEARTS, 2), Card(Suit.DIAMONDS, 7), Card(Suit.SPADES, 7),
        Card(Suit.DIAMONDS, 9), Card(Suit.CLUBS, 9)]

dealer = Dealer()
dealer.hit(deck)
dealer.hit(deck)

dealer.deal_algorithm(deck)

print("End")
