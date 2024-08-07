import random
import json

EMPTY = 0
X = 1
O = -1
SIZE = 3

POPULATION_SIZE = 500
MAX_GENERATIONS = 1000
CROSSOVER_RATE = 0.15
REPLICATION_RATE = 0.10
MUTATION_RATE = 0.01
STRATEGY_FILE = "tic_tac_toe_strategy.json"

def initialize_board():
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]

def check_winner(board):
    for i in range(SIZE):
        if abs(sum(board[i])) == SIZE:
            return board[i][0]
        if abs(sum(row[i] for row in board)) == SIZE:
            return board[0][i]
    if abs(sum(board[i][i] for i in range(SIZE))) == SIZE:
        return board[0][0]
    if abs(sum(board[i][SIZE-i-1] for i in range(SIZE))) == SIZE:
        return board[0][SIZE-1]
    return None

def is_draw(board):
    return all(cell != EMPTY for row in board for cell in row)

def make_move(board, row, col, player):
    if board[row][col] == EMPTY:
        board[row][col] = player
        return True
    return False

def get_possible_moves(board):
    return [(i, j) for i in range(SIZE) for j in range(SIZE) if board[i][j] == EMPTY]

def rotate_board(board):
    return [[board[SIZE - j - 1][i] for j in range(SIZE)] for i in range(SIZE)]

def reflect_board(board):
    return [list(reversed(row)) for row in board]

def all_symmetries(board):
    symmetries = []
    current_board = board
    for _ in range(4):
        symmetries.append(current_board)
        symmetries.append(reflect_board(current_board))
        current_board = rotate_board(current_board)
    return symmetries

def canonical_form(board):
    symmetries = all_symmetries(board)
    flattened_boards = [tuple(cell for row in sym for cell in row) for sym in symmetries]
    return min(flattened_boards)

def board_to_state(board_tuple):
    state = 0
    for cell in board_tuple:
        state = state * 3 + (cell + 1)
    return state

