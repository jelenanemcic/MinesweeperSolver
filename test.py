from cassowary import SimplexSolver, Variable

class Field:
    def __init__(self, i, j):
        # variable is binary value which is true if here is mine
        self.variable = Variable('a[' + str(i) + '][' + str(j) + ']')
        self.adjacent_mines = 0
        self.covered = True

class Board:
    def __init__(self, n):
        self.solver = SimplexSolver()
        self.board_dim = n
        self.vars = [[Field(i, j) for i in range(0, n)] for j in range(0, n)]

    def _get_adjacent(row_index, col_index):
        adjacent_mines = 0
        for i in range(min(0, row_index-1), max(self.board_dim, row_index+1)):
            for j in range(min(0, col_index-1), max(self.board_dim, col_index+1)):
                adjacent_mines += self.vars[i][j].variable.value
        return adjacent_mines

    def update(self):
        for (row_index, row) in enumerate(self.vars):
            for (col_index, field) in enumerate(row):
                field = self.vars[row_index][col_index]
                if field.variable.value == 1:
                    field.adjacent_mines = board._get_adjacent(row_index, col_index)


def main():
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
    main()
