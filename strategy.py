from abc import ABC
from cassowary import SimplexSolver
from random import choice


class Strategy(ABC):

    def solve(self, first_field=None):
        pass


class CSP(Strategy):

    def __init__(self, board):
        self.board = board
        self.solver = SimplexSolver()

    def open(self, field):
        self.board.open_field(field)

        # this case is really interesting, we are opening a field that is safe but solver
        # thinks that is is mined. We need to edit and enforce as stay constraint
        if field.variable.value != 0:
            field.variable.value = 0
            self.solver.add_stay(field.variable)

        if field.adjacent_mines == 0:
            boundary_list = []
            for adjacent_field in self.board.get_adjacent_fields(field.row, field.column):
                if adjacent_field.covered:
                    boundary_list += self.open(adjacent_field)
            return boundary_list
        else:
            return [field]

    def make_constraint(self, row_index, col_index):
        """
        Compute equations for field (row_index, col_index)
        """

        adjacent_fields = self.board.get_adjacent_fields(row_index, col_index)
        adjacent_mines = self.board.get_adjacent_mines(row_index, col_index)

        assert adjacent_mines
        for field in adjacent_fields:
            if field not in self.board.current_adjacent_fields:
                self.board.current_adjacent_fields.append(field)

        # ?
        # adjacent_mines == sum(f.variable for f in adjacent_fields if f.closed)
        constraint = 0
        for field in adjacent_fields:
            if field.covered:
                constraint += field.variable
        #    print(constraint == adjacent_mines)
        return constraint == adjacent_mines

    def solve(self, first_field=None):
        for (row_index, row) in enumerate(self.board.vars):
            for (col_index, var) in enumerate(row):
                self.solver.add_constraint(self.board.vars[row_index][col_index].variable >= 0)
                self.solver.add_constraint(self.board.vars[row_index][col_index].variable <= 1)

        # prefer corner here?
        if first_field:
            newly_opened = self.open(first_field)
        else:
            newly_opened = self.open(self.board.get_random_field())
        visited = []

        while self.board.closed != self.board.num_mines:
            for new in newly_opened:
                self.solver.add_constraint(self.make_constraint(new.row, new.column))
                if new not in visited:
                    visited.append(new)

            possible_fields = []
            for field in self.board.current_adjacent_fields:
                if field.variable.value == 1:
                    print("oznacavam {}", field.variable)
                    field.marked_mine = True
                    if field not in self.board.marked:
                        print("Marking field {} as dangerous".format(field.variable))
                        self.board.marked.append(field)
                elif field not in visited and field.covered:
                    if field.is_mine:
                        print("Pushing mined field {} in possible fields".format(field.variable))
                    possible_fields.append(field)
                if field.variable.value == 0 and field in self.board.marked:
                    print("Remove mark on field {}".format(field.variable))
                    self.board.marked.remove(field)

            if possible_fields:
                new_field = choice(possible_fields)
            else:
                new_field = self.board.get_random_field()

            newly_opened = self.open(new_field)
            for field in newly_opened:
                if field not in visited:
                    visited.append(field)


class SAT(Strategy):

    def solve(self, first_field=None):
        pass
