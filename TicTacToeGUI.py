import tkinter as tk
import json

class TicTacToe:
    def __init__(self, root):
        self.root = root
        self.root.title('Tic Tac Toe')
        self.current_player = 'X'
        self.board = [''] * 9
        self.buttons = []
        self.winning_line = None
        self.create_board()
        self.root.geometry("400x500")
        self.root.resizable(False, False)
        self.strategy = self.load_strategy("/mnt/data/tic_tac_toe_strategy.json")

        # AI goes first
        self.ai_move(first_move=True)

    def create_board(self):
        # Creating the board
        self.canvas = tk.Canvas(self.root, bg='white', width=400, height=400)
        self.canvas.pack()

        # Draw the grid lines
        for i in range(1, 3):
            self.canvas.create_line(0, i * 133, 400, i * 133, fill="black", width=2)
            self.canvas.create_line(i * 133, 0, i * 133, 400, fill="black", width=2)

        for i in range(3):
            row = []
            for j in range(3):
                btn = tk.Button(self.root, text='', font=('Arial', 40, 'bold'), width=2, height=1,
                                bg='white', fg='#333', command=lambda x=i*3 + j: self.on_button_click(x))
                btn_window = self.canvas.create_window(j * 133 + 67, i * 133 + 67, anchor='center', window=btn)
                row.append((btn, btn_window))
            self.buttons.append(row)

        # Adding label line and button
        self.result_label = tk.Label(self.root, text='', font=('Arial', 20, 'bold'), bg='white', width=30)
        self.result_label.pack(pady=10)

        self.reset_button = tk.Button(self.root, text="Reset", font=('Arial', 14), command=self.reset_board, width=30)
        self.reset_button.pack(pady=10)
        self.reset_button.place(x=20, y=460)

    def load_strategy(self, filename):
        # Loading the strategy from Json
        try:
            with open(filename, 'r') as f:
                strategy = json.load(f)
            strategy = {int(k): v for k, v in strategy.items()}
        except FileNotFoundError:
            strategy = {}
        return strategy

    def board_to_state(self, board):
        # Converting the state to an integer representation for the board
        # Empty = 0
        # X = 1
        # O = 2
        state = 0
        for i, cell in enumerate(board):
            if cell == '':
                state += 0 * (3 ** i)
            elif cell == 'X':
                state += 1 * (3 ** i)
            elif cell == 'O':
                state += 2 * (3 ** i)
        return state

    def ai_move(self, first_move=False):
        # Handling the AI's move
        if first_move:
            self.board[2] = 'X'  # Top-right corner as the first move
            self.update_ui_board()
            self.current_player = 'O'
            return

        if '' not in self.board:
            if not self.check_winner():
                self.result_label.config(text="It's a draw!", fg='gray')
            return

        state = self.board_to_state(self.board)

        if state in self.strategy:
            move = self.strategy[state]
            for index in move:
                if self.board[index] == '':
                    self.board[index] = 'X'
                    self.update_ui_board()
                    if self.check_winner():
                        self.result_label.config(text="Player X (AI) wins!", fg='deep pink')
                        self.animate_winning_line(self.winning_combination)
                        return
                    elif '' not in self.board:
                        self.result_label.config(text="It's a draw!", fg='gray')
                        return
                    else:
                        self.current_player = 'O'
                        return
        else:
            self.fallback_ai_move()

    def fallback_ai_move(self):
        # If the strategy cannot be found in the JSON
        possible_moves = [i for i, cell in enumerate(self.board) if cell == '']

        # Check for a winning move or a block
        for move in possible_moves:
            self.board[move] = 'X'
            if self.check_winner():
                self.update_ui_board()
                self.result_label.config(text="Player X (AI) wins!", fg='deep pink')
                self.animate_winning_line(self.winning_combination)
                return
            self.board[move] = ''

        for move in possible_moves:
            self.board[move] = 'O'
            if self.check_winner():
                self.board[move] = 'X'
                self.update_ui_board()
                self.current_player = 'O'
                return
            self.board[move] = ''

        move = possible_moves[0]
        self.board[move] = 'X'
        self.update_ui_board()
        if self.check_winner():
            self.result_label.config(text="Player X (AI) wins!", fg='deep pink')
            self.animate_winning_line(self.winning_combination)
        elif '' not in self.board:
            self.result_label.config(text="It's a draw!", fg='gray')
        else:
            self.current_player = 'O'

    def update_ui_board(self):
        for i, (btn, _) in enumerate(sum(self.buttons, [])):
            if self.board[i] == 'X':
                btn.config(text='X', state='disabled', disabledforeground='deep pink')
            elif self.board[i] == 'O':
                btn.config(text='O', state='disabled', disabledforeground='medium turquoise')
            else:
                btn.config(text='', state='normal')

    def on_button_click(self, index):
        # Handling the player's clicking
        if self.board[index] == '' and not self.check_winner():
            self.board[index] = self.current_player
            self.update_ui_board()
            if self.check_winner():
                self.result_label.config(text=f"Player {self.current_player} wins!", fg='medium turquoise')
                self.animate_winning_line(self.winning_combination)
            elif '' not in self.board:
                self.result_label.config(text="It's a draw!", fg='gray')
            else:
                self.current_player = 'X'
                self.ai_move()

    def check_winner(self):
        win_conditions = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # columns
            [0, 4, 8], [2, 4, 6]             # diagonals
        ]
        for condition in win_conditions:
            if self.board[condition[0]] == self.board[condition[1]] == self.board[condition[2]] != '':
                self.winning_combination = condition
                return True
        if '' not in self.board:
            self.result_label.config(text="It's a draw!", fg='gray')
        return False

    def animate_winning_line(self, combination):
        # Handling the animation when a winner was found
        x1, y1 = combination[0] % 3 * 133 + 67, combination[0] // 3 * 133 + 67
        x2, y2 = combination[2] % 3 * 133 + 67, combination[2] // 3 * 133 + 67
        self.draw_line(x1, y1, x2, y2)

    def draw_line(self, x1, y1, x2, y2):
        if self.winning_line:
            self.canvas.delete(self.winning_line)
        self.winning_line = self.canvas.create_line(x1, y1, x1, y1, fill="red", width=5)
        self.canvas.tag_raise(self.winning_line)
        self.animate_line(x1, y1, x2, y2)

    def animate_line(self, x1, y1, x2, y2):
        steps = 10
        delta_x = (x2 - x1) / steps
        delta_y = (y2 - y1) / steps
        for i in range(steps):
            self.canvas.after(i * 50, self.canvas.coords, self.winning_line, x1, y1, x1 + delta_x * i, y1 + delta_y * i)
        self.canvas.after(steps * 50, self.canvas.coords, self.winning_line, x1, y1, x2, y2)
        self.canvas.tag_raise(self.winning_line)  # Ensure the line is on top after animation

    def reset_board(self):
        # Reset button to start new game
        self.board = [''] * 9
        self.update_ui_board()
        self.result_label.config(text='')
        if self.winning_line:
            self.canvas.delete(self.winning_line)
            self.winning_line = None
        self.current_player = 'X'
        self.ai_move(first_move=True)

if __name__ == "__main__":
    root = tk.Tk()
    game = TicTacToe(root)
    root.mainloop()


