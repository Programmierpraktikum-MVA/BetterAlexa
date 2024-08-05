from typing import Any
import Move as f


class Piece:
    def __init__(self, name, color):
        self.name = name
        self.color = color
        
    def get_name(self):
        return self.name
