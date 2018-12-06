import time
import subprocess
import cnf_creator
import output_creator
import multiprocessing
from multiprocessing import Pool

def main():
    start = time.time()

    # All test Sudokus:
    #('225-2', '225-1', '144-2', '144-1', '100-1', '64-3', '64-2', '64-1', '49-4', '49-3', '49-1', '36-5', '36-4', '36-3', '36-2', '36-1', '25-5', '25-4', '25-3', '25-2', '25-1', '16-5', '16-4', '16-3', '16-2', '16-1', '9-5', '9-4', '9-3', '9-2', '9-1')
    sudokus = ('64-3', '64-2', '64-1', '49-4', '49-3', '49-1', '36-5', '36-4', '36-3', '36-2', '36-1', '25-5', '25-4', '25-3', '25-2', '25-1', '16-5', '16-4', '16-3', '16-2', '16-1', '9-5', '9-4', '9-3', '9-2', '9-1')


    for name in sudokus:
        cnf_creator.create_cnf(name)
    checkpoint = time.time()
    print('\nFINISHED CREATING ALL CNF FILES, time needed: ' + str( round(checkpoint-start, 3))) + 's'
    print('-------------------------------------------------------\n')


    pool = Pool(processes = multiprocessing.cpu_count())
    pool.map(output_creator.create_output, sudokus)
    pool.close()
    pool.join()
    print('\nFINISHED CREATING ALL OUTPUT FILES, time needed: ' + str( round(time.time()-checkpoint, 3))) + 's'
    print('=======================================================\n')
    print('ALL SUDOKUS HAVE BEEN SOLVED, total time was: ' + str( round( time.time()-start, 3))) + 's\n'


if __name__ == '__main__':
    main()
