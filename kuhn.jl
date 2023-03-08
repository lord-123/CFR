include("cfr.jl")
using .CFR
using Random

struct KuhnState
    cards
    history
    actions
    current_player
end

function kuhn_utility(state)
    if state.history in ["bp", "pbp"]
        return 1
    end

    payoff = 'b' in state.history ? 2 : 1
    player_higher = all(state.cards[state.current_player] .>= state.cards[1:2])
    player_higher ? payoff : -payoff
end

kuhn = Game(
    Dict('p' => "pass", 'b' => "bet"),
    () -> KuhnState(shuffle([1,2,3])[1:2], "", "pb", 1),
    (state) -> state.history in ["bp", "bb", "pp", "pbb", "pbp"],
    kuhn_utility,
    (state, action) -> KuhnState(state.cards, state.history*action, state.actions, [2,1][state.current_player]),
    (state) -> string(state.cards[state.current_player],state.history),
    2
)

t = CFRTrainer(kuhn, Dict())
if length(ARGS) > 0
    iterations = parse(Int, ARGS[1])
else
    iterations = 20000
end
println("running for ", iterations÷10, " iterations")
train!(t, iterations÷10)
println("resetting strategies")
reset_nodes(t)
println("running for ", iterations, " iterations")
@time "time tyaken " total_value = train!(t, iterations, true)
print_nodes(t)
println("average game value: ", total_value/iterations)
