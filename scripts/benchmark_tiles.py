#!/usr/bin/python

import cooler.contrib.higlass as cch
import h5py
import multiprocessing as mp
import numpy as np
import sys
import argparse

def make_tile(zoomLevel, x_pos, y_pos, cooler_file):
    f = h5py.File(cooler_file, 'r')
    info = cch.get_info(cooler_file)
    divisor = 2 ** zoomLevel

    start1 = x_pos * info['max_width'] / divisor
    end1 = (x_pos + 1) * info['max_width'] / divisor
    start2 = y_pos * info['max_width'] / divisor
    end2 = (y_pos + 1) * info['max_width'] / divisor

    data = cch.get_data(
        f, zoomLevel, start1, end1 - 1, start2, end2 - 1
    )

    df = data[data['genome_start1'] >= start1]

    binsize = f.attrs[str(zoomLevel)]
    j = (df['genome_start1'].values - start1) // binsize
    i = (df['genome_start2'].values - start2) // binsize

    if 'balanced' in df:
        v = np.nan_to_num(df['balanced'].values)
    else:
        v = np.nan_to_num(df['count'].values)

    out = np.zeros(65536, dtype=np.float32)  # 256^2
    index = [int(x) for x in (i * 256) + j]

    if len(v):
        out[index] = v

    return out

def func(x):
    print("fetching:", x[:3])
    tile = make_tile(x[0], x[1], x[2], x[3])
    print("fetched:", x[:3])
    print("tile:", tile)

def main():
    parser = argparse.ArgumentParser(description="""
    
    python benchmark_tiles.py cooler_file
""")

    parser.add_argument('cooler_file', help="A multires cooler file to read the tiles from")
    parser.add_argument('tiles_list', help="A list of tiles to retrieve")
    parser.add_argument('-t', '--threads', default=1, help="The number of threads to use", type=int)
    #parser.add_argument('-o', '--options', default='yo',
    #					 help="Some option", type='str')
    #parser.add_argument('-u', '--useless', action='store_true', 
    #					 help='Another useless option')

    args = parser.parse_args()
    pool = mp.Pool(args.threads)

    tile = make_tile(0,0,0, args.cooler_file)

    tile_poss = []
    for line in open(args.tiles_list, 'r'):
        z,x,y = [int(p) for p in line.strip().split()]
        tile_poss += [[z,x,y,args.cooler_file]]

        print(z,x,y)

    pool.map(func, tile_poss)

if __name__ == '__main__':
    main()


