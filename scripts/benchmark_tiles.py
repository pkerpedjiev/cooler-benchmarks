#!/usr/bin/python

import cooler.contrib.higlass as cch
import h5py
import numpy as np
import sys
import argparse

def make_tile(zoomLevel, x_pos, y_pos, dset):
    info = dset[1]
    divisor = 2 ** zoomLevel

    start1 = x_pos * info['max_width'] / divisor
    end1 = (x_pos + 1) * info['max_width'] / divisor
    start2 = y_pos * info['max_width'] / divisor
    end2 = (y_pos + 1) * info['max_width'] / divisor

    data = cch.get_data(
        dset[0], zoomLevel, start1, end1 - 1, start2, end2 - 1
    )

    df = data[data['genome_start1'] >= start1]

    binsize = dset[0].attrs[str(zoomLevel)]
    j = (df['genome_start1'].values - start1) // binsize
    i = (df['genome_start2'].values - start2) // binsize

    if 'balanced' in df:
        v = np.nan_to_num(df['balanced'].values)
    else:
        v = np.nan_to_num(df['count'].values)

    out = np.zeros(65536, dtype=np.float32)  # 256^2
    index = (i * 256) + j

    if len(v):
        out[index] = v

    return out

def main():
    parser = argparse.ArgumentParser(description="""
    
    python benchmark_tiles.py cooler_file
""")

    parser.add_argument('cooler_file', help="A multires cooler file to read the tiles from")
    parser.add_argument('tiles_list', help="A list of tiles to retrieve")
    #parser.add_argument('-o', '--options', default='yo',
    #					 help="Some option", type='str')
    #parser.add_argument('-u', '--useless', action='store_true', 
    #					 help='Another useless option')

    args = parser.parse_args()

    f = h5py.File(args.cooler_file, 'r')
    dset = (f, cch.get_info(args.cooler_file))


    tile = make_tile(0,0,0, dset)
    for line in open(args.tiles_list, 'r'):
        z,x,y = [int(p) for p in line.strip().split()]

        print(z,x,y)
        tile = make_tile(z,x,y, dset)
    print("tile:", tile)

if __name__ == '__main__':
    main()


