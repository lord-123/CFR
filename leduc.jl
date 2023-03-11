include("cfr.jl")
using .CFR
using Random

@enum Actions BET RAISE CALL CHECK FOLD

RANKS = Dict(
    (3,3) => 1,
    (2,2) => 2,
    (1,1) => 3,
    (3,2) => 4, (2, 3) => 4,
    (3,1) => 5, (1, 3) => 5,
    (2,1) => 6, (1, 2) => 6,
)

struct LeducState
    cards::Vector{Int8}
    history::Vector{Actions}
    actions::Vector{Actions}
    current_player::Int8
end

function leduc_terminal(state)
    if length(state.history) < 1 return false end

    recent_action = state.history[end]
    if recent_action == FOLD return true end
    if count(==(CALL), state.history) == 2 return true end

    false
end

function leduc_utility(state)
    player = 1
    stakes = [1,1]
    round = 1
    #println(state.history, " ", typeof(state.history))
    for a in state.history
        wager = 2*round
        if a == BET
            stakes[player] += wager
        elseif a == CALL
            stakes[player] = maximum(stakes)
            round += 1
        elseif a == RAISE
            stakes[player] = maximum(stakes)+wager
        end
        player = player%2+1
    end
    util = sum(stakes)-stakes[state.current_player]

    if state.history[end] == FOLD
        return util
    end

    hands = [(card, state.cards[3]) for card in state.cards[1:2]]
    if RANKS[hands[state.current_player]] < RANKS[hands[state.current_player%2+1]]
        return util
    else
        return -util
    end
end

function handle_leduc_action(state, action)
    new_actions = Dict(
        BET => [RAISE, CALL, FOLD],
        RAISE => [CALL, FOLD],
        CHECK => [BET, CALL],
        CALL => [BET, CHECK],
        FOLD => []
    )[action]

    LeducState(
        state.cards,
        [state.history..., action],
        new_actions,
        state.current_player%2+1,
    )
end

leduc = Game(
    Dict(
        BET => "bet",
        RAISE => "raise",
        CALL => "call",
        CHECK => "check",
        FOLD => "fold"
    ),
    () -> LeducState(shuffle([1,1,2,2,3,3][1:3]), [], [BET, CHECK], 1),
    leduc_terminal,
    leduc_utility,
    (state, action) -> handle_leduc_action(state, action),
    (state) -> (state.cards[state.current_player], state.history),
    2
)

#=t = CFRTrainer(leduc, Dict())
iterations = 20000
if length(ARGS) > 0
    iterations = parse(Int, ARGS[1])
end
println("running for ", iterations÷10, " iterations")
train!(t, iterations÷10)
println("resetting strategies")
reset_nodes(t)
println("running for ", iterations, " iterations")
@time "time taken " total_value = train!(t, iterations, true)
print_nodes(t)
println("average game value: ", total_value/iterations)
save_training_to_file(t, "leduc")
=#
t = load_training_from_file(leduc, "leduc")
play_ai(t)
