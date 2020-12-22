from cassowary import SimplexSolver, Variable
from random import randint
from strategy import CSP
import tkinter as tk
from tkinter import ttk

class Field:
    # a[row][col]
    def __init__(self, i, j, board, is_mine=False):
        # variable is binary value which is true if here is mine
        self.variable = Variable('a[' + str(i) + '][' + str(j) + ']')
        self.row = i
        self.column = j
        # we need to have a reference to the board in order to notify the event
        self.board = board
        self.adjacent_mines = 0
        self.covered = True
        self.is_mine = is_mine
        self.marked_mine = False
        self.button = ttk.Button(self.grid, text=" ")
        self.button.grid(row=i, column=j)
        self.button.bind('<ButtonPress-1>', lambda e: self.board._left_click(e))
        self.button.bind('<ButtonPress-2>', lambda e: self.board._right_click(e))

class Board:
    def __init__(self, n, k):
        """
        Create board object with dimensions nxn and k mines inside
        set at random locations
        """
        self.board_dim = n
        self.num_mines = k
        self.marked = []
        self.vars = [[Field(j, i, self) for i in range(n)] for j in range(n)]
        self.closed = n*n
        self.current_adjacent_fields = []

        self.setup_gui()

        # for (x, y) in zip(sample(range(n), k), sample(range(n), k)):
        #    self.vars[x][y].is_mine = True

    def _right_click(self, event):
        grid_info = event.widget.grid_info()
        column, row = grid_info["column"], grid_info["row"]

        if self.vars[row][column].marked:
            self.remove_mark_from_field(self.vars[row][column])
        else:
            self.mark_field(self.vars[row][column])

    def _left_click(self, event):
        grid_info = event.widget.grid_info()
        column, row = grid_info["column"], grid_info["row"]

        if self.vars[row][column].covered:
            self.open_field(self.vars[row][column])

    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("Minesweeper solver")

        # create 2x3 grid for root frame
        [self.root.rowconfigure(r, weight=1) for r in range(2)]
        [self.root.columnconfigure(c, weight=1) for c in range(3)]

        keys = ("mines", "alive", "opened")
        self.labelvars = {k: tk.StringVar() for k in keys}

        self.labels["mines"] = ttk.Label(self.root, text="Mines: " + str(board.num_mines))
        self.labels["mines"].grid(row=0, column=0)

        self.labelvars["alive"].set("Alive")
        self.labels["alive"] = ttk.Label(self.root, textvariable=self.labelvars["alive"])
        self.labels["alive"].grid(row=0, column=1)

        self.labelvars["opened"].set("0")
        self.labels["opened"] = ttk.Label(self.root, text="Opened: 0")
        self.labels["opened"].grid(row=0, column=2)

        # create a frame for minesweeper button grid
        self.grid = ttk.Frame(self.root)
        self.grid.grid(row=1, column=0, rowspan=1, columnspan=self.board_dim)

        for x in range(self.board_dim);
            for y in range(self.board_dim):
                b = ttk.Button(self.grid, text=" ")
                b.grid(row=x, column=y)
                b.bind('<ButtonPress-1>', self._left_click)
                b.bind('<ButtonPress-2>', self._right_click)

    # TODO: delete later, just for testing
    def set_mines(self, mines):
        self.num_mines = len(mines)
        for (row_index, col_index) in mines:
            self.vars[row_index][col_index].is_mine = True

    def get_adjacent_fields(self, row_index, col_index):
        """
        Get a list of adjacent fields around field specified with row_index and col_index
        """
        adjacent_fields = []
        for i in range(max(0, row_index - 1), min(self.board_dim, row_index + 2)):
            for j in range(max(0, col_index - 1), min(self.board_dim, col_index + 2)):
                if i != row_index or j != col_index:
                    adjacent_fields.append(self.vars[i][j])
        return adjacent_fields

    def get_adjacent_mines(self, row_index, col_index):
        return sum(f.is_mine for f in self.get_adjacent_fields(row_index, col_index))

    def update(self):
        """
        For each field that is not marked with is_mine compute number of adjacent mines
        """
        for (row_index, row) in enumerate(self.vars):
            for (col_index, field) in enumerate(row):
                field = self.vars[row_index][col_index]
                if not field.is_mine:
                    field.adjacent_mines = self.get_adjacent_mines(row_index, col_index)

    def get_random_field(self):
        # TODO: we should somehow sample list of safe fields
        while True:
            i = randint(0, self.board_dim - 1)
            j = randint(0, self.board_dim - 1)
            if self.vars[i][j].variable.value == 0 and self.vars[i][j].covered:
                break

        return self.vars[i][j]

    def mark_field(self, field):
        if field not in self.marked:
            self.marked.append(field)

    def remove_mark_from_field(self, field):
        if field in self.marked:
            self.marked.remove(field)
            field.marked = False
            print("Remove mark on field {}".format(field.variable))

    def open_field(self, field):
        """
        Open field and check.

        Opened field is removed from current_adjacent_fields list.
        If there is a bomb this function will raise Explosion and callee should handle that.
        If opened field has no adjacent mines we will open new all of his covered adjacent
        fields.
        """
        assert field.covered
        self.closed -= 1
        field.covered = False

        if field in self.current_adjacent_fields:
            self.current_adjacent_fields.remove(field)
        print("otvaram {}: {}".format(field.variable, field.adjacent_mines))

        if field.is_mine:
            # TODO: not a ValueError, raise Explosion or something
            raise ValueError("Boom")

        # if any of these fields are marked as dangerous we should delete now because
        # they are obviously not dangerous
        self.remove_mark_from_field(field)

    def run_strategy(self, strategy, first_field=None):
        strategy.solve(first_field)


def test1():
    b = Board(3, 3)

    # Mine se nalaze na poljima označenim s X
    # 0 X 0
    # X 0 X
    # 0 X 0

    #   b.vars[0][1].is_mine = True
    b.vars[1][0].is_mine = True
    b.vars[1][2].is_mine = True
    b.vars[2][1].is_mine = True

    #  b.update()
    # print(b.vars)

    # Vrijednosti trebeaju biti
    # 2 X 2
    # X 4 X
    # 2 X 2
    #    assert b.vars[0][0].adjacent_mines == 2
    #    assert b.vars[0][2].adjacent_mines == 2
    #    assert b.vars[1][1].adjacent_mines == 4
    #    assert b.vars[2][0].adjacent_mines == 2
    #    assert b.vars[2][2].adjacent_mines == 2

    # sva polja su zatvorena osim:
    # b.vars[0][0].covered = False
    # b.vars[0][2].covered = False

   # b.solve()


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
    print([[var.variable.value for var in row] for row in b.vars])


def test3():
    # cool example that fails because CSP can infer the right thing
    b = Board(4, 3)
    b.set_mines([(0, 2), (0, 3), (3, 3)])
    b.update()

    for row in b.vars:
        print(" ".join([str(v.is_mine) for v in row]))

    for row in b.vars:
        print(" ".join([str(v.adjacent_mines) for v in row]))

    #b.run_strategy(CSP(b))
    print([[var.variable.value for var in row] for row in b.vars])


if __name__ == "__main__":
    test2()
