import math
import time
import subprocess
from multiprocessing import Pool


def main():
    start_time = time.time()

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
    print("data read")

    # calculate n
    n = len(sudoku)
    n_sub = int(math.sqrt(n))
    n_len = len(str(n))

    # fill grid
    grid = [["-" for x in range(n)] for y in range(n)]
    for x in range(0, n):
        for y in range(0, n):
            if not sudoku[x][y].startswith("_"):
                grid[x][y] = int(sudoku[x][y])
    print("grid filled")



    ### CONVERTING GRID TO CNF ###
    nv = int(str(n)*3)
    nc = 0

    pool = Pool(processes=5)

    p1 = pool.map_async(process1, [(n,n_sub,n_len),])
    p2 = pool.map_async(process2, [(n,n_sub,n_len),])
    p3 = pool.map_async(process3, [(n,n_sub,n_len),])
    p4 = pool.map_async(process4, [(n,n_sub,n_len),])
    p5 = pool.map_async(process5, [(n,n_sub,n_len),])

    pool.close()
    pool.join()

    c0 = ''
    for x in range(n):
        for y in range(n):
            if grid[x][y] != "-":
                c0 += ctv(x+1, y+1, grid[x][y], n_len) + " 0\n"
                nc += 1
    #print('SET EXISTING NUMBERS')

    c1 = p1.get()[0][0]
    c4 = p1.get()[0][1]
    c6 = p1.get()[0][2]
    c7 = p1.get()[0][3]
    c9 = p1.get()[0][4]
    nc+= p1.get()[0][5]
    c2 = p2.get()[0][0]
    nc+= p2.get()[0][1]
    c3 = p3.get()[0][0]
    nc+= p3.get()[0][1]
    c8 = p4.get()[0][0]
    nc+= p4.get()[0][1]
    c5 = p5.get()[0][0]
    nc+= p5.get()[0][1]

    f = open('sudo.cnf', 'w')
    f.write("p cnf " + str(nv) + " " + str(nc) + "\n")
    f.write(c1)
    f.write(c2)
    f.write(c3)
    f.write(c4)
    f.write(c5)
    f.write(c6)
    f.write(c7)
    f.write(c8)
    f.write(c9)
    f.write(c0)
    f.close()
    print("cnf written")


    ### RUN RISS AND CATCH stdout ###
    riss = subprocess.Popen("./riss_505/bin/riss sudo.cnf", stdout=subprocess.PIPE, shell=True)
    # might be optimizable
    (output, error) = riss.communicate()
    status = riss.wait()
    print('RISS completed')


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
    print('grid completed')


    ### WRITING OUTPUT TXT ###
    out = ''
    # TODO missing information:
        #experiment: generator (Time: 0.001419 s)
        #number of tasks: 1
        #task: 1
        #puzzle size: 3x3
    out += spacer(n_sub, n_len)
    x = 0
    for block_vertical in range(0,n_sub):
        for row in range(0,n_sub):
            out += '| '
            y = 0
            for block_horizontal in range(0,n_sub):
                for col in range(0,n_sub):
                    z = grid[x][y]
                    out += ' ' * (n_len - len(z))
                    out += z + ' '
                    y += 1
                out += '| '
            out += '\n'
            x += 1
        out += spacer(n_sub, n_len)
    txt = open('output.txt', 'w')
    txt.write(out)
    txt.close()
    print('done')
    print('time needed: '+ str(time.time()-start_time))




