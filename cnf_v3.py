import math
import time

extendedCNF = True  # choose between minimal and extended encoding


def create_cnf(name='-bsp'):
    start = time.time()

    # get data from file
    with open('./sudokus/table'+name+'.txt') as input:
        input = input.read().split('\n')
    del input[:5]
    del input[-1:]
    sudoku = []
    for line in input:
        if not line.startswith('+') and line is not '':
            data = line.replace('| ', '').replace(' |', '').split(' ')
            while '' in data:
                data.remove('')
            sudoku.append(data)

    n = len(sudoku)
    n_sub = int(math.sqrt(n))
    n_len = len(str(n))
    nv = int(str(n)*3)
    nc = 0
    if extendedCNF:
        nc = int(4*n*n + 4*n*n*bc(n,2))
    else:
        nc =int(n*n + 3*n*n*bc(n,2))

    # fill grid
    grid = [['-' for x in range(n)] for y in range(n)]
    for x in range(0, n):
        for y in range(0, n):
            if not sudoku[x][y].startswith('_'):
                grid[x][y] = int(sudoku[x][y])
                nc += 1


    # create all cnf clauses and write to file TODO optimze
    cnf = open('./cnf/table'+name+'.cnf', 'w')

    clauses = ''  # EACH ENTRY, at least one number
    for x in range(1, n+1):
        for y in range(1, n+1):
            for z in range(1, n+1):
                clauses += ctv(x, y, z, n_len) + ' '
            clauses += "0\n"
            #nc += 1
    cnf.write(clauses)
    clauses = ''  # EACH ROW, each number at most once
    for x in range(1, n + 1):
        for z in range(1, n+1):
            for y in range(1, n):
                for i in range(y + 1, n + 1):
                    clauses += "-" + ctv(x, y, z, n_len) + " " + "-" + ctv(x, i, z, n_len) + " 0\n"
                    #nc += 1
    cnf.write(clauses)
    clauses = ''  # EACH COLUMN, each number at most once
    for y in range(1, n+1):
        for z in range(1, n+1):
            for x in range(1, n):
                for i in range(x+1, n+1):
                    clauses += "-" + ctv(x, y, z, n_len) + " " + "-" + ctv(i, y, z, n_len) + " 0\n"
                    #nc += 1
    cnf.write(clauses)
    clauses = ''  # SUB-GRID, each number at most once (1)
    for z in range(1, n+1):
        for i in range(0, n_sub):
            for j in range(0, n_sub):
                for x in range(1, n_sub+1):
                    for y in range(1, n_sub+1):
                        for k in range(y+1, n_sub+1):
                            clauses += "-" + ctv((n_sub*i + x), (n_sub*j + y), z, n_len) + " -" + ctv((n_sub*i+x), (n_sub*j+k), z, n_len) + " 0\n"
                            #nc += 1
    cnf.write(clauses)
    clauses = ''  # SUB-GRID, each number at most once (2)
    for z in range(1, n+1):
        for i in range(0, n_sub):
            for j in range(0, n_sub):
                for x in range(1, n_sub+1):
                    for y in range(1, n_sub+1):
                        for k in range(x+1, n_sub+1):
                            for l in range(1, n_sub+1):
                                clauses += "-" + ctv((n_sub*i + x), (n_sub*j + y), z, n_len) + " -" + ctv((n_sub*i+k), (n_sub*j+l), z, n_len) + " 0\n"
                                #nc += 1
    cnf.write(clauses)
    clauses = ''  # SET EXISTING NUMBERS
    for x in range(n):
        for y in range(n):
            if grid[x][y] != "-":
                clauses += ctv(x+1, y+1, grid[x][y], n_len) + " 0\n"
                #nc += 1
    cnf.write(clauses)

    if extendedCNF:
        clauses = ''  # EACH ENTRY, at most one number
        for x in range(1, n+1):
            for y in range(1, n+1):
                for z in range(1, n):
                    for i in range(z+1, n+1):
                        clauses += "-" + ctv(x, y, z, n_len) + " " + "-" + ctv(x, y, i, n_len) + " 0\n"
                        #nc += 1
        cnf.write(clauses)
        clauses = ''  # EACH ROW, each number at least once
        for x in range(1, n+1):
            for z in range(1, n+1):
                for y in range(1, n+1):
                    clauses += ctv(x, y, z, n_len) + ' '
                clauses += "0\n"
                #nc += 1
        cnf.write(clauses)
        clauses = ''  # EACH COLUMN, each number at least once
        for y in range(1, n+1):
            for z in range(1, n+1):
                for x in range(1, n+1):
                    clauses += ctv(x, y, z, n_len) + ' '
                clauses += "0\n"
                #nc += 1
        cnf.write(clauses)
        clauses = ''  # SUB-GRID, each number at least once
        for i in range(1, n_sub):
            for j in range(1, n_sub):
                for x in range(1, n_sub+1):
                    for y in range(1, n_sub+1):
                        for z in range(1, n+1):
                            clauses += ctv((n_sub*i+x), (n_sub*j+y), z, n_len) + " "
                        clauses += "0\n"
                        #nc += 1
        cnf.write(clauses)

    cnf.write("p cnf " + str(nv) + " " + str(nc))
    cnf.close()

    print('table'+name+' cnf was created, in ' + str( round(time.time()-start, 3))) + 's'


# convert coordinate with number to variable and fill with leading zeros
def ctv(x, y, z, length):
    return str(x).zfill(length) + str(y).zfill(length) + str(z).zfill(length)

def bc(n,k):
    # Binomial coefficient
    a = math.factorial(n)
    b = math.factorial(k)
    c = math.factorial(n-k)
    return a / (b * c)


if __name__ == '__main__':
    create_cnf()
