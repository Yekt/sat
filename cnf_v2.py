import math
import time
import multiprocessing as mp
from functools import partial

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
    if extendedCNF:
        nc = int(4*n*n + 4*n*n*bc(n,2))
    else:
        nc =int( n*n + 3*n*n*bc(n,2))

    # fill grid
    grid = [['-' for x in range(n)] for y in range(n)]
    for x in range(0, n):
        for y in range(0, n):
            if not sudoku[x][y].startswith('_'):
                grid[x][y] = int(sudoku[x][y])
                nc += 1

    # create all cnf clauses and write file TODO optimze
    manager = mp.Manager()
    q = manager.Queue()
    pool = mp.Pool(processes = mp.cpu_count()+2)

    w = partial(writer, name, nv, nc)
    guard = pool.apply_async(w, (q,))

    p1 = partial(constraint1, q, n, n_len)
    pool.map_async(p1, range(1,n+1))
    p2 = partial(constraint2, q, n, n_len)
    pool.map_async(p2, range(1,n+1))
    p3 = partial(constraint3, q, n, n_len)
    pool.map_async(p3, range(1,n+1))
    p4 = partial(constraint4, q, n_sub, n_len)
    pool.map_async(p4, range(1,n+1))
    p5 = partial(constraint5, q, n, n_sub, n_len)
    pool.map_async(p5, range(1,n+1))
    if extendedCNF:
        p6 = partial(constraint6, q, n, n_len)
        pool.map_async(p6, range(1,n+1))
        p7 = partial(constraint7, q, n, n_len)
        pool.map_async(p7, range(1,n+1))
        p8 = partial(constraint8, q, n, n_len)
        pool.map_async(p8, range(1,n+1))
        p9 = partial(constraint9, q, n, n_sub, n_len)
        pool.map_async(p9, range(1,n_sub))

    clauses = ''  # SET EXISTING NUMBERS
    for x in range(n):
        for y in range(n):
            if grid[x][y] != "-":
                clauses += ctv(x+1, y+1, grid[x][y], n_len) + " 0\n"
    q.put(clauses)

    pool.close()
    pool.join()

    print('table'+name+' cnf was created, in ' + str( round(time.time()-start, 3))) + 's'



def writer(name, nv, nc, q):
    cnf = open('./cnf/table'+name+'.cnf', 'w')
    cnf.write("p cnf " + str(nv) + " " + str(nc) + '\n')
    while True:
        clause = q.get()
        if clause == 'done':
            break
        cnf.write(clause)
    cnf.close()


def foo(q, n, n_sub, n_len):
    pass


def constraint1(q, n, n_len, x):
    # EACH ENTRY, at least one number
    clauses = ''
    for y in range(1, n+1):
        for z in range(1, n+1):
            clauses += ctv(x, y, z, n_len) + ' '
        clauses += "0\n"
    q.put(clauses)
def constraint2(q, n, n_len, x):
    # EACH ROW, each number at most once
    clauses = ''
    for z in range(1, n+1):
        for y in range(1, n):
            for i in range(y + 1, n + 1):
                clauses += "-" + ctv(x, y, z, n_len) + " " + "-" + ctv(x, i, z, n_len) + " 0\n"
    q.put(clauses)
def constraint3(q, n, n_len, y):
    # EACH COLUMN, each number at most once
    clauses = ''
    for z in range(1, n+1):
        for x in range(1, n):
            for i in range(x+1, n+1):
                clauses += "-" + ctv(x, y, z, n_len) + " " + "-" + ctv(i, y, z, n_len) + " 0\n"
    q.put(clauses)
def constraint4(q, n_sub, n_len, z):
    # SUB-GRID, each number at most once (1)
    clauses = ''
    for i in range(0, n_sub):
        for j in range(0, n_sub):
            for x in range(1, n_sub+1):
                for y in range(1, n_sub+1):
                    for k in range(y+1, n_sub+1):
                        clauses += "-" + ctv((n_sub*i + x), (n_sub*j + y), z, n_len) + " -" + ctv((n_sub*i+x), (n_sub*j+k), z, n_len) + " 0\n"
    q.put(clauses)
def constraint5(q, n, n_sub, n_len, z):
    # SUB-GRID, each number at most once (2)
    clauses = ''
    for i in range(0, n_sub):
        for j in range(0, n_sub):
            for x in range(1, n_sub+1):
                for y in range(1, n_sub+1):
                    for k in range(x+1, n_sub+1):
                        for l in range(1, n_sub+1):
                            clauses += "-" + ctv((n_sub*i + x), (n_sub*j + y), z, n_len) + " -" + ctv((n_sub*i+k), (n_sub*j+l), z, n_len) + " 0\n"
    q.put(clauses)
    if not extendedCNF and z == n:
        q.put('done')

def constraint6(q, n, n_len, x):
    # EACH ENTRY, at most one number
    clauses = ''
    for y in range(1, n+1):
        for z in range(1, n):
            for i in range(z+1, n+1):
                clauses += "-" + ctv(x, y, z, n_len) + " " + "-" + ctv(x, y, i, n_len) + " 0\n"
    q.put(clauses)
def constraint7(q, n, n_len, x):
    # EACH ROW, each number at least once
    clauses = ''
    for z in range(1, n+1):
        for y in range(1, n+1):
            clauses += ctv(x, y, z, n_len) + ' '
        clauses += "0\n"
    q.put(clauses)
def constraint8(q, n, n_len, y):
    # EACH COLUMN, each number at least once
    clauses = ''
    for z in range(1, n+1):
        for x in range(1, n+1):
            clauses += ctv(x, y, z, n_len) + ' '
        clauses += "0\n"
    q.put(clauses)
def constraint9(q, n, n_sub, n_len, i):
    # SUB-GRID, each number at least once
    clauses = ''
    for j in range(1, n_sub):
        for x in range(1, n_sub+1):
            for y in range(1, n_sub+1):
                for z in range(1, n+1):
                    clauses += ctv((n_sub*i+x), (n_sub*j+y), z, n_len) + " "
                clauses += "0\n"
    q.put(clauses)
    if i == n_sub-1:
        q.put('done')


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
