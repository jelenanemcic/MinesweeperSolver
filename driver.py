from test import Minesweeper
from strategy import CSP

if __name__ == "__main__":
    b = Minesweeper(4, 3)
    b.set_mines([(0, 1), (1, 2), (2, 2)])
    b.update()

    for row in b.board:
        print(" ".join([str(v.is_mine) for v in row]))

    for row in b.board:
        print(" ".join([str(v.adjacent_mines) for v in row]))

    b.root.mainloop()
    b.run_strategy(CSP(b), first_field=[3, 0])
