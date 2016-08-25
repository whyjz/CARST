import multiprocessing
import subprocess
import time;


def calculate(value):
    return value*10;


if __name__ == '__main__':
    #print(multiprocessing.cpu_count());
    #pool=multiprocessing.Pool(None);
    pool=multiprocessing.Pool(processes=2);

    N=5*10**6;
    tasks=range(N);

    results=[];

    print(time.clock());
    r = pool.map_async(calculate, tasks, chunksize=10000, callback=results.append);
    r.wait();
    print(time.clock());
