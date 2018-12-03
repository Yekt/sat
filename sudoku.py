import math
import subprocess


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

    # calculate n
    n = len(sudoku)
    n_sub = int(math.sqrt(n))
    n_len = len(str(n))
    #print('Sudoku size is %sx%s' % (n, n))

    # fill grid
    grid = [["-" for x in range(n)] for y in range(n)]
    for x in range(0, n):
        for y in range(0, n):
            if not sudoku[x][y].startswith("_"):
                grid[x][y] = int(sudoku[x][y])
    #print(grid)



    ### CONVERTING GRID TO CNF ###
    nv = int(str(n)*3)
    nc = 0
    content = ''

    # TODO fix cnf algorithm for sudokus larger than 9x9
    # EACH ENTRY

    # AT LEAST ONE NUMBER
    for x in range(1, n+1):
        for y in range(1, n+1):
            for z in range(1, n+1):
                content += ctv(x, y, z, n_len) + ' '
            content += "0\n"
            nc += 1

    # AT MOST ONE NUMBER
    for x in range(1, n+1):
        for y in range(1, n+1):
            for z in range(1, n):
                for i in range(z+1, n+1):
                    content += "-" + ctv(x, y, z, n_len) + " " + "-" + ctv(x, y, i, n_len) + " 0\n"
                    nc += 1

    # EACH ROW

    # EACH NUMBER AT MOST ONCE
    for x in range(1, n + 1):
        for z in range(1, n+1):
            for y in range(1, n):
                for i in range(y + 1, n + 1):
                    content += "-" + ctv(x, y, z, n_len) + " " + "-" + ctv(x, i, z, n_len) + " 0\n"
                    nc += 1

    # EACH NUMBER AT LEAST ONCE
    for x in range(1, n+1):
        for z in range(1, n+1):
            for y in range(1, n+1):
                content += ctv(x, y, z, n_len) + ' '
            content += "0\n"
            nc += 1


    # EACH COLUMN

    # EACH NUMBER AT MOST ONCE
    for y in range(1, n+1):
        for z in range(1, n+1):
            for x in range(1, n):
                for i in range(x+1, n+1):
                    content += "-" + ctv(x, y, z, n_len) + " " + "-" + ctv(i, y, z, n_len) + " 0\n"
                    nc += 1

    # EACH NUMBER AT LEAST ONCE
    for y in range(1, n+1):
        for z in range(1, n+1):
            for x in range(1, n+1):
                content += ctv(x, y, z, n_len) + ' '
            content += "0\n"
            nc += 1

    # SUB-GRID

    # EACH NUMBER AT MOST ONCE
    for z in range(1, n+1):
        for i in range(0, n_sub):
            for j in range(0, n_sub):
                for x in range(1, n_sub+1):
                    for y in range(1, n_sub+1):
                        for k in range(y+1, n_sub+1):
                            content += "-" + ctv((n_sub*i + x), (n_sub*j + y), z, n_len) + " -" + ctv((n_sub*i+x), (n_sub*j+k), z, n_len) + " 0\n"
                            nc += 1

    for z in range(1, n+1):
        for i in range(0, n_sub):
            for j in range(0, n_sub):
                for x in range(1, n_sub+1):
                    for y in range(1, n_sub+1):
                        for k in range(x+1, n_sub+1):
                            for l in range(1, n_sub+1):
                                content += "-" + ctv((n_sub*i + x), (n_sub*j + y), z, n_len) + " -" + ctv((n_sub*i+k), (n_sub*j+l), z, n_len) + " 0\n"
                                nc += 1

    # EACH NUMBER AT LEAST ONCE
    for i in range(1, n_sub):
        for j in range(1, n_sub):
            for x in range(1, n_sub+1):
                for y in range(1, n_sub+1):
                    for z in range(1, n+1):
                        content += ctv((n_sub*i+x), (n_sub*j+y), z, n_len) + " "
                    content += "0\n"
                    nc += 1

    # SET EXISTING NUMBERS
    for x in range(n):
        for y in range(n):
            if grid[x][y] != "-":
                content += ctv(x+1, y+1, grid[x][y], n_len) + " 0\n"
                nc += 1

    f = open('sudo.cnf', 'w')
    f.write("p cnf " + str(nv) + " " + str(nc) + "\n")
    f.write(content)
    f.close()



    ### RUN RISS AND CATCH stdout ###
    riss = subprocess.Popen("./riss_505/bin/riss sudo.cnf", stdout=subprocess.PIPE, shell=True)
    # might be optimizable
    (output, error) = riss.communicate()
    status = riss.wait()
    print(output)



    ### COMPLETE GRID FROM RISS OUTPUT ###
    result = output.split(' ')
    del result[-1:]
    finished = False
    while not finished:
        value = result.pop()
        if not value.startswith("-"):
            # gets x, y and z from back to front, because riss kills the first leading zero(s)
            z = str(int(value[ len(value)-n_len: len(value)]))
            value = value[:-n_len]
            y = int(value[ len(value)-n_len: len(value)]) -1
            value = value[:-n_len]
            x = int(value) -1
            grid[x][y] = z
            if x==0 and y==0: finished = True




    ### WRITING OUTPUT TXT ###
    # TODO missing information:
        #experiment: generator (Time: 0.001419 s)
        #number of tasks: 1
        #task: 1
        #puzzle size: 3x3
    txt = open('output.txt', 'w')
    txt.write(spacer(n_sub, n_len))
    x = 0
    for block_vertical in range(0,n_sub):
        for row in range(0,n_sub):
            txt.write('| ')
            y = 0
            for block_horizontal in range(0,n_sub):
                for col in range(0,n_sub):
                    z = grid[x][y]
                    txt.write(z)
                    txt.write(' ' * len(z))
                    y += 1
                txt.write('| ')
            txt.write('\n')
            x += 1
        txt.write(spacer(n_sub, n_len))
    txt.close()



# convert coordinate with number to variable and fill with leading zeros
def ctv(x, y, z, length):
    return str(x).zfill(length) + str(y).zfill(length) + str(z).zfill(length)

# creates a spacer for the final sudoku with correct width
def spacer(root, len):
    i = root*len + root + 1
    result = ''
    for plus in range(0,root):
        result += '+'
        for minus in range(0,i):
            result += '-'
    result += '+\n'
    return result

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
