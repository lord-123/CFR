import random

PASS = 0
BET = 1
ACTION_C = 2
ACTION_NAMES = ["pass", "bet"]

node_map = {}

class Node:
    def __init__(self):
        self.infoset = ""

        self.regret_sum = [0 for _ in range(ACTION_C)]
        self.strategy = [None for _ in range(ACTION_C)]
        self.strategy_sum = [0 for _ in range(ACTION_C)]

    def get_strategy(self, realisation_weight):
        normalising_sum = 0

        for a in range(ACTION_C):
            self.strategy[a] = self.regret_sum[a] if self.regret_sum[a] > 0 else 0
            normalising_sum += self.strategy[a]

        for a in range(ACTION_C):
            if normalising_sum > 0:
                self.strategy[a] /= normalising_sum
            else:
                self.strategy[a] = 1/ACTION_C

            self.strategy_sum[a] += realisation_weight * self.strategy[a];

        return self.strategy

    def get_avg_strategy(self):
        avg_strategy = [None for _ in range(ACTION_C)]
        normalising_sum = 0

        for a in range(ACTION_C):
            normalising_sum += self.strategy_sum[a]
        for a in range(ACTION_C):
            if normalising_sum > 0:
                avg_strategy[a] = self.strategy_sum[a] / normalising_sum
            else:
                avg_strategy[a] = 1/ACTION_C

        return avg_strategy

    def __repr__(self):
        avg_strat = self.get_avg_strategy()
        r = f"{self.infoset}: ("
        for i in range(len(avg_strat)):
            r += f"{ACTION_NAMES[i]}: {avg_strat[i]:%}"
            if i != len(avg_strat)-1:
                r += ", "
        r += ")"
        return r

def cfr(cards, history, p0, p1):
    plays = len(history)
    player = plays % 2
    opponent = 1-player

    # terminal state
    if plays > 1:
        terminal_pass = history[plays-1] == "p"
        double_bet = history[plays-2:plays] == "bb"
        player_card_higher = cards[player] > cards[opponent]

        if terminal_pass:
            if history == "pp":
                return 1 if player_card_higher else -1
            else:
                return 1
        elif double_bet:
            return 2 if player_card_higher else -2

    infoset = f"{cards[player]}{history}"

    # get info on node or create it
    if infoset not in node_map:
        node = Node()
        node.infoset = infoset
        node_map[infoset] = node
    else:
        node = node_map[infoset]

    # call cfr with additional history and probability
    strategy = node.get_strategy(p0 if player == 0 else p1)
    util = [None for _ in range(ACTION_C)]
    node_util = 0

    for a in range(ACTION_C):
        next_history = history + ("p" if a == 0 else "b")
        if player == 0:
            util[a] = -cfr(cards, next_history, p0*strategy[a], p1)
        else:
            util[a] = -cfr(cards, next_history, p0, p1*strategy[a])
        node_util += strategy[a] * util[a]

    # compute counterfactual regret
    for a in range(ACTION_C):
        regret = util[a] - node_util
        node.regret_sum[a] += (p1 if player == 0 else p0) * regret

    return node_util

def train(iterations):
    cards = [1, 2, 3]
    util = 0

    for i in range(iterations):
        random.shuffle(cards)
        util += cfr(cards, "", 1, 1)
        if i % 10000 == 0:
            print("i:", i)

    print(f"Average game value: {util/iterations}")
    for n in node_map:
        print(node_map[n])

if __name__ == "__main__":
    train(1000000)
