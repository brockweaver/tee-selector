class Tee:

    def __init__(self, index=-1, name='', holes=[], holes_by_yards={}, front=-1, back=-1, total=-1):
        self.index = index
        self.name = name
        self.holes = holes
        self.holes_by_yards = holes_by_yards
        self.front = front
        self.back = back
        self.total = total

    def configure(self, row):

        ## copied from https://course.bluegolf.com/bluegolf/course/course/tcofiowa/detailedscorecard.htm
        # Click the dropdown at top left of scorecard and select "SHOW ALL"
        # 
        # TEE	1	2	3	4	5	6	7	8	9	OUT	10	11	12	13	14	15	16	17	18	IN	TOT
        # KING	392	415	186	593	185	480	556	456	156	3419	427	376	442	515	325	194	222	637	456	3594	7013
        # MASTER	341	386	175	578	180	467	548	396	151	3222	356	344	427	476	310	175	191	596	434	3309	6531
        # PALMER	328	368	157	544	161	440	523	385	145	3051	322	328	379	440	258	154	164	554	390	2989	6040
        # DEACON	300	314	139	513	141	414	500	341	136	2798	311	301	343	430	229	147	150	520	338	2769	5567
        # LEGEND	243	258	105	470	102	376	419	296	115	2384	262	283	298	334	223	85	110	512	331	2438	4822
        # LEGEND (FORWARD)	243	258	105	470	102	376	419	296	115	2384	262	283	298	334	131	85	110	512	331	2346	4730

        self.index = -1
        self.name = row[0]

        # grab holes 1-9 and convert each one from string to integer        
        # (note slot #0 is the name of the tee)
        front9 = [int(x) for x in row[1:10]]

        # grab holes 10-18 and convert each one from string to integer
        # (note slot #10 is the total for the front 9, aka "OUT")
        back9 = [int(x) for x in row[11:20]]

        # concatenate those two separate arrays into a new one that contains all the holes
        self.holes = front9 + back9

        # create a reverse-lookup from yards to hole offset as this will prove useful later on when doing the large mapping operation
        self.holes_by_yards = {}
        for i, y in enumerate(self.holes):
            self.holes_by_yards[y] = i

        #gather remaining metadata in case we need it later. e.g. front total, back total, all total.
        self.front = int(row[10]) # aka "OUT"
        self.back = int(row[20]) # aka "IN"
        self.total = int(row[21]) # aka "TOT"

        return self


    def __repr__(self):
        # this is called when the class needs to be represented as a string. e.g. print(tee)
        return f"Tee({self.name}, index={self.index}, holes={self.holes}, holes_by_yards={self.holes_by_yards}, front={self.front}, back={self.back}, total={self.total})"
    