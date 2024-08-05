class Move:
    def __init__(self, name:str, fr0m: tuple, t0: tuple, take: bool, check: bool, promotion: str):
        self.name = name
        self.fr0m = fr0m
        self.t0 = t0
        self.take = take 
        self.check = check
        self.promotion = promotion

    def __str__(self):
        return str((self.name, self.fr0m, self.t0, self.take, self.check, self.promotion))
    
    def __eq__(self, other):
        if self.name == other.name and self.fr0m == other.fr0m and self.take == other.take and self.check == other.check and self.promotion == other.promotion:
            return True
        return False
