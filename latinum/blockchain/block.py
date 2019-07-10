from typing import Optional

from latinum.utils import random_string

class Block():
    
    def __init__(self, id:str, previous:'Block', difficulty:float, height:Optional[int]=None, time:Optional[float]=None):
        self.id = id
        self.previous = previous
        self.difficulty = difficulty
        self.height = height
        self.time = time

    def __str__(self):
        height_info = " ({})".format(self.height) if self.height is not None else ""
        return "[{} : {}{}]".format(self.id, self.difficulty, height_info)

    @classmethod
    def new_id(self) -> str:
        return random_string(8)

    @property
    def weight(self) -> float:
        return self.difficulty

    def copy(self) -> 'Block':
        # Don't include height
        return Block(id=self.id, previous=self.previous, difficulty=self.difficulty, time=self.time)
