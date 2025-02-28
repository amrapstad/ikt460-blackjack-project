from Game.card import Card

class GameManager:

    # On initialize
    def __init__(self, deck_count):
        self.availalbe_cards = []
        self.create_decks(deck_count=deck_count)

        # For testing
        for card in self.availalbe_cards:
            suit, value = card.get_card()
            print(f"Suit: {suit}, Value: {value}")


    def create_decks(self, deck_count):
        for i in range(deck_count):
            for suit in ["S", "D", "C", "H"]:
                self.availalbe_cards.extend(Card(suit, n+1) for n in range(13))
            return