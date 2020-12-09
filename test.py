from cassowary import SimplexSolver, Variable, STRONG


class Field:
    def __init__(self, i, j):
        # variable is binary value which is true if here is mine
        self.variable = Variable('a[' + str(i) + '][' + str(j) + ']')
        self.row = i
        self.column = j
        self.adjacent_mines = 0
        self.covered = True


class Board:
    def __init__(self, n):
        self.solver = SimplexSolver()
        self.board_dim = n
        self.vars = [[Field(i, j) for i in range(0, n)] for j in range(0, n)]

    def _get_adjacent(self, row_index, col_index):
        adjacent_mines = 0
        adjacent_fields = []
        for i in range(max(0, row_index-1), min(self.board_dim, row_index+2)):
            for j in range(max(0, col_index-1), min(self.board_dim, col_index+2)):
                adjacent_fields.append(self.vars[i][j])
                adjacent_mines += self.vars[i][j].variable.value
        return adjacent_mines, adjacent_fields

    def update(self):
        for (row_index, row) in enumerate(self.vars):
            for (col_index, field) in enumerate(row):
                field = self.vars[row_index][col_index]
                if field.variable.value == 0:
                    field.adjacent_mines, _ = self._get_adjacent(row_index, col_index)

    def make_constraint(self, row_index, col_index):
        self.solver.add_constraint(self.vars[row_index][col_index].variable >= 0)
        self.solver.add_constraint(self.vars[row_index][col_index].variable <= 1)
        adjacent_mines, adjacent_fields = self._get_adjacent(row_index, col_index)
        constraint = 0
        for field in adjacent_fields:
            if field.covered:
                constraint += field.variable
     #   print(constraint)
        return constraint == adjacent_mines

    def solve(self):
        for (row_index, row) in enumerate(self.vars):
            for (col_index, var) in enumerate(row):
                if var.variable.value == 1:
                    self.solver.add_stay(var.variable, strength=STRONG)

        for (row_index, row) in enumerate(self.vars):
            for (col_index, var) in enumerate(row):
                if var.variable.value == 0:
                    self.solver.add_constraint(self.make_constraint(row_index, col_index))
        print([[var.variable.value for var in row] for row in self.vars])


def test1():
    b = Board(3)

    # Mine se nalaze na poljima označenim s X
    # 0 X 0
    # X 0 X
    # 0 X 0
    b.vars[0][1].variable.value = 1
    b.vars[1][0].variable.value = 1
    b.vars[1][2].variable.value = 1
    b.vars[2][1].variable.value = 1

    b.update()
    # print(b.vars)

    # Vrijednosti trebeaju biti
    # 2 X 2
    # X 4 X
    # 2 X 2
    assert b.vars[0][0].adjacent_mines == 2
    assert b.vars[0][2].adjacent_mines == 2
    assert b.vars[1][1].adjacent_mines == 4
    assert b.vars[2][0].adjacent_mines == 2
    assert b.vars[2][2].adjacent_mines == 2

    # sva polja su zatvorena osim:
   # b.vars[0][0].covered = False
   # b.vars[0][2].covered = False

    b.solve()


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


if __name__ == "__main__":
    test1()
