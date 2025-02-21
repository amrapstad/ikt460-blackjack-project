from Game.card import Card

class GameManager:

    # On initialize
    def __init__(self, deckCount):
        self.availalbeCards = []
        self.createDecks(deckCount=deckCount)

        # For testing
        for card in self.availalbeCards:
            suit, value = card.getCard()
            print(f"Suit: {suit}, Value: {value}")


    def createDecks(self, deckCount):
        for i in range(deckCount):
            for suit in ["S", "D", "C", "H"]:
                self.availalbeCards.extend(Card(suit, n+1) for n in range(13))
            return