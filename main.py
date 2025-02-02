import argparse
from tee_selector import TeeManager 
from pprint import pprint

tm = TeeManager()

parser = argparse.ArgumentParser(description="Import given file and generate random combinations of tees between the given yardages.")
parser.add_argument("-i", help="File to import course definition for. Should be generated from https://course.bluegolf.com/bluegolf/course/course/tcofiowa/detailedscorecard.htm")
parser.add_argument("--parse-only", action="store_true", help="Parses input file and displays parsed contents (to be sure your import file is formatted properly)")
parser.add_argument("--count-only", action="store_true", help="Parses input file and calculates the total number of possibilities after blacklisting is applied (but excluding yardage range as this is more expensive than just doing the real calculation)")
parser.add_argument("--example", action="store_true", help="output an example import file format")
parser.add_argument("--lower", type=int, help="Lower boundary for total yardage. e.g. 6100", default=6100)
parser.add_argument("--upper", type=int, help="Upper boundary for total yardage. e.g. 6400", default=6800)
parser.add_argument("--max-count", type=int, help="Max number of combinations to generate. Default is 1 million", default=1000)
parser.add_argument("--chunk-size", type=int, help="Number of items to process between scren updates. Default is 5,000. Maximum allowed is 100,000.")
parser.add_argument("--blacklist-tees", nargs="*", help="List of tee names to blacklist" )
parser.add_argument("--blacklist-holes", nargs="*", help="List of hole_number:tee_name to blacklist. e.g. --blacklist-holes 1:master ""3:legend (forward)"" 6:palmer" )
parser.add_argument("--select-random", action="store_true", help="If a .data file has already been generated, this allows you to select a random row from that file and output it in tee format")
parser.add_argument("--abort-on-slow-progress", action="store_true", help="If several rows are inspected consecutively and no result is found, bail out of the process.")
args = parser.parse_args()

path = args.i # "scripts/courses/tci.txt"

if args.example:
    print(tm.example())
    exit(0)

if args.i:

    # parse input file
    tm.import_course(args.i)

    if args.select_random:
        tees = tm.select_random(args.i)
        #pprint(tees)
        total_yardage = sum([t.holes[i] for i, t in enumerate(tees)])
        pprint([f"Hole {i+1:>2} => {t.name}" for i, t in enumerate(tees)])
        print(f"Yardage: {total_yardage}")
        exit(0)


    if args.blacklist_tees:
        for x in args.blacklist_tees:
            tm.blacklist_by_tee(x)


    if args.blacklist_holes:
        for x in args.blacklist_holes:
            arr = x.split(":")
            tm.blacklist_by_hole(arr[1], arr[0])

    if args.parse_only:
        pprint(tm.tees)
        exit(0)


    if args.count_only:
        total = tm.count_possibilities()
        print(f"Total possibilities: {total:,}")
        exit(0)

    tm.find_in_range(args.i, args.lower, args.upper, args.max_count, args.chunk_size or 5000, args.abort_on_slow_progress)