import math


def main():

    ### READING INPUT FILE ###
    with open ("bsp-sudoku-input.txt", "r") as input:
        raw = input.read().split('\n')

    # trimm raw data
    del raw[:5]
    del raw[-1:]
    sudoku = []
    for line in raw:
        if not line.startswith("+") and line is not "":
            data = line.replace("| ", "").replace(" |", "").split(" ")
            while "" in data:
                data.remove("")
            sudoku.append(data)
    print(sudoku)

    # calculate n
    n = len(sudoku)
    n_sub = int(math.sqrt(n))
    print(n)

    # fill grid
    grid = [["-" for x in range(n)] for y in range(n)]
    for x in range(0, n):
        for y in range(0, n):
            if not sudoku[x][y].startswith("_"):
                grid[x][y] = int(sudoku[x][y])
    #print_grid(grid)



    ### CONVERTING GRID TO CNF ###
    # those should be calculated
    nv = 999
    nc = 11979

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
    #print_file()
    #print("nc is " + str(nc))


# convert coordinate with number to variable
def ctv(x, y, z):
    return str(x) + str(y) + str(z)


def print_grid(grid):
    for x in grid:
        for y in x:
            end= ' '
            print(y, end)
        print()


def print_file():
    print("===============\nFile CONTENT")
    f = open('sudo.cnf', 'r')
    print(f.read())
    f.close()


if __name__ == '__main__':
    main()
