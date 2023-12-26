import tkinter as tk
from tkinter import messagebox, simpledialog
from connect_four import ConnectFourGame

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

