from cassowary import SimplexSolver, Variable
from strategy import CSP


class Field:
    # a[row][col]
    def __init__(self, i, j, is_mine=False):
        self.row = i
        self.column = j
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
        self.board = [[Field(j, i) for i in range(n)] for j in range(n)]
        self.closed = n*n

        # for (x, y) in zip(sample(range(n), k), sample(range(n), k)):
        #    self.vars[x][y].is_mine = True

    # TODO: delete later, just for testing
    def set_mines(self, mines):
        self.num_mines = len(mines)
        for (row_index, col_index) in mines:
            self.board[row_index][col_index].is_mine = True

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

    def mark_field_dangerours(self, field):
        if field not in self.marked:
            field.marked_mine = True
            self.marked.append(field)
            print("Mark field {}".format(field))

    def mark_field_safe(self, field):
        if field in self.marked:
            field.marked_mine = False
            self.marked.remove(field)
            print("Remove mark on field {}".format(field))

    def open_field(self, field):
        """
        Open field and check.

        If there is a bomb this function will raise Explosion and callee should handle that.
        If opened field has no adjacent mines we will open new all of his covered adjacent
        fields.

        Returns list of newly opened fields
        """
        assert field.covered
        self.closed -= 1
        field.covered = False

        print("Opening {}".format(field))

        if field.is_mine:
            # TODO: not a ValueError, raise Explosion or something
            raise ValueError("Boom")

        # if any of these fields are marked as dangerous we should delete now because
        # they are obviously not dangerous and mark as safe
        self.mark_field_safe(field)

        if field.adjacent_mines == 0:
            opened_fields = []
            for adjacent_field in self.get_adjacent_fields(field.row, field.column):
                if adjacent_field.covered:
                    opened_fields += self.open_field(adjacent_field)
            return opened_fields
        else:
            return [field]

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
