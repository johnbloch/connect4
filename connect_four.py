import random
import math
import copy

class ConnectFourGame:
    def __init__(self):
        self.board = [['_' for _ in range(7)] for _ in range(6)]
        self.current_player = 'X'  # Players are 'X' (computer) and 'O' (human)

    def print_board(self): 
        for row in self.board:
            print(' '.join(row))
        print()

    def is_valid_move(self, column): # a move is valid if and only if the top square is empty
        return self.board[0][column] == '_'

    def make_move(self, column): # places piece in specified column, returns true if valid, false else
        if not self.is_valid_move(column):
            return False
        for row in reversed(self.board):
            if row[column] == '_':
                row[column] = self.current_player
                return True
        return False

    def is_winner(self, player):
        # Horizontal, vertical, and diagonal checks
        for c in range(7 - 3):
            for r in range(6):
                if all(self.board[r][c + i] == player for i in range(4)):
                    return True

        for c in range(7):
            for r in range(6 - 3):
                if all(self.board[r + i][c] == player for i in range(4)):
                    return True

        for c in range(7 - 3):
            for r in range(6 - 3):
                if all(self.board[r + i][c + i] == player for i in range(4)):
                    return True

        for c in range(7 - 3):
            for r in range(3, 6):
                if all(self.board[r - i][c + i] == player for i in range(4)):
                    return True
        return False

    def is_draw(self):
        # Check if all columns in the top row are filled, indicating a draw
        return all(self.board[0][col] != '_' for col in range(7))

    def get_available_moves(self): # get possible moves (column #s) based on current state
        return [c for c in range(7) if self.is_valid_move(c)]

    def switch_player(self): 
        self.current_player = 'O' if self.current_player == 'X' else 'X'

    def play_game(self): # only used for terminal version of game
        self.choose_first_player()  # Method to choose who goes first
        while True:
            self.print_board()
            if self.current_player == 'X':  # AI's turn
                move = self.get_ai_move()
            else:  # Human's turn
                move = self.get_human_move()

            if self.make_move(move):
                if self.is_winner(self.current_player):
                    self.print_board()
                    print(f"Player {self.current_player} wins!")
                    break
                self.switch_player()
            else:
                print("Invalid move, try again.")

    def get_ai_move(self): # use MCTS to determine next move of engine
        mcts = MCTS()
        best_move = mcts.search(self)
        return best_move

    def get_human_move(self): # only for terminal version of game
        while True:
            try:
                move = int(input(f"Player {self.current_player}, enter your move (0-6): "))
                if move in self.get_available_moves():
                    return move
                else:
                    print("Invalid move, please try a valid column.")
            except ValueError:
                print("Invalid input, please enter a number.")

    def choose_first_player(self): # only for terminal version of game
        choice = input("Do you want to go first? (yes/no): ").strip().lower()
        self.current_player = 'O' if choice in ['yes', 'y'] else 'X'

class MCTSNode: # node in tree
    def __init__(self, game_state, parent=None, move=None):
        self.game_state = copy.deepcopy(game_state) # game state at this node
        self.parent = parent # parent of this node
        self.move = move # move that led to this state
        self.children = [] # children of this node (possible states from this state)
        self.wins = 0 # number of simulated wins from this node
        self.visits = 0 # number of total simulations from this node
        self.untried_moves = game_state.get_available_moves() # list of moves that have not been explored

    def select_child(self): # selects child of this node which maximizes UCB1 value
        return max(self.children, key=lambda c: c.wins / c.visits + math.sqrt(2 * math.log(self.visits) / c.visits))

    def add_child(self, move, game_state): # adds a child to this node given a move and a current game state
        child_node = MCTSNode(game_state=game_state, parent=self, move=move)
        self.untried_moves.remove(move)
        self.children.append(child_node)
        return child_node

    def update(self, result): # updates the number of wins based on a result of a simulation
        self.visits += 1
        self.wins += result

class MCTS: # stores the actual tree and the actual search method 
    def __init__(self, exploration_weight=1.4):
        self.exploration_weight = exploration_weight # sqrt(2)

    def simulate(self, node): #start from node and play random game until terminal state, returns end state of random game
        current_state = copy.deepcopy(node.game_state)
        while not current_state.is_winner('X') and not current_state.is_winner('O') and not current_state.is_draw():
            # make a random move
            available_moves = current_state.get_available_moves()
            move = random.choice(available_moves)
            current_state.make_move(move)
            current_state.switch_player()
        return current_state # return the terminal state of this simulation

    # four main stages of MCTS: selection, expansion, simulation, backpropogation
    # these four steps are repeated many times until tree converges to optimal game tree for engine
    def search(self, initial_state, max_iterations=2500): 
        root = MCTSNode(game_state=initial_state)
        for _ in range(max_iterations):
            node = root
            state = copy.deepcopy(initial_state)

            # SELECTION: select most promising nodes (based on UCB1 values) until we reach a node that has not been fully expanded or is a terminal state 
            while node.untried_moves == [] and node.children != []: 
                node = node.select_child()
                state.make_move(node.move)
                state.switch_player()

            # EXPANSION: if there are moves left to try, pick a random one and add it as a child
            if node.untried_moves != []:
                move = random.choice(node.untried_moves)
                state.make_move(move)
                state.switch_player()
                node = node.add_child(move, state)

            # SIMULATION: simulate the game from this randomly chosen node and store the terminal state
            simulation_result = self.simulate(node)

            # BACKPROPOGATION: given the result of the simulation, update all the parents on the result
            while node is not None:
                node.update(1 if simulation_result.is_winner('X') else 0)
                node = node.parent

        # the best move is the move that has the highest win ratio
        return max(root.children, key=lambda c: c.wins / c.visits).move
  