import csv
import gc
import json
import os
import struct
import sys
from .tee import Tee
import itertools 
import random
from datetime import datetime, timedelta

class TeeManager:
    """Manages tee information"""

    MAGIC_VALUE = -9999999

    def example(self):
        return """
TEE	1	2	3	4	5	6	7	8	9	OUT	10	11	12	13	14	15	16	17	18	IN	TOT
KING	392	415	186	593	185	480	556	456	156	3419	427	376	442	515	325	194	222	637	456	3594	7013
MASTER	341	386	175	578	180	467	548	396	151	3222	356	344	427	476	310	175	191	596	434	3309	6531
PALMER	328	368	157	544	161	440	523	385	145	3051	322	328	379	440	258	154	164	554	390	2989	6040
DEACON	300	314	139	513	141	414	500	341	136	2798	311	301	343	430	229	147	150	520	338	2769	5567
LEGEND	243	258	105	470	102	376	419	296	115	2384	262	283	298	334	223	85	110	512	331	2438	4822
LEGEND (FORWARD)	243	258	105	470	102	376	419	296	115	2384	262	283	298	334	131	85	110	512	331	2346	4730
"""        

    def import_course(self, file_name):
        """Parses a tab-separated values file (tsv). Ignores empty lines and those that start with '#'. See scripts/courses/tci.txt for example file layout."""

        # this is what we allow the caller to manipulate via remove_* methods
        self.tees = []

        # this is a copy of what we actually imported so we can allow caller to wipe and restart.
        self.imported_tees = []

        with open(file_name, "r", newline='', encoding="utf-8") as file:
            reader = csv.reader(file, delimiter="\t")

            # slurp in all lines from the file, skipping those that start with # and those that are empty
            for row in reader:
                if row and not row[0].startswith("#") and not row[0].startswith("TEE"):
                    t = Tee().configure(row)
                    self.imported_tees.append(t)
                    self.tees.append(t)
        
    def blacklist_by_tee(self, tee_name):
        """If you want to remove an entire set of tees, pass its name here"""
        # we'll actually remove it from the list of available tees as it will cut down on our processing significantly.
        self.tees = [t for t in self.tees if self.normalize_name(t.name) != self.normalize_name(tee_name)]

    def blacklist_by_hole(self, tee_name, hole_number):
        """If you want to ignore a tee on a specific hole"""
        tee = next(t for t in self.tees if self.normalize_name(t.name) == self.normalize_name(tee_name))
        if (tee):
            # if we remove the hole, it means things can get out of whack.
            # instead we'll leave it there but make its yardage such that it would never be in the desired output.
            yards = tee.holes[int(hole_number) - 1]
            tee.holes[int(hole_number) - 1] = self.MAGIC_VALUE
            tee.holes_by_yards[yards] = self.MAGIC_VALUE

    def normalize_name(self, name):
        return name.lower().replace(" ", "").replace("(", "").replace(")", "").replace("-", "")
    
    def find_in_range(self, path, lower, upper, count):

        # pre-emptive garbage collection for large set purposes
        gc.collect()

        if lower <= 0:
            raise ValueError('lower must be greater than 0')

        # they may have manipulated the tee list, so let's write indexes now.
        for i, t in enumerate(self.tees):
            t.index = i

        # # we need to create a map file.
        # # this is so the huge data file (.data) can be condensed considerably,
        # # as we'll just write the index of the tee in the teemap file instead of the tee name.
        # with open(path + ".tee.map", "w") as file:
        #     file.writelines(f"{tee}\n" for tee in self.tees)
        
        # we save json too for programmatic reasons
        with open(path + ".tee.json", "w") as file:
            json.dump([tee.__dict__ for tee in self.tees], file, indent=4)

        # we have things in objects so they can be manipulated easily.
        # we want to dump yardages into a 2d array so we can use standard tools for doing calculations.
        # note the 2d array is a hole per row, tee per column. each cell represents yardage.
        # e.g.:
        #        | teeA | teeB | teeC
        # --------------------------------
        # Hole 1 | 390  | 402  | 277
        # Hole 2 | 229  | 176  | 123
        # ...

        matrix = self.transform(self.tees)

        # this will kick out potentially trillions of combinations since we have tees ** 18 holes
        # anything to the 18th power is a lot:
        # Two tees   =>   2**18 =>        262,144
        # Three tees =>   3**18 =>    387,420,489
        # Four tees  =>   4**18 => 68,719,476,736

        start = datetime.now()
        print("Starting calculations...")

        with open(path + ".data", "wb") as file:
            chunk = 50000
            big_chunk = chunk * 10
            results = []
            hits = set()
            for i, combo in enumerate(self.capture_combos(matrix, lower, upper)):
                # a combo is a set of yardages.
                # we need to map those back to their tee names for each hole, then record that result.
                result = self.convert_yards_to_teemap_indexes(combo)
                if result not in hits:
                    results.append(result)
                    hits.add(result)
                    hit_count = len(hits)
                    if hit_count >= count:
                        break
                    elif hit_count % chunk == 0:
                        #file.writelines(x for x in results)
                        file.write(struct.pack(f"{len(results)}Q", *results))  # Write as binary
                        tick = datetime.now() - start
                        print(f"\rFound: {hit_count:,}... ({tick})", end="", flush=True)
                        results = []

                    if hit_count % big_chunk == 0:
                        # mem = (sys.getsizeof(hits) + sum(map(sys.getsizeof, hits))) / 1024 / 1024
                        gc.collect()

            if results:
                #file.writelines(x for x in results)
                file.write(struct.pack(f"{len(results)}Q", *results))  # Write as binary

            ended = datetime.now() - start
            print(f"\nFound {hit_count:,} total combinations between {lower} and {upper}. Duration: {ended}")
 
    # dynamically generate the cartesian product
    # of the matrix and filter out all those which don't fall within our expected range
    def capture_combos(self, matrix, lower, upper):
        
        # Shuffle the columns (randomizing each row independently)
        shuffled_matrix = [random.sample(row, len(row)) for row in matrix]

        for combo in itertools.product(*shuffled_matrix):
            total = sum(combo)
            if total >= lower and total <= upper:
            #if total >= lower and total <= upper and total not in totals:
                #totals[total] = total
                yield combo

    def convert_yards_to_teemap_indexes(self, combo):
        rv = [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
        for i, yard in enumerate(combo):
            for t in self.tees:
                if t.holes[i] == yard:
                    rv[i] = t.index
                    break
                # if yard in t.holes_by_yards:
                #     rv[i] = t.holes_by_yards[yard]
                #     break
        #return "".join(map(str, rv)) + "\n"
        return int(("".join(map(str, rv))))

    def transform(self, tees):
        # we have data like this:
        # obj    h1   h2   h3   h4
        # Tee(A, 390, 298, 167, 488, ...)
        # Tee(B, 302, 277, 123, 355, ...)

        # what we really want is 2d array like this:
        #     teeA teeB
        #  h1 390  302
        #  h2 298  277
        # ...

        # so we're going to do that transform before
        # we get into the expensive operation.
        # we're going to put it into a matrix
        matrix = []
        for index in range(0, 18):
            matrix.append([t.holes[index] for t in tees])

        return matrix

    def select_random(self, input_file):
        data_file = input_file + ".data"
        if (not os.path.exists(data_file)):
            print(f"Could not find {data_file}. Have you successfully imported the course file before?")
            exit(1)
        else:

            json_file = input_file + ".tee.json"
            if (not os.path.exists(json_file)):
                print(f"Could not find {json_file}. Have you successfully imported the course file before?")

            with open(json_file, "r") as file:
                data = json.load(file)
                self.tees = []
                for o in data:
                    t = Tee(**o)
                    self.tees.append(t)
                

            size = os.path.getsize(data_file)
            entry_count = int(size / 8) #  8 bytes stores all 18 holes tee indexes (assumes never have more than 9 tees per hole)
            entry = random.randint(0, entry_count-1)

            with open(data_file, "rb") as file:
                newpos = file.seek(entry * 8, 0)
                data = file.read(8)
                [int_value] = struct.unpack("Q", data)

            #print(int_value)

            rv = []
            digits = [int(d) for d in str(int_value).zfill(18)]
            for d in digits:
                rv.append(self.tees[d])

            # size = os.path.getsize(data_file)
            # row_count = int(size / 19) #  19 = 18 holes + \n character
            # row = random.randint(0, row_count)
            # with open(data_file, "rb") as file:
            #     newpos = file.seek(row * 19, 0)
            #     data = file.read(18)
            # rv = []
            # for b in data:
            #     i = b - 48 # 48 = 0 in ascii
            #     rv.append(self.tees[i])
            
            return rv

            
