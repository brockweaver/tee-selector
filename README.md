# tee-selector
Given a range of total yardages, generate all potential tee combinations for a given course

## To generate the initial data file with 10,000,000 entries:

```bash
python3 main.py -i scripts/courses/tci.txt --blacklist-tees king "legend (forward)" --blacklist-holes 1:Master 3:Deacon --count 10000000 --lower 6100 --upper 6400
```

## To pull a random value from that generated file:

```bash
python3 main.py -i scripts/courses/tci.txt --select-random
```

Run that as many times as you like until you get a tee combination that suits you.

