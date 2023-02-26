import random
import sys

sys.setrecursionlimit(2000)

NUM_SIDES = 6
NUM_ACTIONS = (2 * NUM_SIDES) + 1
DUDO = NUM_ACTIONS - 1

CLAIM_NUM  = [1,1,1,1,1,1,2,2,2,2,2,2]
CLAIM_RANK = [2,3,4,5,6,1,2,3,4,5,6,1]

node_map = {}

class Node:
    def __init__(self):
        self.infoset = 0

        self.regret_sum = [0 for _ in range(NUM_ACTIONS)]
        self.strategy = [None for _ in range(NUM_ACTIONS)]
        self.strategy_sum = [0 for _ in range(NUM_ACTIONS)]

    def get_strategy(self, realisation_weight):
        normalising_sum = 0

        for a in range(NUM_ACTIONS):
            self.strategy[a] = self.regret_sum[a] if self.regret_sum[a] > 0 else 0
            normalising_sum += self.strategy[a]

        for a in range(NUM_ACTIONS):
            if normalising_sum > 0:
                self.strategy[a] /= normalising_sum
            else:
                self.strategy[a] = 1/NUM_ACTIONS

            self.strategy_sum[a] += realisation_weight * self.strategy[a];

        return self.strategy

    def get_avg_strategy(self):
        avg_strategy = [None for _ in range(NUM_ACTIONS)]
        normalising_sum = 0

        for a in range(NUM_ACTIONS):
            normalising_sum += self.strategy_sum[a]
        for a in range(NUM_ACTIONS):
            if normalising_sum > 0:
                avg_strategy[a] = self.strategy_sum[a] / normalising_sum
            else:
                avg_strategy[a] = 1/NUM_ACTIONS

        return avg_strategy

    def __repr__(self):
        avg_strat = self.get_avg_strategy()
        r = f"{self.infoset} {str_infoset(self.infoset)}: ("
        for i, x in enumerate(avg_strat):
            if i > 0:
                r += " "
            if i == DUDO:
                r += f"DUDO: {x:%}"
            else:
                r += f"{CLAIM_NUM[i]}x{CLAIM_RANK[i]}: {x:%}"
        r += ")"
        return r

def infoset_to_history(infoset):
    history = []
    for a in range(NUM_ACTIONS-2, 0, -1):
        history += [infoset&1]
        infoset //= 2
    return history

def str_infoset(infoset):
    history = [0 for _ in range(NUM_ACTIONS-1)]
    for a in range(NUM_ACTIONS-2, 0, -1):
        if infoset&1==1:
            history[NUM_ACTIONS-a-1] = 1
        infoset //= 2
    return f"{infoset} {history}"

def int_infoset(roll, claimed):
    num = roll
    for a in range(NUM_ACTIONS-2, 0, -1):
        num *= 2
        if claimed[a]: num += 1
    return num

def cfr(dice, history, p0, p1):
    plays = sum(history)
    player = plays % 2
    opponent = 1-player

    recent_play = 0
    for i, x in enumerate(history):
        if x and i != DUDO: recent_play = i

    # check for terminal state
    if plays >= 1 and history[DUDO]:
        claimed_num = CLAIM_NUM[recent_play]
        claimed_rank = CLAIM_RANK[recent_play]

        real_num = len(list(filter(lambda x: x==claimed_rank or x==1, dice)))

        return 1 if real_num >= claimed_num else -1

    infoset = int_infoset(dice[player], history)

    # get node info
    if infoset not in node_map:
        node = Node()
        node.infoset = infoset
        node_map[infoset] = node
    else:
        node = node_map[infoset]

    # CFR
    max_action = NUM_ACTIONS + (0 if plays > 0 else -1)
    strategy = node.get_strategy(p0 if player == 0 else p1)
    util = [None for _ in range(NUM_ACTIONS)]
    node_util = 0

    for a in range(recent_play+1, max_action):
        next_history = history[::]
        next_history[a] = True

        if player == 0:
            util[a] = -cfr(dice, next_history, p0*strategy[a], p1)
        else:
            util[a] = -cfr(dice, next_history, p0, p1*strategy[a])
        node_util += strategy[a] * util[a]

    # compute counterfactual regret
    for a in range(recent_play+1, max_action):
        regret = util[a] - node_util
        node.regret_sum[a] += (p1 if player == 0 else p0) * regret

    return node_util

def train(iterations):
    dice = []
    util = 0

    for i in range(iterations):
        #print(i)
        dice = (random.randint(1, NUM_SIDES), random.randint(1, NUM_SIDES))
        util += cfr(dice, [False for _ in range(NUM_ACTIONS)], 1, 1)
        if i % 100 == 0:
            print("i:", i)

    print(f"Average game value: {util/iterations}")
    for n in node_map:
        print(node_map[n])

if __name__ == "__main__":
    train(5000)
