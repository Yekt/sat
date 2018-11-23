import math


def main():
    n = 9
    n_sub = int(math.sqrt(n))

    # those should be calculated
    nv = 999
    nc = 11979

    grid = [["-" for x in range(n)] for y in range(n)]

    setup_sudoku(grid)
    print_grid(grid)

    f = open('sudo.cnf', 'w')
    f.write("p cnf " + str(nv) + " " + str(nc) + "\n")

    # EACH ENTRY

    # AT LEAST ONE NUMBER
    for x in range(1, n+1):
        for y in range(1, n+1):
            for z in range(1, 10):
                f.write(ctv(x, y, z) + ' ')
            f.write("0\n")
            nc += 1

    # AT MOST ONE NUMBER
    for x in range(1, n+1):
        for y in range(1, n+1):
            for z in range(1, 9):
                for i in range(z+1, 10):
                    f.write("-" + ctv(x, y, z) + " " + "-" + ctv(x, y, i) + " 0\n")
                    nc += 1

    # EACH ROW

    # EACH NUMBER AT MOST ONCE
    for y in range(1, n+1):
        for z in range(1, 10):
            for x in range(1, n):
                for i in range(x+1, n+1):
                    f.write("-" + ctv(x, y, z) + " " + "-" + ctv(i, y, z) + " 0\n")
                    nc += 1

    # EACH NUMBER AT LEAST ONCE
    for y in range(1, n+1):
        for z in range(1, 10):
            for x in range(1, n+1):
                f.write(ctv(x, y, z) + ' ')
            f.write("0\n")
            nc += 1

    # EACH COLUMN

    # EACH NUMBER AT MOST ONCE
    for x in range(1, n + 1):
        for z in range(1, 10):
            for y in range(1, n):
                for i in range(y + 1, n + 1):
                    f.write("-" + ctv(x, y, z) + " " + "-" + ctv(x, i, z) + " 0\n")
                    nc += 1

    # EACH NUMBER AT LEAST ONCE
    for x in range(1, n+1):
        for z in range(1, 10):
            for y in range(1, n+1):
                f.write(ctv(x, y, z) + ' ')
            f.write("0\n")
            nc += 1

    # SUB-GRID

    # EACH NUMBER AT MOST ONCE
    for z in range(1, 10):
        for i in range(0, n_sub):
            for j in range(0, n_sub):
                for x in range(1, n_sub+1):
                    for y in range(1, n_sub+1):
                        for k in range(y+1, n_sub+1):
                            f.write("-" + ctv((3*i + x), (3*j + y), z) + " -" + ctv((3*i+x), (3*j+k), z) + " 0\n")
                            nc += 1

    for z in range(1, 10):
        for i in range(0, n_sub):
            for j in range(0, n_sub):
                for x in range(1, n_sub+1):
                    for y in range(1, n_sub+1):
                        for k in range(x+1, n_sub+1):
                            for l in range(1, n_sub+1):
                                f.write("-" + ctv((3*i + x), (3*j + y), z) + " -" + ctv((3*i+k), (3*j+l), z) + " 0\n")
                                nc += 1

    # EACH NUMBER AT LEAST ONCE
    for i in range(1, n_sub):
        for j in range(1, n_sub):
            for x in range(1, n_sub+1):
                for y in range(1, n_sub+1):
                    for z in range(1, n+1):
                        f.write(ctv((3*i+x), (3*j+y), z) + " ")
                    f.write("0\n")
                    nc += 1

    # SET EXISTING NUMBERS
    for x in range(n):
        for y in range(n):
            if grid[x][y] != "-":
                f.write(ctv(x+1, y+1, grid[x][y]) + " 0\n")
                nc += 1

    f.close()
    print_file()
    print("nc is " + str(nc))


# convert coordinate with number to variable
def ctv(x, y, z):
    return str(x) + str(y) + str(z)


def print_grid(grid):
    for x in grid:
        for y in x:
            print(y, end=' ')
        print()


def print_file():
    print("===============\nFile CONTENT")
    f = open('sudo.cnf', 'r')
    print(f.read())
    f.close()


def setup_sudoku(grid):
    grid[0][2] = 4
    grid[0][3] = 2
    grid[0][4] = 3
    grid[0][5] = 9
    grid[1][1] = 8
    grid[1][3] = 5
    grid[1][5] = 6

    grid[2][0] = 9
    grid[2][3] = 8
    grid[2][5] = 4
    grid[2][7] = 6

    grid[3][0] = 5
    grid[3][1] = 7
    grid[3][2] = 1
    grid[3][6] = 9
    grid[3][7] = 4
    grid[3][8] = 6
    grid[4][0] = 8
    grid[4][8] = 3

    grid[5][0] = 2
    grid[5][1] = 3
    grid[5][2] = 9
    grid[5][6] = 7
    grid[5][7] = 8
    grid[5][8] = 1

    grid[6][3] = 4
    grid[6][5] = 8
    grid[6][8] = 7
    grid[7][2] = 3
    grid[7][3] = 9
    grid[7][5] = 7
    grid[7][7] = 1

    grid[8][3] = 1
    grid[8][4] = 2
    grid[8][5] = 3
    grid[8][6] = 4




if __name__ == '__main__':
    main()