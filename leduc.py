import random
import sys
from cfr import CFRTrainer

RANKS = {
    (3,3): 1,
    (2,2): 2,
    (1,1): 3,
    (3,2): 4, (2, 3): 4, 3: 4,
    (3,1): 5, (1, 3): 5, 2: 5,
    (2,1): 6, (1, 2): 6, 1: 6
}

BET = 0
RAISE = 1
CALL = 2
CHECK = 3
FOLD = 4

ACTION_NAMES = [
    "bet", "raise", "call", "check", "fold"
]

class LeducState:
    ACTION_NAMES = [ "bet", "raise", "call", "check", "fold" ]

    marked_terminal = {}

    def __init__(self, cards=None, history=tuple([tuple()]), actions=(BET, CHECK), current_player=0):
        self.cards = cards
        if self.cards is None:
            self.cards = random.sample((1, 1, 2, 2, 3, 3), 3)
        self.history = history
        self.actions = actions
        self.current_player = current_player

    def is_terminal(self):
        if len(self.history[-1]) < 1: return False
        recent_action = self.history[-1][-1]
        if recent_action == FOLD:
            self.marked_terminal[self.history]=True
            return True
        if len(self.history) > 1 and recent_action == CALL:
            self.marked_terminal[self.history]=True
            return True
        return False

    def utility(self):
        player = 0
        stakes = [1, 1]
        for i, betting_round in enumerate(self.history, 1):
            wager = 2 * i
            for a in betting_round:
                if a == BET:
                    stakes[player] += wager
                elif a == CALL:
                    stakes[player] = max(stakes)
                elif a == RAISE:
                    stakes[player] = max(stakes)+wager
                player=1-player
        assert (player == self.current_player)
        util = sum(stakes)-stakes[self.current_player]

        if self.history[-1][-1] == FOLD:
            return util

        hands = [(self.cards[i], self.cards[2]) for i in range(2)]
        if RANKS[hands[self.current_player]] < RANKS[hands[1-self.current_player]]:
            return util
        else:
            return -util

    def handle_action(self, action):
        new_actions = {
            BET:   (RAISE, CALL, FOLD),
            RAISE: (CALL, FOLD),
            CHECK: (BET, CALL),
            CALL:  (BET, CHECK), #new round
            FOLD:  tuple()
        }[action]

        if action == CALL and len(self.history) < 2:
            new_history = (*self.history, [action])
            new_history = (*self.history[:-1], (*self.history[-1], action), tuple([]))
        else:
            new_history = (*self.history[:-1], (*self.history[-1], action))

        return LeducState(
            cards = self.cards[::],
            history = new_history,
            actions = new_actions,
            current_player = 1-self.current_player,
        )

    def get_representation(self):
        preflop = len(self.history) == 1
        if preflop:
            community = None
        else:
            community = self.cards[2]

        return (self.cards[self.current_player], community, self.history)

    @staticmethod
    def translate_representation(r):
        rank, community, history = r
        s = f"({rank}, {community}, {LeducState.history_string(history)})"
        return s

    @staticmethod
    def history_string(history):
        s = "("
        for h in history:
            s += "("
            s += ", ".join([ACTION_NAMES[a] for a in h])
            s += ")"
        s += ")"
        return s

if __name__ == "__main__":
    if len(sys.argv) < 2:
        iterations = 20000
    else:
        iterations = int(sys.argv[1])

    trainer = CFRTrainer(LeducState)

    print(f"running for {iterations//10} iterations")
    trainer.train(iterations//10)
    print("resetting strategies")
    trainer.reset()
    print(f"running for {iterations} iterations")
    value = trainer.train(iterations, True)

    trainer.print_nodes()
    print(f"average game value: {value/iterations}")
