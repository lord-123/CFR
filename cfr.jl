export CFR

module CFR
using Random
using Printf
using JLD2
using FileIO

export CFRTrainer
export Node
export Game
export train!
export reset_nodes
export print_nodes
export save_training_to_file
export load_training_from_file
export play_ai

normalise(v) = (s=sum(v); s>0 ? map(x -> x/s, v) : map(x -> 1/length(v), v))

struct Node
    infoset
    actions

    action_c
    regret_sum
    strategy_sum
end

function create_node(infoset, actions)
    action_c = length(actions)
    Node(infoset, actions, action_c, zeros(action_c), zeros(action_c))
end

function get_strategy!(node, realisation_weight)
    strategy = normalise(map(x -> max(x, 0), node.regret_sum))

    node.strategy_sum .+= (realisation_weight .* strategy)

    strategy
end

get_avg_strategy(node) = normalise(node.strategy_sum)

struct Game
    action_names
    initial_state
    is_terminal
    get_utility
    handle_action
    get_representation
    player_c
end

struct CFRTrainer
    game
    node_map
end

function reset_nodes(trainer)
    for (k, v) in trainer.node_map
        fill!(v.strategy_sum, 0)
    end
end

function get_node(trainer, state)
    infoset = trainer.game.get_representation(state)
    if haskey(trainer.node_map, infoset)
        node = trainer.node_map[infoset]
    else
        node = create_node(infoset, state.actions)
        trainer.node_map[infoset] = node
    end
    node
end

get_cf_reach_prob(probs, player) = prod(probs[1:player-1])*prod(probs[player+1:end])

function cfr!(trainer, state, probabilities)
    if trainer.game.is_terminal(state)
        return trainer.game.get_utility(state)
    end

    if probabilities[state.current_player] < 0.001
        return 0
    end

    node = get_node(trainer, state)
    strategy = get_strategy!(node, probabilities[state.current_player])
    util = zeros(node.action_c)

    for i in eachindex(state.actions)
        new_probs = copy(probabilities)
        new_probs[state.current_player] *= strategy[i]

        new_state = trainer.game.handle_action(state, state.actions[i])
        util[i] = -cfr!(trainer, new_state, new_probs)
    end
    node_util = sum(strategy .* util)

    previous = copy(node.regret_sum)
    cf_reach_prob = get_cf_reach_prob(probabilities, state.current_player)
    node.regret_sum .+= (cf_reach_prob * (util .- node_util))

    node_util
end

function train!(trainer, iterations, verbose=false)
    util = 0
    for i in 1:iterations
        util += cfr!(trainer, trainer.game.initial_state(), [1. for _ in 1:trainer.game.player_c])
        if i%10000==0 && verbose
            println("i: ", i)
        end
    end
    util
end

function print_nodes(trainer)
    for (key, node) in trainer.node_map
        print(key, ": [ ")
        strategy = get_avg_strategy(node)
        for i in 1:node.action_c
            print(trainer.game.action_names[node.actions[i]], " ")
            @printf("%.2f%% ", strategy[i]*100)
        end
        println("]")
    end
end

function save_training_to_file(trainer, filename)
    save(filename*".jld2", "data", trainer.node_map)
end

function load_training_from_file(game, filename)
    node_map = load(filename*".jld2")["data"]
    CFRTrainer(game, node_map)
end

get_action = (node) -> findfirst(cumsum(get_avg_strategy(node)).>=rand())

function play_ai(trainer)
    state = trainer.game.initial_state()
    while !trainer.game.is_terminal(state)
        println("current player: ", state.current_player)
        if state.current_player == 1
            action = state.actions[get_action(trainer.node_map[trainer.game.get_representation(state)])]
        else
            println("game state: ", trainer.game.get_representation(state))
            print("choose an action: ", state.actions, " ")
            action = state.actions[parse(Int, readline())]
        end
        println("player ", state.current_player, " ", action)
        state = trainer.game.handle_action(state, action)
    end
    println("utility: ", trainer.game.get_utility(state))
end

end

