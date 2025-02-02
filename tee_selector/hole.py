class Hole:
    def __init__(self, number, tees):
        self.number = number
        self.tees = tees

    def __repr__(self):
        return f"Hole({self.number}, tees={self.tees})"