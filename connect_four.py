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

    def make_move(self, column): # 
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

    def get_available_moves(self):
        return [c for c in range(7) if self.is_valid_move(c)]

    def switch_player(self):
        self.current_player = 'O' if self.current_player == 'X' else 'X'

    def play_game(self):
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

    def get_ai_move(self):
        mcts = MCTS()
        best_move = mcts.search(self)
        return best_move

    def get_human_move(self):
        while True:
            try:
                move = int(input(f"Player {self.current_player}, enter your move (0-6): "))
                if move in self.get_available_moves():
                    return move
                else:
                    print("Invalid move, please try a valid column.")
            except ValueError:
                print("Invalid input, please enter a number.")

    def choose_first_player(self):
        choice = input("Do you want to go first? (yes/no): ").strip().lower()
        self.current_player = 'O' if choice in ['yes', 'y'] else 'X'

class MCTSNode:
    def __init__(self, game_state, parent=None, move=None):
        self.game_state = copy.deepcopy(game_state)
        self.parent = parent
        self.move = move
        self.children = []
        self.wins = 0
        self.visits = 0
        self.untried_moves = game_state.get_available_moves()

    def select_child(self):
        return max(self.children, key=lambda c: c.wins / c.visits + math.sqrt(2 * math.log(self.visits) / c.visits))

    def add_child(self, move, game_state):
        child_node = MCTSNode(game_state=game_state, parent=self, move=move)
        self.untried_moves.remove(move)
        self.children.append(child_node)
        return child_node

    def update(self, result):
        self.visits += 1
        self.wins += result

class MCTS:
    def __init__(self, exploration_weight=1.4):
        self.exploration_weight = exploration_weight

    def simulate(self, node):
        current_state = copy.deepcopy(node.game_state)
        while not current_state.is_winner('X') and not current_state.is_winner('O') and not current_state.is_draw():
            available_moves = current_state.get_available_moves()
            move = random.choice(available_moves)
            current_state.make_move(move)
            current_state.switch_player()
        return current_state

    def search(self, initial_state, max_iterations=2500):
        root = MCTSNode(game_state=initial_state)
        for _ in range(max_iterations):
            node = root
            state = copy.deepcopy(initial_state)

            while node.untried_moves == [] and node.children != []: 
                node = node.select_child()
                state.make_move(node.move)
                state.switch_player()

            if node.untried_moves != []:
                move = random.choice(node.untried_moves)
                state.make_move(move)
                state.switch_player()
                node = node.add_child(move, state)

            simulation_result = self.simulate(node)
            while node is not None:
                node.update(1 if simulation_result.is_winner('X') else 0)
                node = node.parent

        return max(root.children, key=lambda c: c.wins / c.visits).move
import tkinter as tk
from tkinter import messagebox, simpledialog

class ConnectFourGUI:
    def __init__(self, game):
        self.game = game
        self.root = tk.Tk()
        self.root.title("Connect Four")

        # Styling constants
        self.player_colors = {'X': 'red', 'O': 'yellow', '_': 'SystemButtonFace'}
        self.bg_color = 'blue'
        self.button_font = ('Arial', 20)
        self.circle_radius = 30
        self.circle_pad = 10

        # Create canvas for board
        canvas_width = 7 * (self.circle_radius * 2 + self.circle_pad)
        canvas_height = 6 * (self.circle_radius * 2 + self.circle_pad)
        self.canvas = tk.Canvas(self.root, bg=self.bg_color, height=canvas_height, width=canvas_width)
        self.canvas.grid(row=1, column=0, columnspan=7)

        # Draw empty circles for the board
        self.circles = []
        for r in range(6):
            row = []
            for c in range(7):
                x0 = c * (self.circle_radius * 2 + self.circle_pad) + self.circle_pad + self.circle_radius
                y0 = r * (self.circle_radius * 2 + self.circle_pad) + self.circle_pad + self.circle_radius
                x1 = x0 + self.circle_radius * 2
                y1 = y0 + self.circle_radius * 2
                circle = self.canvas.create_oval(x0 - self.circle_radius, y0 - self.circle_radius, x1 - self.circle_radius, y1 - self.circle_radius, fill=self.player_colors['_'], outline="")
                row.append(circle)
            self.circles.append(row)

        # Create column buttons
        self.buttons = []
        for col in range(7):
            button = tk.Button(self.root, text='↓', font=self.button_font, height=1, width=3,
                               bg='SystemButtonFace', command=lambda c=col: self.player_move(c))
            button.grid(row=0, column=col)
            self.buttons.append(button)

        # Game status label
        self.status_label = tk.Label(self.root, text="", font=self.button_font)
        self.status_label.grid(row=2, column=0, columnspan=7)

        self.start_game()

    def player_move(self, col):
        if self.game.current_player == 'O':  # Human player
            self.make_move(col)

    def ai_move(self):
        best_move = self.game.get_ai_move()
        self.make_move(best_move)

    def make_move(self, col):
        if self.game.is_valid_move(col):
            self.game.make_move(col)
            self.update_board()
            winner = self.game.is_winner(self.game.current_player)
            draw = self.game.is_draw()
            if winner or draw:
                message = f"Player {self.game.current_player} wins!" if winner else "It's a draw!"
                self.root.after(1000, lambda: self.end_game(message))
            else:
                self.game.switch_player()
                self.update_status()
                if self.game.current_player == 'X':  # AI's turn
                    self.root.after(500, self.ai_move)  # AI makes a move after a short delay

    def update_board(self):
        for r in range(6):
            for c in range(7):
                color = self.player_colors[self.game.board[r][c]]
                self.canvas.itemconfig(self.circles[r][c], fill=color)

    def update_status(self):
        self.status_label.config(text=f"Player {self.game.current_player}'s Turn")

    def end_game(self, message):
        messagebox.showinfo("Game Over", message)
        self.root.destroy()

    def start_game(self):
        first_player = simpledialog.askstring("First Player", "Who goes first? (X for AI / O for Human)")
        if first_player and first_player.upper() in ['X', 'O']:
            self.game.current_player = first_player.upper()
        else:
            self.game.current_player = 'O'  # Default to human if input is invalid
        self.update_status()
        if self.game.current_player == 'X':
            self.ai_move()
        self.root.mainloop()

# Assuming your game and MCTS classes are defined as before
game = ConnectFourGame()
gui = ConnectFourGUI(game)
