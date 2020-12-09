from cassowary import SimplexSolver, Variable, STRONG
import random

class Field:
    def __init__(self, i, j, is_mine=False):
        # variable is binary value which is true if here is mine
        self.variable = Variable('a[' + str(i) + '][' + str(j) + ']')
        self.row = i
        self.column = j
        self.adjacent_mines = 0
        self.covered = True
        self.is_mine = is_mine
        self.marked_mine = False


class Board:
    def __init__(self, n, k):
        self.solver = SimplexSolver()
        self.board_dim = n
        self.num_mines = k
        self.marked = []
        self.vars = [[Field(i, j) for i in range(0, n)] for j in range(0, n)]
        self.current_adjacent_fields = []


    def _get_adjacent(self, row_index, col_index):
        adjacent_mines = 0
        adjacent_fields = []
        for i in range(max(0, row_index-1), min(self.board_dim, row_index+2)):
            for j in range(max(0, col_index-1), min(self.board_dim, col_index+2)):
                if i != row_index or j != col_index:
                    adjacent_fields.append(self.vars[i][j])
                    adjacent_mines += 1 if self.vars[i][j].is_mine else 0
        return adjacent_mines, adjacent_fields

    def update(self):
        for (row_index, row) in enumerate(self.vars):
            for (col_index, field) in enumerate(row):
                field = self.vars[row_index][col_index]
                if field.variable.value == 0:
                    field.adjacent_mines, _ = self._get_adjacent(row_index, col_index)

    def make_constraint(self, row_index, col_index):

        adjacent_mines, adjacent_fields = self._get_adjacent(row_index, col_index)
        for field in adjacent_fields:
            if field not in self.current_adjacent_fields:
                self.current_adjacent_fields.append(field)

        constraint = 0
        for field in adjacent_fields:
            if field.covered:
                constraint += field.variable
     #   print(constraint == adjacent_mines)
        return constraint == adjacent_mines

    def open_random(self):
        i = random.randint(0, self.board_dim - 1)
        j = random.randint(0, self.board_dim - 1)
        print("otvaram " + str(i) + " " + str(j))
        self.vars[i][j].covered = False
        if self.vars[i][j].is_mine:
            print("You have opened a mine.")
            exit(0)
        return self.vars[i][j]

    def solve(self):
        for (row_index, row) in enumerate(self.vars):
            for (col_index, var) in enumerate(row):
                self.solver.add_constraint(self.vars[row_index][col_index].variable >= 0)
                self.solver.add_constraint(self.vars[row_index][col_index].variable <= 1)
        newly_opened = self.open_random()
        visited = []

        while self.num_mines != len(self.marked) or len(visited) < 3:

            print(newly_opened.variable)

            self.solver.add_constraint(self.make_constraint(newly_opened.row, newly_opened.column))
            if newly_opened not in visited:
                visited.append(newly_opened)

            possible_fields = []
            found_mine = False
            for field in self.current_adjacent_fields:
                if field.variable.value == 1:
        #            print("oznacavam")
                    field.marked_mine = True
                    found_mine = True
                    if field not in self.marked:
                        self.marked.append(field)
                if field.variable.value == 0 and field in self.marked:
                    self.marked.remove(field)
                elif field != newly_opened and field not in visited:
                    possible_fields.append(field)

            if len(possible_fields) != 0:
                newly_opened = random.choice(possible_fields)

        #    if not found_mine or len(visited) < 2:
        #        newly_opened = self.open_random()

            newly_opened.covered = False
            if newly_opened.is_mine:
                print("You have opened a mine.")
                exit(0)

            print([[var.variable.value for var in row] for row in self.vars])


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
