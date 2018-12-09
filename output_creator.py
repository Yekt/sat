import time
import math
import subprocess

def create_output(name='-bsp'):
    start = time.time()

    # run riss
    riss = subprocess.Popen('./riss_505/bin/riss ./cnf/table'+name+'.cnf', stdout=subprocess.PIPE, shell=True)
    (output, error) = riss.communicate()

    # complete grid from riss output
    result = output.split(' ')
    del result[-1:]

    n_str = str( abs( int( result[len(result)-1] )))
    n_len = int(len(n_str) / 3)
    n = int(n_str[:n_len])
    n_sub = int(math.sqrt(n))
    grid = [['-' for x in range(n)] for y in range(n)]

    finished = False
    while not finished:
        value = result.pop()
        if not value.startswith("-"):
            z = str(int(value[ len(value)-n_len: len(value)]))
            value = value[:-n_len]
            y = int(value[ len(value)-n_len: len(value)]) -1
            value = value[:-n_len]
            x = int(value) -1
            grid[x][y] = z
            if x==0 and y==0: finished = True


    # test finished sudoku
    check = 'CORRECT'
    for x in range(0,n):
        nbrs = []
        for y in range(0,n):
            nbrs.append(int(grid[x][y]))
        nbrs.sort()
        if nbrs != range(1,n+1):
            check = 'ERROR'
    for y in range(0,n):
        nbrs = []
        for x in range(0,n):
            nbrs.append(int(grid[x][y]))
        nbrs.sort()
        if nbrs != range(1,n+1):
            check = 'ERROR'
    for i in range(0,n_sub):
        for j in range(0,n_sub):
            nbrs = []
            for x in range(0,n_sub):
                xpos = i*n_sub + x
                for y in range(0,n_sub):
                    ypos = j*n_sub + y
                    nbrs.append(int(grid[xpos][ypos]))
            nbrs.sort()
            if nbrs != range(1,n+1):
                check = 'ERROR'
    for j in range(0,n_sub):
        for i in range(0,n_sub):
            nbrs = []
            for x in range(0,n_sub):
                xpos = i*n_sub + x
                for y in range(0,n_sub):
                    ypos = j*n_sub + y
                    nbrs.append(int(grid[xpos][ypos]))
            nbrs.sort()
            if nbrs != range(1,n+1):
                check = 'ERROR'


    # creating output txt
    out = spacer(n_sub, n_len)
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
    txt = open('./outputs/result'+name+'.txt', 'a')
    txt.write('puzzle size: ' + str(n_sub) + 'x' + str(n_sub) + '\n' + out)
    txt.close()

    print(check + ' table'+name+' output was created, in ' + str( round(time.time()-start, 3))) + 's'


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
    create_output()
