# tee-selector
Given a range of total yardages, generate all potential tee combinations for a given course

## To count the total number of combinations of tees mathematically possible (note this ignores lower/upper range as that is too computationally expensive):

```bash
python3 main.py -i scripts/courses/tci.txt --blacklist-tees king "legend (forward)" --blacklist-holes 1:Master 3:Deacon --count-only
```
Example output:
```text
Total possibilities: 68,719,476,736
```

## To generate the initial data file with 10,000,000 entries:

```bash
 python3 main.py -i scripts/courses/tci.txt --blacklist-tees king "legend (forward)" --blacklist-holes 1:Master 3:Deacon --max-count 100000 --lower 6100 --upper 6400
```

Example output:
```text

```

## To pull a random value from that generated file:

```bash
python3 main.py -i scripts/courses/tci.txt --select-random
```

Example output:
```text
['Hole  1 => LEGEND',
 'Hole  2 => MASTER',
 'Hole  3 => MASTER',
 'Hole  4 => DEACON',
 'Hole  5 => MASTER',
 'Hole  6 => MASTER',
 'Hole  7 => PALMER',
 'Hole  8 => PALMER',
 'Hole  9 => PALMER',
 'Hole 10 => MASTER',
 'Hole 11 => LEGEND',
 'Hole 12 => MASTER',
 'Hole 13 => PALMER',
 'Hole 14 => LEGEND',
 'Hole 15 => DEACON',
 'Hole 16 => MASTER',
 'Hole 17 => MASTER',
 'Hole 18 => MASTER']
Yardage: 6114
```

Run that as many times as you like until you get a tee combination that suits you.

