import sys
import random
from cfr import CFRTrainer

class KuhnState:
    ACTION_NAMES = ["pass", "bet"]

    def __init__(self, cards=None, history="", actions="pb", current_player=0):
        self.cards = cards
        if self.cards is None:
            self.cards = random.sample((1, 2, 3), 2)
        self.history = history
        self.actions = actions
        self.current_player = current_player

    def is_terminal(self):
        return self.history in ("bp", "bb", "pp", "pbb", "pbp")

    def utility(self):
        if self.history in ("bp", "pbp"):
            return 1

        payoff = 2 if "b" in self.history else 1
        player_higher = self.cards[self.current_player] > self.cards[1-self.current_player]
        return payoff if player_higher else -payoff

    def handle_action(self, action):
        return KuhnState(self.cards[::], self.history+action, self.actions[::], 1-self.current_player)

    def get_representation(self):
        return f"{self.cards[self.current_player]}{self.history}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        iterations = 20000
    else:
        iterations = int(sys.argv[1])

    trainer = CFRTrainer(KuhnState)

    print(f"running for {iterations//10} iterations")
    trainer.train(iterations//10)
    print("resetting strategies")
    trainer.reset()
    print(f"running for {iterations} iterations")
    value = trainer.train(iterations, True)
    print(f"average value: {value/iterations}")

    for n in trainer.node_map.values():
        print(n)
