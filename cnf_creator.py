import math
import time
from multiprocessing import Pool
import multiprocessing

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

    # fill grid
    grid = [['-' for x in range(n)] for y in range(n)]
    for x in range(0, n):
        for y in range(0, n):
            if not sudoku[x][y].startswith('_'):
                grid[x][y] = int(sudoku[x][y])

    # create all cnf clauses TODO optimze
    pool = Pool(processes = 5)  # multiprocessing.cpu_count()
    p1 = pool.map_async(process1, [(n,n_sub,n_len),])
    p2 = pool.map_async(process2, [(n,n_sub,n_len),])
    p3 = pool.map_async(process3, [(n,n_sub,n_len),])
    p4 = pool.map_async(process4, [(n,n_sub,n_len),])
    if extendedCNF:
        p5 = pool.map_async(process5, [(n,n_sub,n_len),])
    pool.close()
    pool.join()
    p1 = p1.get()
    p2 = p2.get()
    p3 = p3.get()
    p4 = p4.get()
    if extendedCNF:
        p5 = p5.get()


    c0 = ''  # SET EXISTING NUMBERS
    for x in range(n):
        for y in range(n):
            if grid[x][y] != "-":
                c0 += ctv(x+1, y+1, grid[x][y], n_len) + " 0\n"
                nc += 1

    c1 = p1[0][0]
    c7 = p1[0][1]
    nc+= p1[0][2]
    c3 = p2[0][0]
    nc+= p2[0][1]
    c8 = p3[0][0]
    nc+= p3[0][1]
    c5 = p4[0][0]
    nc+= p4[0][1]
    if extendedCNF:
        c2 = p5[0][0]
        nc+= p5[0][1]
        c4 = p1[0][3]
        c6 = p1[0][4]
        c9 = p1[0][5]

    # write cnf file
    f = open('./cnf/table'+name+'.cnf', 'w')
    f.write("p cnf " + str(nv) + " " + str(nc) + '\n')  # TODO writing the 'headline' last works too, which yould be helpfull
    f.write(c1)
    f.write(c3)
    f.write(c5)
    f.write(c7)
    f.write(c8)
    f.write(c0)
    if extendedCNF:
        f.write(c2)
        f.write(c4)
        f.write(c6)
        f.write(c9)
    f.close()

    print('table'+name+' cnf was created, in ' + str( round(time.time()-start, 3))) + 's'



def process1(triple):
    #print('1 start')
    nc = 0
    n = triple[0]
    n_sub = triple[1]
    n_len = triple[2]
    c1 = ''  # EACH ENTRY, at least one number
    for x in range(1, n+1):
        for y in range(1, n+1):
            for z in range(1, n+1):
                c1 += ctv(x, y, z, n_len) + ' '
            c1 += "0\n"
            nc += 1
    c7 = ''  # SUB-GRID, each number at most once (1)
    for z in range(1, n+1):
        for i in range(0, n_sub):
            for j in range(0, n_sub):
                for x in range(1, n_sub+1):
                    for y in range(1, n_sub+1):
                        for k in range(y+1, n_sub+1):
                            c7 += "-" + ctv((n_sub*i + x), (n_sub*j + y), z, n_len) + " -" + ctv((n_sub*i+x), (n_sub*j+k), z, n_len) + " 0\n"
                            nc += 1
    c4, c6, c9 = None, None, None
    if extendedCNF:
        c4 = ''  # EACH ROW, each number at least once
        for x in range(1, n+1):
            for z in range(1, n+1):
                for y in range(1, n+1):
                    c4 += ctv(x, y, z, n_len) + ' '
                c4 += "0\n"
                nc += 1
        c6 = ''  # EACH COLUMN, each number at least once
        for y in range(1, n+1):
            for z in range(1, n+1):
                for x in range(1, n+1):
                    c6 += ctv(x, y, z, n_len) + ' '
                c6 += "0\n"
                nc += 1
        c9 = ''  # SUB-GRID, each number at least once
        for i in range(1, n_sub):
            for j in range(1, n_sub):
               for x in range(1, n_sub+1):
                    for y in range(1, n_sub+1):
                        for z in range(1, n+1):
                            c9 += ctv((n_sub*i+x), (n_sub*j+y), z, n_len) + " "
                        c9 += "0\n"
                        nc += 1
    #print('1 end')
    return (c1,c7,nc, c4,c6,c9)

def process2(triple):
    #print('2 start')
    nc = 0
    n = triple[0]
    n_len = triple[2]
    c3 = ''  # EACH ROW, each number at most once
    for x in range(1, n + 1):
        for z in range(1, n+1):
            for y in range(1, n):
                for i in range(y + 1, n + 1):
                    c3 += "-" + ctv(x, y, z, n_len) + " " + "-" + ctv(x, i, z, n_len) + " 0\n"
                    nc += 1
    #print('2 end')
    return (c3,nc)

def process3(triple):
    #print('3 start')
    nc = 0
    n = triple[0]
    n_sub = triple[1]
    n_len = triple[2]
    c8 = ''  # SUB-GRID, each number at most once (2)
    for z in range(1, n+1):
        for i in range(0, n_sub):
            for j in range(0, n_sub):
                for x in range(1, n_sub+1):
                    for y in range(1, n_sub+1):
                        for k in range(x+1, n_sub+1):
                            for l in range(1, n_sub+1):
                                c8 += "-" + ctv((n_sub*i + x), (n_sub*j + y), z, n_len) + " -" + ctv((n_sub*i+k), (n_sub*j+l), z, n_len) + " 0\n"
                                nc += 1
    #print('3 end')
    return (c8,nc)

def process4(triple):
    #print('4 start')
    nc = 0
    n = triple[0]
    n_len = triple[2]
    c5 = ''  # EACH COLUMN, each number at most once
    for y in range(1, n+1):
        for z in range(1, n+1):
            for x in range(1, n):
                for i in range(x+1, n+1):
                    c5 += "-" + ctv(x, y, z, n_len) + " " + "-" + ctv(i, y, z, n_len) + " 0\n"
                    nc += 1
    #print('4 end')
    return (c5,nc)

def process5(triple):
    #print('5 start')
    nc = 0
    n = triple[0]
    n_len = triple[2]
    c2 = ''  # EACH ENTRY, at most one number
    for x in range(1, n+1):
        for y in range(1, n+1):
            for z in range(1, n):
                for i in range(z+1, n+1):
                    c2 += "-" + ctv(x, y, z, n_len) + " " + "-" + ctv(x, y, i, n_len) + " 0\n"
                    nc += 1
    #print('5 end')
    return (c2,nc)

# convert coordinate with number to variable and fill with leading zeros
def ctv(x, y, z, length):
    return str(x).zfill(length) + str(y).zfill(length) + str(z).zfill(length)



if __name__ == '__main__':
    create_cnf()
