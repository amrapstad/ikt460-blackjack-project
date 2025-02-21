class Card:
    def __init__(self, suit, value):
        self.Suit = suit
        self.Value = value
        return
    
    def getCard(self):
        return (self.Suit, self.Value)