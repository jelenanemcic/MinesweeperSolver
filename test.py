from cassowary import SimplexSolver, Variable
from strategy import CSP
import tkinter as tk
from tkinter import ttk

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
        self.board_dim = n
        self.num_mines = k
        self.marked = []
        self.board = [[Field(j, i, self.board_dim) for i in range(n)] for j in range(n)]
        self.buttons = []
        self.opened = 0

        self.setup_gui()

        # for (x, y) in zip(sample(range(n), k), sample(range(n), k)):
        #    self.vars[x][y].is_mine = True

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

        # create 2x3 grid for root frame
        [self.root.rowconfigure(r, weight=1) for r in range(2)]
        [self.root.columnconfigure(c, weight=1) for c in range(3)]

        self.labels = {}

        self.labels["mines"] = ttk.Label(self.root, text="Mines: {}".format(self.num_mines))
        self.labels["mines"].grid(row=0, column=0)

        self.labels["alive"] = ttk.Label(self.root, text="Alive")
        self.labels["alive"].grid(row=0, column=1)

        self.labels["opened"] = ttk.Label(self.root, text="Opened: 0")
        self.labels["opened"].grid(row=0, column=2)

        # create a frame for minesweeper button grid
        self.grid = ttk.Frame(self.root)
        self.grid.grid(row=1, column=0, rowspan=1, columnspan=self.board_dim)

        for x in range(self.board_dim):
            row_buttons = []
            for y in range(self.board_dim):
                b = ttk.Button(self.grid, text=" ")
                b.grid(row=x, column=y)
                b.bind('<ButtonPress-1>', self._left_click)
                b.bind('<ButtonPress-3>', self._right_click)
                row_buttons.append(b)
            self.buttons.append(row_buttons)

    # TODO: delete later, just for testing
    def set_mines(self, mines):
        self.num_mines = len(mines)
        for (row_index, col_index) in mines:
            self.board[row_index][col_index].is_mine = True

    def num_closed(self):
        return self.board_dim**2 - self.opened

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

    def update(self):
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
            self.buttons[field.row][field.column].config(text="M")

    def mark_field_safe(self, field):
        if field in self.marked:
            field.marked_mine = False
            self.marked.remove(field)
            print("Remove mark on field {}".format(field))
            self.buttons[field.row][field.column].config(text=" ")


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
            # TODO: not a ValueError, raise Explosion or something
            raise ValueError("Boom")


        self.labels["opened"].config(text="Opened: {}".format(self.opened))
        self.buttons[field.row][field.column].config(text=str(field.adjacent_mines),
                                                     state=tk.DISABLED)

        # if any of these fields are marked as dangerous we should delete now because
        # they are obviously not dangerous and mark as safe
        self.mark_field_safe(field)

        if field.adjacent_mines == 0:
            opened_fields = [field]
            for adjacent_field in self.get_adjacent_fields(field.row, field.column):
                if adjacent_field.covered:
                    opened_fields += self.open_field(adjacent_field)
            return opened_fields
        else:
            return [field]

    def run_strategy(self, strategy, first_field=None):
        strategy.solve(first_field)


""" 
def main1():
    # minesweeper problem:
    # ? ? ?
    # 1 2 1
    x = [Variable('x' + str(i)) for i in range(3)]
    y = [Variable('y' + str(i), 1) for i in range(3)]

    c1 = x[0] + x[1] == 1
    c2 = x[0] + x[1] + x[2] == 2
    c3 = x[1] + x[2] == 1

    solver = SimplexSolver()

    solver.add_constraint(c1)
    solver.add_constraint(c2)
    solver.add_constraint(c3)

    assert x[0].value == 1 and x[1].value == 0 and x[2].value == 1


def test2():
    b = Board(4, 3)
    b.set_mines([(0, 1), (1, 2), (2, 2)])
    b.update()

    for row in b.vars:
        print(" ".join([str(v.is_mine) for v in row]))

    for row in b.vars:
        print(" ".join([str(v.adjacent_mines) for v in row]))

    b.run_strategy(CSP(b))
 #   b.solve(first_field=b.vars[3][0])
    #print([[var.variable.value for var in row] for row in b.vars])


def test3():
    # cool example that fails because CSP can infer the right thing
    b = Board(4, 3)
    b.set_mines([(0, 2), (0, 3), (3, 3)])
    b.update()

    for row in b.vars:
        print(" ".join([str(v.is_mine) for v in row]))

    for row in b.vars:
        print(" ".join([str(v.adjacent_mines) for v in row]))

  #  b.solve(first_field=b.vars[0][0])
    b.run_strategy(CSP(b))
    print([[var.variable.value for var in row] for row in b.vars])


if __name__ == "__main__":
    test2()
"""