### splitting the work load in 5 processes for multi core use ###
def process1(triple):
    print('->PROCESS 1 started')
    t = time.time()
    nc = 0
    n = triple[0]
    n_sub = triple[1]
    n_len = triple[2]
    c1 = ''
    for x in range(1, n+1):
        for y in range(1, n+1):
            for z in range(1, n+1):
                c1 += ctv(x, y, z, n_len) + ' '
            c1 += "0\n"
            nc += 1
    #print('EACH ENTRY, at least one number')
    c4 = ''
    for x in range(1, n+1):
        for z in range(1, n+1):
            for y in range(1, n+1):
                c4 += ctv(x, y, z, n_len) + ' '
            c4 += "0\n"
            nc += 1
    #print('EACH ROW, each number at least once')
    c6 = ''
    for y in range(1, n+1):
        for z in range(1, n+1):
            for x in range(1, n+1):
                c6 += ctv(x, y, z, n_len) + ' '
            c6 += "0\n"
            nc += 1
    #print('EACH COLUMN, each number at least once')
    c7 = ''
    for z in range(1, n+1):
        for i in range(0, n_sub):
            for j in range(0, n_sub):
                for x in range(1, n_sub+1):
                    for y in range(1, n_sub+1):
                        for k in range(y+1, n_sub+1):
                            c7 += "-" + ctv((n_sub*i + x), (n_sub*j + y), z, n_len) + " -" + ctv((n_sub*i+x), (n_sub*j+k), z, n_len) + " 0\n"
                            nc += 1
    #print('SUB-GRID, each number at most once (1)')
    c9 = ''
    for i in range(1, n_sub):
        for j in range(1, n_sub):
            for x in range(1, n_sub+1):
                for y in range(1, n_sub+1):
                    for z in range(1, n+1):
                        c9 += ctv((n_sub*i+x), (n_sub*j+y), z, n_len) + " "
                    c9 += "0\n"
                    nc += 1
    #print('SUB-GRID, each number at least once')
    print('->PROCESS 1 finished, total time: ' + str(time.time() - t))
    return (c1,c4,c6,c7,c9,nc)


def process2(triple):
    print('->PROCESS 2 started')
    t = time.time()
    nc = 0
    n = triple[0]
    n_sub = triple[1]
    n_len = triple[2]
    c2 = ''
    for x in range(1, n+1):
        for y in range(1, n+1):
            for z in range(1, n):
                for i in range(z+1, n+1):
                    c2 += "-" + ctv(x, y, z, n_len) + " " + "-" + ctv(x, y, i, n_len) + " 0\n"
                    nc += 1
    #print('EACH ENTRY, at most one number')
    print('->PROCESS 2 finished, total time: ' + str(time.time() - t))
    return (c2,nc)


def process3(triple):
    print('->PROCESS 3 started')
    t = time.time()
    nc = 0
    n = triple[0]
    n_len = triple[2]
    c3 = ''
    for x in range(1, n + 1):
        for z in range(1, n+1):
            for y in range(1, n):
                for i in range(y + 1, n + 1):
                    c3 += "-" + ctv(x, y, z, n_len) + " " + "-" + ctv(x, i, z, n_len) + " 0\n"
                    nc += 1
    #print('EACH ROW, each number at most once')
    print('->PROCESS 3 finished, total time: ' + str(time.time() - t))
    return (c3,nc)


def process4(triple):
    print('->PROCESS 4 started')
    t = time.time()
    nc = 0
    n = triple[0]
    n_sub = triple[1]
    n_len = triple[2]
    c8 = ''
    for z in range(1, n+1):
        for i in range(0, n_sub):
            for j in range(0, n_sub):
                for x in range(1, n_sub+1):
                    for y in range(1, n_sub+1):
                        for k in range(x+1, n_sub+1):
                            for l in range(1, n_sub+1):
                                c8 += "-" + ctv((n_sub*i + x), (n_sub*j + y), z, n_len) + " -" + ctv((n_sub*i+k), (n_sub*j+l), z, n_len) + " 0\n"
                                nc += 1
    #print('SUB-GRID, each number at most once (2)')
    print('->PROCESS 4 finished, total time: ' + str(time.time() - t))
    return (c8,nc)


def process5(triple):
    print('->PROCESS 5 started')
    t = time.time()
    nc = 0
    n = triple[0]
    n_len = triple[2]
    c5 = ''
    for y in range(1, n+1):
        for z in range(1, n+1):
            for x in range(1, n):
                for i in range(x+1, n+1):
                    c5 += "-" + ctv(x, y, z, n_len) + " " + "-" + ctv(i, y, z, n_len) + " 0\n"
                    nc += 1
    #print('EACH COLUMN, each number at most once')
    print('->PROCESS 5 finished, total time: ' + str(time.time() - t))
    return (c5,nc)




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


if __name__ == '__main__':
    main()
