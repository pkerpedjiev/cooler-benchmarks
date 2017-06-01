This is a script to test how quickly regions can be fetched from a cooler file

### Getting the data

```
wget -P data/ https://s3.amazonaws.com/pkerp/public/Rao2014-GM12878-MboI-allreps-filtered.100kb.multires.cool
```

### Generating a list of tile ids

We need to generate a list of tile ids that will be used to test cooler's
tile fetching performance.

```
python scripts/generate_random_tiles.py 7 -n 100 > data/tile_list.txt
```

In this instance, `7` is the maximum zoom level and `-n 100` indicates that we should
generate 100 tile ids.

### Running the benchmark

This script will fetch each of the tiles listed in the `tile_list.txt` file generated above.

```
/usr/bin/time python scripts/benchmark_tiles.py data/Rao2014-GM12878-MboI-allreps-filtered.100kb.multires.cool data/tile_list.txt
```

