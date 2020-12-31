import tkinter as tk
from tkinter import ttk
from random import randrange
import math
from strategy import CSP, SAT


class Field:
    # a[row][col]
    def __init__(self, i, j, board_dim, is_mine=False):
        self.row = i
        self.column = j
        self.id = int(board_dim * i + j + 1)
        self.adjacent_mines = 0
        self.covered = True
        self.is_mine = is_mine
        self.marked_mine = False

    def __repr__(self):
        return "[{}][{}]: {}".format(self.row, self.column, self.adjacent_mines)


class Minesweeper:
    def __init__(self, n, k):
        """
        Create board object with dimensions nxn and k mines inside
        set at random locations
        """
        self.labels = {}
        self.board_dim = n
        self.num_mines = k
        self.marked = []
        self.board = [[Field(j, i, self.board_dim) for i in range(n)] for j in range(n)]
        self.buttons = []
        self.opened = 0
        self.strategy = None

        self.setup_gui()

    def get_field_by_id(self, id):
        return self.board[math.floor((id - 1) / self.board_dim)][(id - 1) % self.board_dim]

    def _right_click(self, event):
        grid_info = event.widget.grid_info()
        column, row = grid_info["column"], grid_info["row"]

        if self.board[row][column].marked_mine:
            self.mark_field_safe(self.board[row][column])
        else:
            self.mark_field_dangerous(self.board[row][column])

    def _left_click(self, event):
        grid_info = event.widget.grid_info()
        column, row = grid_info["column"], grid_info["row"]

        if self.board[row][column].covered:
            self.open_field(self.board[row][column])

    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("Minesweeper solver")

        self.images = {
            "covered": tk.PhotoImage(file="images/covered.png").subsample(6, 6),
            "marked": tk.PhotoImage(file="images/flagged.png").subsample(6, 6),
            "numbers": [tk.PhotoImage(file="images/{}.png".format(i)).subsample(6, 6) for i in range(8+1)],
            "bomb": tk.PhotoImage(file="images/bomb.png").subsample(2, 2)
        }

        # create 2x3 grid for root frame
        [self.root.rowconfigure(r, weight=1) for r in range(3)]
        [self.root.columnconfigure(c, weight=1) for c in range(3)]

        self.labels["mines"] = ttk.Label(self.root, text="Mines: {}".format(self.num_mines))
        self.labels["mines"].grid(row=0, column=0)

        self.labels["alive"] = ttk.Label(self.root, text="Alive")
        self.labels["alive"].grid(row=0, column=1)

        self.labels["opened"] = ttk.Label(self.root, text="Opened: 0")
        self.labels["opened"].grid(row=0, column=2)

        self.strategy_grid = ttk.Frame(self.root, name="strategy_grid")
        self.strategy_grid.grid(row=1, column=0, rowspan=1, columnspan=3)

        CSP_button = ttk.Button(self.strategy_grid, name="csp_button", text="CSP Strategy")
        CSP_button.grid(row=0, column=0)
        CSP_button.bind('<ButtonPress-1>', self._run_CSP)
        SAT_button = ttk.Button(self.strategy_grid, name="sat_button", text="SAT Strategy")
        SAT_button.grid(row=0, column=1)
        SAT_button.bind('<ButtonPress-1>', self._run_SAT)
        next_step = ttk.Button(self.strategy_grid, name="next_step", text="Next step")
        next_step.grid(row=0, column=2)
        next_step.bind('<ButtonPress-1>', self._next_step)
        next_step.config(state=tk.DISABLED)

        # create a frame for minesweeper button grid
        self.grid = ttk.Frame(self.root)
        self.grid.grid(row=2, column=0, rowspan=1, columnspan=self.board_dim)

        for x in range(self.board_dim):
            row_buttons = []
            for y in range(self.board_dim):
                b = ttk.Button(self.grid, width=2, image=self.images["covered"])
                b.grid(row=x, column=y)
                b.bind('<ButtonPress-1>', self._left_click)
                b.bind('<ButtonPress-3>', self._right_click)
                b.config(state=tk.DISABLED)
                row_buttons.append(b)
            self.buttons.append(row_buttons)

    def set_mines(self, first_field):
        """
        Generate self.num_mines random tuples that represent mine positions
        """
        mines = 0
        while mines < self.num_mines:
            x, y = (randrange(0, self.board_dim), randrange(0, self.board_dim))

            if first_field != (x, y):
                mines += 1
                self.board[x][y].is_mine = True
        self._update()

    def num_closed(self):
        return self.board_dim ** 2 - self.opened

    def get_adjacent_fields(self, row_index, col_index):
        """
        Get a list of adjacent fields around field specified with row_index and col_index
        """
        adjacent_fields = []
        for i in range(max(0, row_index - 1), min(self.board_dim, row_index + 2)):
            for j in range(max(0, col_index - 1), min(self.board_dim, col_index + 2)):
                if i != row_index or j != col_index:
                    adjacent_fields.append(self.board[i][j])
        return adjacent_fields

    def get_adjacent_mines(self, row_index, col_index):
        return sum(f.is_mine for f in self.get_adjacent_fields(row_index, col_index))

    def _update(self):
        """
        For each field that is not marked with is_mine compute number of adjacent mines
        """
        for (row_index, row) in enumerate(self.board):
            for (col_index, field) in enumerate(row):
                field = self.board[row_index][col_index]
                if not field.is_mine:
                    field.adjacent_mines = self.get_adjacent_mines(row_index, col_index)

    def mark_field_dangerous(self, field):
        if field not in self.marked:
            field.marked_mine = True
            self.marked.append(field)
            print("Mark field {}".format(field))
            self.buttons[field.row][field.column].config(image=self.images["marked"])

    def mark_field_safe(self, field):
        if field in self.marked:
            field.marked_mine = False
            self.marked.remove(field)
            print("Remove mark on field {}".format(field))
            self.buttons[field.row][field.column].config(image=self.images["covered"])

    def open_field(self, field):
        """
        Open field and check.

        If there is a bomb this function will raise Explosion and callee should handle that.
        If opened field has no adjacent mines we will open new all of his covered adjacent
        fields.

        Returns list of newly opened fields
        """
        assert field.covered
        self.opened += 1
        field.covered = False

        print("Opening {}".format(field))

        if field.is_mine:
            self.buttons[field.row][field.column].config(image=self.images["bomb"])
            self.labels["alive"].config(text="Dead")

            print("Game over.")
            popup = tk.Toplevel(self.root)
            popup.wm_title("Lose")

            l = tk.Label(popup, text="Game over")
            l.grid(row=0, column=0, columnspan=2)

            b1 = ttk.Button(popup, text="Exit", command=quit)
            b1.grid(row=1, column=0)
            b2 = ttk.Button(popup, text="Restart", command=lambda: self.restart())
            b2.grid(row=1, column=1)

        else:
            # if any of these fields are marked as dangerous we should delete now because
            # they are obviously not dangerous and mark as safe
            self.mark_field_safe(field)

            self.labels["opened"].config(text="Opened: {}".format(self.opened))
            self.buttons[field.row][field.column].config(image=self.images["numbers"][field.adjacent_mines])

            # check if all fields are opened
            if self.num_closed() == self.num_mines:

                # mark all covered as bombs
                for row in self.board:
                    for field in row:
                        if field.covered:
                            self.mark_field_dangerous(field)

                print("Game solved.")
                popup = tk.Toplevel(self.root)
                popup.wm_title("Win")

                l = tk.Label(popup, text="Game solved")
                l.grid(row=0, column=0, columnspan=2)

                b1 = ttk.Button(popup, text="Exit", command=quit)
                b1.grid(row=1, column=0)
                b2 = ttk.Button(popup, text="Restart", command=lambda: self.restart())
                b2.grid(row=1, column=1)

            elif field.adjacent_mines == 0:
                opened_fields = [field]
                for adjacent_field in self.get_adjacent_fields(field.row, field.column):
                    if adjacent_field.covered:
                        opened_fields += self.open_field(adjacent_field)
                return opened_fields
            else:
                return [field]

        return [field]

    def run_strategy(self, strategy, first_field=None):
        strategy.solve(first_field)

    def _run_CSP(self, event):
        # disable SAT button if CSP is clicked
        SAT_button = event.widget.winfo_toplevel().nametowidget("strategy_grid.sat_button")
        SAT_button.config(state=tk.DISABLED)
        self.enable_buttons(event)

        self.strategy = CSP(self)
        first_field = (randrange(0, self.board_dim), randrange(0, self.board_dim))
        self.set_mines(first_field)

        self.strategy.first_step(first_field=first_field)

    def _run_SAT(self, event):
        # disable CSP button if SAT is clicked
        CSP_button = event.widget.winfo_toplevel().nametowidget("strategy_grid.csp_button")
        CSP_button.config(state=tk.DISABLED)
        self.enable_buttons(event)

        self.strategy = SAT(self)
        first_field = (randrange(0, self.board_dim), randrange(0, self.board_dim))
        self.set_mines(first_field)

        self.strategy.first_step(first_field=first_field)

    def _next_step(self, event):
        self.strategy.step()

    def enable_buttons(self, event):
        """
        Enables Next step button and all field buttons in the board.
        """
        next_step = event.widget.winfo_toplevel().nametowidget("strategy_grid.next_step")
        next_step.config(state=tk.NORMAL)

        for row in self.buttons:
            for button in row:
                button.config(state=tk.NORMAL)

    def restart(self):
        self.root.destroy()
        self.labels = {}
        self.marked = []
        self.board = [[Field(j, i, self.board_dim) for i in range(self.board_dim)] for j in range(self.board_dim)]
        self.buttons = []
        self.opened = 0
        self.strategy = None

        self.setup_gui()

