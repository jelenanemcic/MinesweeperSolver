from cassowary import SimplexSolver, Variable, STRONG
from random import sample, randint, choice

class Field:
    # a[row][col]
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
    def __init__(self, n, k=0):
        """
        Create board object with dimensions nxn and k mines inside
        set at random locations
        """
        self.solver = SimplexSolver()
        self.board_dim = n
        #self.num_mines = k
        self.marked = []
        self.vars = [[Field(j, i) for i in range(n)] for j in range(n)]

        #for (x, y) in zip(sample(range(n), k), sample(range(n), k)):
        #    self.vars[x][y].is_mine = True

        self.current_adjacent_fields = []

    #TODO: delete later, just for testing
    def set_mines(self, mines):
        self.num_mines = len(mines)
        for (row_index, col_index) in mines:
            self.vars[row_index][col_index].is_mine = True


    def _get_adjacent_fields(self, row_index, col_index):
        """
        Get a list of adjacent fields around field specified with row_index and col_index
        """
        adjacent_fields = []
        for i in range(max(0, row_index-1), min(self.board_dim, row_index+2)):
            for j in range(max(0, col_index-1), min(self.board_dim, col_index+2)):
                if i != row_index or j != col_index:
                    adjacent_fields.append(self.vars[i][j])
        return adjacent_fields

    def _get_adjacent_mines(self, row_index, col_index):
        return sum(f.is_mine for f in self._get_adjacent_fields(row_index, col_index))

    def update(self):
        """
        For each field that is not marked with is_mine compute number of adjacent mines
        """
        for (row_index, row) in enumerate(self.vars):
            for (col_index, field) in enumerate(row):
                field = self.vars[row_index][col_index]
                if not field.is_mine:
                    field.adjacent_mines = self._get_adjacent_mines(row_index, col_index)

    def open_field(self, field):
        """
        Open field and check.

        If there is a bomb this function will raise Explosion and callee should handle that.
        If opened field has no adjacent mines we will open new all of his covered adjacent
        fields.
        """
        field.covered = False
        print("otvaram {}: {}".format(field.variable, field.adjacent_mines))
        if field.is_mine:
            #TOOD: not a ValueError, raise Explosion or something
            raise ValueError("Boom")
        if field.adjacent_mines == 0:
            boundary_list = []
            for adjacent_field in self._get_adjacent_fields(field.row, field.column):
                if adjacent_field.covered:
                    boundary_list += self.open_field(adjacent_field)
            return boundary_list
        else:
            return [field]


    def make_constraint(self, row_index, col_index):
        """
        Compute equations for field (row_index, col_index)
        """

        adjacent_fields = self._get_adjacent_fields(row_index, col_index)
        adjacent_mines = self._get_adjacent_mines(row_index, col_index)

        for field in adjacent_fields:
            if field not in self.current_adjacent_fields:
                self.current_adjacent_fields.append(field)

        constraint = 0
        for field in adjacent_fields:
            if field.covered:
                constraint += field.variable
    #   print(constraint == adjacent_mines)
        return constraint == adjacent_mines

    def get_random_field(self):
        #TODO: we should somehow sample list of safe fields
        while True:
            i = randint(0, self.board_dim - 1)
            j = randint(0, self.board_dim - 1)

            if self.vars[i][j].variable.value == 0:
                break

        return self.vars[i][j]

    def solve(self):
        for (row_index, row) in enumerate(self.vars):
            for (col_index, var) in enumerate(row):
                self.solver.add_constraint(self.vars[row_index][col_index].variable >= 0)
                self.solver.add_constraint(self.vars[row_index][col_index].variable <= 1)
        # prefer corner here?
        newly_opened = self.get_random_field()
        self.open_field(newly_opened)
        visited = []

        # second condition?
        while self.num_mines != len(self.marked) or len(visited) < 3:
            print(newly_opened.variable)

            self.solver.add_constraint(self.make_constraint(newly_opened.row, newly_opened.column))
            if newly_opened not in visited:
                visited.append(newly_opened)

            possible_fields = []
            found_mine = False
            for field in self.current_adjacent_fields:
                if field.variable.value == 1:
                    print("oznacavam {}", field.variable)
                    field.marked_mine = True
                    found_mine = True
                    if field not in self.marked:
                        self.marked.append(field)
                if field.variable.value == 0 and field in self.marked:
                    self.marked.remove(field)
                elif field != newly_opened and field not in visited:
                    possible_fields.append(field)

            if possible_fields:
                newly_opened = choice(possible_fields)
            else:
                newly_opened = self.get_random_field()

            self.open_field(newly_opened)

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

def test2():
    b = Board(4)
    b.set_mines([(0, 1), (1, 2)])
    b.update()

    [print(f.variable, f.adjacent_mines) for f in b.open_field(b.vars[3][0])]


if __name__ == "__main__":
    test2()
