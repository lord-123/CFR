def normalise(strategy):
    s = sum(strategy)
    if s > 0: return [a/s for a in strategy]
    else: return [1/len(strategy)] * len(strategy)

class Node:
    def __init__(self, infoset, actions):
        self.infoset = infoset
        self.actions = actions

        self.action_c = len(actions)
        self.regret_sum = [0] * self.action_c
        self.strategy_sum = [0] * self.action_c

    def get_strategy(self, realisation_weight):
        strategy = [max(a, 0) for a in self.regret_sum]
        strategy = normalise(strategy)

        for a in range(self.action_c):
            self.strategy_sum[a] += realisation_weight * strategy[a]

        return strategy

    def get_avg_strategy(self):
        return normalise(self.strategy_sum[::])

    def __repr__(self):
        return f"{self.infoset}: (" + ", ".join(f"{a:%}" for a in self.get_avg_strategy()) + ")"

class CFRTrainer:
    def __init__(self, initialstate, player_c=2):
        self.action_names = initialstate.ACTION_NAMES
        self.node_map = {}
        self.initialstate = initialstate
        self.player_c = player_c

    def reset(self):
        for n in self.node_map.values():
            n.strategy_sum=[0]*n.action_c

    def get_node(self, state):
        infoset = state.get_representation()
        if infoset not in self.node_map:
            self.node_map[infoset] = Node(infoset, state.actions)
        return self.node_map[infoset]

    def get_cf_reach_prob(self, probs, player):
        m = 1
        for i, x in enumerate(probs):
            if i == player:
                pass
            m *= x
        return m

    def cfr(self, state, probabilities):
        if state.is_terminal():
            return state.utility()

        node = self.get_node(state)
        strategy = node.get_strategy(probabilities[state.current_player])
        util = [0] * node.action_c
        node_util = 0

        for i, x in enumerate(state.actions):
            new_probabilities = probabilities[::]
            new_probabilities[state.current_player] *= strategy[i]

            util[i] = -self.cfr(state.handle_action(x), new_probabilities)
            node_util += strategy[i] * util[i]

        for i, x in enumerate(state.actions):
            cf_reach_prob = self.get_cf_reach_prob(probabilities, state.current_player)
            regrets = util[i] - node_util
            node.regret_sum[i] += cf_reach_prob * regrets

        return node_util

    def train(self, iterations, verbose=False):
        util = 0
        for i in range(iterations):
            util += self.cfr(self.initialstate(), [1] * self.player_c)
            if i % 10000 ==0 and verbose:
                print(f"i:  {i}")
        return util

    def print_nodes(self):
        for n in self.node_map:
            probs = ", ".join(
                f"{self.action_names[name]} {prob:%}"
                for name, prob in
                zip(self.node_map[n].actions,
                    self.node_map[n].get_avg_strategy()))
            print(f"{self.initialstate.translate_representation(n)}: ({probs})")

        for h in self.initialstate.marked_terminal:
            print(self.initialstate.history_string(h), abs(self.initialstate(history=h, current_player=sum(len(x) for x in h)%2).utility()))