canonical_cache = {}
for state in range(3 ** (SIZE * SIZE)):
    board_tuple = [(state // (3 ** i)) % 3 - 1 for i in range(SIZE * SIZE)]
    board = [board_tuple[i*SIZE:(i+1)*SIZE] for i in range(SIZE)]
    canonical_cache[state] = board_to_state(canonical_form(board))

def board_to_canonical_state(board):
    board_tuple = tuple(cell for row in board for cell in row)
    state = board_to_state(board_tuple)
    return canonical_cache[state]

def generate_random_strategy():
    strategy = {}
    for state in range(3 ** (SIZE * SIZE)):
        board_tuple = [(state // (3 ** i)) % 3 - 1 for i in range(SIZE * SIZE)]
        board = [board_tuple[i*SIZE:(i+1)*SIZE] for i in range(SIZE)]
        valid_moves = get_possible_moves(board)
        if valid_moves:
            canonical_state = canonical_cache[state]
            strategy[canonical_state] = random.choice(valid_moves)
    return strategy

def play_game(strategy, opponent_strategy):
    board = initialize_board()
    current_player = X
    while True:
        state = board_to_canonical_state(board)
        possible_moves = get_possible_moves(board)
        if current_player == X:
            move = strategy.get(state, random.choice(possible_moves))
        else:
            move = opponent_strategy.get(state, random.choice(possible_moves))

        if move not in possible_moves:
            return -current_player

        make_move(board, move[0], move[1], current_player)

        winner = check_winner(board)
        if winner is not None:
            return winner
        if is_draw(board):
            return 0
        current_player = -current_player

def evaluate_fitness(strategy, opponents):
    n_total = 0
    n_lost = 0
    for opponent in opponents:
        result = play_game(strategy, opponent)
        n_total += 1
        if result == O:
            n_lost += 1
    return (n_total - n_lost) / n_total

def select_parents(population, fitness_scores):
    total_fitness = sum(fitness_scores)
    selection_probs = [score / total_fitness for score in fitness_scores]
    parents = random.choices(population, weights=selection_probs, k=len(population))
    return parents

def crossover(parent1, parent2):
    child1, child2 = {}, {}
    for key in parent1:
        if random.random() < CROSSOVER_RATE:
            child1[key], child2[key] = parent2[key], parent1[key]
        else:
            child1[key], child2[key] = parent1[key], parent2[key]
    return child1, child2

def mutate(strategy):
    if random.random() < MUTATION_RATE:
        mutation_point = random.choice(list(strategy.keys()))
        board_tuple = [(mutation_point // (3 ** i)) % 3 - 1 for i in range(SIZE * SIZE)]
        board = [board_tuple[i*SIZE:(i+1)*SIZE] for i in range(SIZE)]
        valid_moves = get_possible_moves(board)
        if valid_moves:
            strategy[mutation_point] = random.choice(valid_moves)
    return strategy

def genetic_algorithm(pop_size, generations):
    population = [generate_random_strategy() for _ in range(pop_size)]
    for generation in range(generations):
        fitness_scores = [evaluate_fitness(strategy, population) for strategy in population]
        best_fitness = max(fitness_scores)
        average_fitness = sum(fitness_scores) / pop_size
        print(f"Generation {generation + 1}: Best Fitness = {best_fitness}, Average Fitness = {average_fitness:.2f}")
        parents = select_parents(population, fitness_scores)
        new_population = []
        while len(new_population) < pop_size:
            if random.random() < REPLICATION_RATE:
                new_population.append(random.choice(parents))
            else:
                parent1, parent2 = random.sample(parents, 2)
                child1, child2 = crossover(parent1, parent2)
                new_population.append(mutate(child1))
                new_population.append(mutate(child2))
        population = new_population[:pop_size]
        if best_fitness >= 1.0:
            print(f"Optimal strategy found in generation {generation + 1}")
            break
    best_strategy = max(population, key=lambda s: evaluate_fitness(s, population))
    return best_strategy

def print_board(board):
    def cell_to_char(cell):
        if cell == X:
            return "X"
        elif cell == O:
            return "O"
        else:
            return " "

    print("-------------")
    for i in range(SIZE):
        print(f"| {cell_to_char(board[i][0])} | {cell_to_char(board[i][1])} | {cell_to_char(board[i][2])} |")
        print("-------------")

def print_board_init():
    print("-------------")
    print("| 0 | 1 | 2 |")
    print("-------------")
    print("| 3 | 4 | 5 |")
    print("-------------")
    print("| 6 | 7 | 8 |")
    print("-------------")

def is_winner(board, player):
    win_conditions = [
        [(0, 0), (0, 1), (0, 2)], [(1, 0), (1, 1), (1, 2)], [(2, 0), (2, 1), (2, 2)],  # rows
        [(0, 0), (1, 0), (2, 0)], [(0, 1), (1, 1), (2, 1)], [(0, 2), (1, 2), (2, 2)],  # columns
        [(0, 0), (1, 1), (2, 2)], [(0, 2), (1, 1), (2, 0)]                            # diagonals
    ]
    return any(all(board[row][col] == player for row, col in condition) for condition in win_conditions)

def is_board_full(board):
    return all(cell != EMPTY for row in board for cell in row)

def play_user_move(board):
    while True:
        try:
            move = int(input("Enter your move (0-8): "))
            if 0 <= move <= 8:
                row, col = divmod(move, SIZE)
                if board[row][col] == EMPTY:
                    return row, col
            print("Invalid move. Try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def play_ai_move(board, strategy):
    print("AI's Move:")
    state = board_to_canonical_state(board)
    move = strategy.get(state)
    if move is None or board[move[0]][move[1]] != EMPTY:
        possible_moves = get_possible_moves(board)
        move = random.choice(possible_moves)
        print("Fallback to random move due to invalid strategy move.")
    print(f"Move: {move}")
    return move

def play_again(strategy):
    print("Game over.")
    play_again = input("Play again? (y/n): ")
    if play_again.lower() == "y":
        print("Welcome to Tic Tac Toe against AI!")
        print_board_init()
        play_game_user(strategy)

def play_game_user(strategy):
    board = initialize_board()
    turn = X  # X always starts

    while any(EMPTY in row for row in board):
        if turn == X:
            ai_move = play_ai_move(board, strategy)
            if ai_move is None:
                print("You win by default! The AI made an invalid move.")
                play_again(strategy)
                return
            board[ai_move[0]][ai_move[1]] = X
        else:
            user_move = play_user_move(board)
            board[user_move[0]][user_move[1]] = O

        print_board(board)

        if is_winner(board, turn):
            if turn == X:
                print("AI wins!")
                play_again(strategy)
            else:
                print("Congratulations! You won!")
                play_again(strategy)
            return

        if is_board_full(board):
            print("It's a draw!")
            play_again(strategy)
            return

        turn = O if turn == X else X

def save_strategy_to_json(strategy, filename):
    with open(filename, 'w') as f:
        json.dump(strategy, f)

def load_strategy_from_json(filename):
    try:
        with open(filename, 'r') as f:
            strategy = json.load(f)
        strategy = {int(k): tuple(v) for k, v in strategy.items()}
        return strategy
    except FileNotFoundError:
        return None

strategy = load_strategy_from_json(STRATEGY_FILE)
if strategy is None:
    strategy = genetic_algorithm(POPULATION_SIZE, MAX_GENERATIONS)
    save_strategy_to_json(strategy, STRATEGY_FILE)

print("Welcome to Tic Tac Toe against AI!")
print_board_init()
play_game_user(strategy)
