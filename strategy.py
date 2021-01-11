from abc import ABC
from cassowary import SimplexSolver, Variable
from random import choice, randint
from pysat.solvers import Solver as SATSolver
from pysat.card import CardEnc, EncType


class Strategy(ABC):

    def get_random_field(self):
        pass

    def open(self, field):
        pass

    def make_constraint(self, row_index, col_index):
        pass

    def first_step(self, first_field=None):
        pass

    def step(self):
        pass


class CSP(Strategy):

    def __init__(self, game):
        self.game = game
        self.solver = SimplexSolver()
        self.current_adjacent_fields = []
        self.newly_opened = []
        self.vars = [[Variable("a[{}][{}]".format(j, i)) for i in range(self.game.board_dim)]
                     for j in range(self.game.board_dim)]

    def get_random_field(self):
        while True:
            i = randint(0, self.game.board_dim - 1)
            j = randint(0, self.game.board_dim - 1)
            if self.vars[i][j].value == 0 and self.game.board[i][j].covered:
                break

        return self.game.board[i][j]

    def open(self, field):
        boundary_list = []
        for field in self.game.open_field(field):

            # this case is really interesting, we are opening a field that is safe but solver
            # thinks that it is mined. We need to edit and enforce as stay constraint
            if self.vars[field.row][field.column] != 0:
                self.vars[field.row][field.column].value = 0
            self.solver.add_stay(self.vars[field.row][field.column])

            # if adjacent_mines is set we are looking at boundary field and we need to add it
            # to the boundary_list
            if field.adjacent_mines:
                boundary_list.append(field)

            if field in self.current_adjacent_fields:
                self.current_adjacent_fields.remove(field)
        return boundary_list

    def make_constraint(self, row_index, col_index):
        """
        Compute equations for field (row_index, col_index)
        """

        adjacent_fields = self.game.get_adjacent_fields(row_index, col_index)
        adjacent_mines = self.game.get_adjacent_mines(row_index, col_index)

        assert adjacent_mines
        for field in adjacent_fields:
            if field not in self.current_adjacent_fields and self.game.board[field.row][field.column].covered:
                self.current_adjacent_fields.append(field)

        return adjacent_mines == sum(self.vars[f.row][f.column]
                                     for f in adjacent_fields if f.covered)

    def first_step(self, first_field=None):
        self.solver.add_constraint(self.game.num_mines == sum(self.vars[i][j]
                                                              for i in range(0, self.game.board_dim) for j in
                                                              range(0, self.game.board_dim)))

        for (row_index, row) in enumerate(self.game.board):
            for (col_index, var) in enumerate(row):
                self.solver.add_constraint(self.vars[row_index][col_index] >= 0)
                self.solver.add_constraint(self.vars[row_index][col_index] <= 1)

        if first_field:
            row, column = first_field
            self.newly_opened = self.open(self.game.board[row][column])
        else:
            self.newly_opened = self.open(self.get_random_field())

    def step(self):
        for new in self.newly_opened:
            self.solver.add_constraint(self.make_constraint(new.row, new.column))

        possible_fields = []
        for field in self.current_adjacent_fields:
            if self.vars[field.row][field.column].value == 1:
                self.game.mark_field_dangerous(field)
            else:
                if field.is_mine:
                    print("[CST-PSST] Pushing mined field {} in possible fields".format(field))
                else:
                    print("[CST]Pushing field {} in possible fields".format(field))
                possible_fields.append(field)

                if field in self.game.marked:
                    self.game.mark_field_safe(field)

        if possible_fields:
            print("[CST] Randomly choosing from possible fields: {}".format(possible_fields))
            new_field = choice(possible_fields)
        else:
            print("[CST] I have no idea what to choose next, randomly generating...")
            new_field = self.get_random_field()

        self.newly_opened = self.open(new_field)


class SAT(Strategy):

    def __init__(self, game):
        self.game = game
        self.solver = SATSolver(name='minicard')
        self.current_adjacent_fields = []
        self.newly_opened = []
        self.mines = []
        self.vars = [[0 for _ in range(self.game.board_dim)]
                     for _ in range(self.game.board_dim)]

    def get_random_field(self):
        while True:
            i = randint(0, self.game.board_dim - 1)
            j = randint(0, self.game.board_dim - 1)
            if self.vars[i][j] == 0 and self.game.board[i][j].covered:
                break

        return self.game.board[i][j]

    def open(self, field):
        boundary_list = []
        for field in self.game.open_field(field):

            # if adjacent_mines is set we are looking at boundary field and we need to add it
            # to the boundary_list
            if field.adjacent_mines:
                boundary_list.append(field)

            if field in self.current_adjacent_fields:
                self.current_adjacent_fields.remove(field)
        return boundary_list

    def make_constraint(self, row_index, col_index):
        """
        Compute equations for field (row_index, col_index)
        """

        adjacent_fields = self.game.get_adjacent_fields(row_index, col_index)
        adjacent_mines = self.game.get_adjacent_mines(row_index, col_index)

        assert adjacent_mines
        for field in adjacent_fields:
            if field not in self.current_adjacent_fields \
                    and self.game.board[field.row][field.column].covered \
                    and field not in self.mines:
                self.current_adjacent_fields.append(field)

        literals = []
        for field in adjacent_fields:
            if field.covered:
                literals.append(field.id)

        return CardEnc.equals(lits=literals, bound=adjacent_mines, encoding=EncType.native)

    def first_step(self, first_field=None):
        self.solver.append_formula(
            CardEnc.equals(lits=list(range(1, self.game.board_dim ** 2 + 1)), bound=self.game.num_mines,
                           encoding=EncType.native))

        if first_field:
            row, column = first_field
            self.newly_opened = self.open(self.game.board[row][column])
        else:
            self.newly_opened = self.open(self.get_random_field())

    def step(self):
        for new in self.newly_opened:
            self.solver.append_formula(self.make_constraint(new.row, new.column))

        possible_fields = []
        for field in self.current_adjacent_fields:
            # negative value -> clear field, positive value -> mine
            sat_clear = self.solver.solve(assumptions=self.mines + [-field.id])
            sat_mine = self.solver.solve(assumptions=self.mines + [field.id])
            # if unsatisfiable when field is clear -> mark field as mine
            if not sat_clear:
                self.game.mark_field_dangerous(field)
                self.vars[field.row][field.column] = 1
                self.current_adjacent_fields.remove(field)
                self.mines.append(field.id)
            # if unsatisfiable when filed is mine -> mark field as safe
            elif not sat_mine:
                self.game.mark_field_safe(field)
                self.vars[field.row][field.column] = 0
                if field.is_mine:
                    print("[SAT-PSST] Pushing mined field {} in possible fields".format(field))
                else:
                    print("[SAT] Pushing field {} in possible fields".format(field))
                possible_fields.append(field)

        if possible_fields:
            print("[SAT] Randomly choosing from possible fields: {}".format(possible_fields))
            new_field = choice(possible_fields)
        else:
            print("[SAT] I have no idea what to choose next, randomly generating...")
            new_field = self.get_random_field()

        self.newly_opened = self.open(new_field)
