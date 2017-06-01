#!/usr/bin/python

from __future__ import print_function

import random
import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description="""
    
    python generate_random_tiles.py max_zoom

    Generate a list of random tile ids
""")

    parser.add_argument('max_zoom', type=int)
    parser.add_argument('-n', '--num-tiles', default=10,
    			 help="The number of tiles to generate", 
                         type=int)
    #parser.add_argument('-u', '--useless', action='store_true', 
    #					 help='Another useless option')
    args = parser.parse_args()

    zooms = [random.choice(range(args.max_zoom)) for i in range(args.num_tiles)]

    for z in zooms:
        x = random.randint(0, 2 ** z)
        y = random.randint(0, 2 ** z)
        print(z,x,y)
    

if __name__ == '__main__':
    main()


