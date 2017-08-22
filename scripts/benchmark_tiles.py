#!/usr/bin/python

import cooler.contrib.higlass as cch
import h5py
import multiprocessing as mp
import numpy as np
import sys
import time
import argparse

def make_tiles(zoomLevel, x_pos, y_pos, cooler_file, x_width=1, y_width=1):
    '''
    Generate tiles for a given location. This function retrieves tiles for
    a rectangular region of width x_width and height y_width

    Arguments
    ---------
        zoomLevel: int
            The zoom level to retrieve tiles for (e.g. 0, 1, 2... )
        x_pos: int
            The starting x position
        y_pos: int
            The starting y position
        cooler_file: string
            The filename of the cooler file to get the data from
        x_width: int 
            The number of tiles to retrieve along the x dimension
        y_width: int
            The number of tiles to retrieve along the y dimension
    '''
            

    t1 = time.time()
    #print("opening...")
    f = h5py.File(cooler_file, 'r')

    num_values = len(f[str(zoomLevel)]['pixels']['count'])
    num_chunks = f[str(zoomLevel)]['pixels']['count'].chunks[0]
    #print(zoomLevel, x_pos, y_pos, num_values, num_chunks, num_values / num_chunks)


    t2 = time.time()
    info = cch.get_info(cooler_file)
    divisor = 2 ** zoomLevel

    start1 = x_pos * info['max_width'] / divisor
    end1 = (x_pos + x_width) * info['max_width'] / divisor
    start2 = y_pos * info['max_width'] / divisor
    end2 = (y_pos + y_width) * info['max_width'] / divisor

    data = cch.get_data(
        f, zoomLevel, start1, end1 - 1, start2, end2 - 1
    )

    #print("x_width:", x_width)
    #print("y_width:", y_width)
    # split out the individual tiles
    for x_offset in range(0, x_width):
        for y_offset in range(0, y_width):

            start1 = (x_pos + x_offset) * info['max_width'] / divisor
            end1 = (x_pos + 1) * info['max_width'] / divisor
            start2 = (y_pos + y_offset) * info['max_width'] / divisor
            end2 = (y_pos + 1) * info['max_width'] / divisor

            df = data[data['genome_start1'] >= start1]
            df = df[df['genome_start1'] <= end1]

            df = df[df['genome_start2'] >= start2]
            df = df[df['genome_start2'] <= end2]

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

    t3 = time.time()
    print("fetched: {:.3f}, opened {:.3f}".format(t3 - t2, t2 - t1))
    return out

def func(x):
    #print("fetching:", x[:3])
    tile = make_tiles(*x)
    #print("fetched:", x[:3])
    #print("tile:", tile)

def main():
    parser = argparse.ArgumentParser(description="""
    
    python benchmark_tiles.py cooler_file
""")

    parser.add_argument('cooler_file', help="A multires cooler file to read the tiles from")
    parser.add_argument('tiles_list', help="A list of tiles to retrieve")
    parser.add_argument('-t', '--threads', default=1, help="The number of threads to use", type=int)
    parser.add_argument('--combined-tiles', default=False, action='store_true')

    #parser.add_argument('-o', '--options', default='yo',
    #					 help="Some option", type='str')
    #parser.add_argument('-u', '--useless', action='store_true', 
    #					 help='Another useless option')

    args = parser.parse_args()
    pool = mp.Pool(args.threads)

    if args.combined_tiles:
        for line in open(args.tiles_list, 'r'):
            # and extract the z,x,y coordinates
            zxys = [[int(x) for x in p.split('.')] for p in line.strip().split()]

            minx = min([x[1] for x in zxys])
            maxx = max([x[1] for x in zxys])

            miny = min([x[2] for x in zxys])
            maxy = max([x[2] for x in zxys])

            # assume that all requests are for the same zoom level
            # so we take the zoom level from the first entry
            z = zxys[0][0]

            print("parts:", zxys)
            #print("mins:", z, [minx, maxx], [miny, maxy])
            func([z, minx, miny, args.cooler_file, maxx - minx + 1, maxy - miny + 1])
    else:
        tile = make_tile(0,0,0, args.cooler_file)

        tile_poss = []
        for line in open(args.tiles_list, 'r'):
            z,x,y = [int(p) for p in line.strip().split()]
            tile_poss += [[z,x,y,args.cooler_file]]

            #print(z,x,y)

        for tile_pos in tile_poss:
            func(tile_pos)
        #pool.map(func, tile_poss)

if __name__ == '__main__':
    main()
