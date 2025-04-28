import pandas as pd
from optimal_agent import OptimalAgent, get_action_from_csv
from Game.card import Card, Suit
from Game.hand import Hand

temp = {
    0: "Stand",
    1: "Hit",
    2: "Double down",
    3: "Split"
}

agent = OptimalAgent()

hand_1 = Hand([Card(Suit.CLUBS, 1), Card(Suit.HEARTS, 1)]) # Split
hand_2 = Hand([Card(Suit.CLUBS, 1), Card(Suit.HEARTS, 3), Card(Suit.SPADES, 4)]) # Soft
hand_3 = Hand([Card(Suit.CLUBS, 2), Card(Suit.HEARTS, 4)]) # Hard
hand_4 = Hand([Card(Suit.CLUBS, 2), Card(Suit.HEARTS, 10)], Card(Suit.SPADES, 1))# Hard with ace

face_up = Card(Suit.CLUBS, 9)


result = agent.choose_action(hand_4, face_up)
print(temp[result])