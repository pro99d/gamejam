import json
from base_classes import Vec2
from dataclasses import dataclass

@dataclass
class WallData:
    pos: Vec2
    size: Vec2

class LevelLoader:
    @staticmethod
    def from_json(path):
        with open(path) as file:
            level = json.loads(file.read())
        keys = level.keys()
        walls = []
        if "walls" in keys:
            for wall in level["walls"]:
                dat = wall.keys()
                if "size" in dat:
                    size = wall["size"]
                    size = Vec2(size[0], size[1])
                else:
                    size = Vec2(50, 50)
                if "pos" in dat:
                    pos = wall["pos"]
                    pos = Vec2(pos[0], pos[1])
                else:
                    raise SyntaxError("Invalid walls format!")
                walls.append(WallData(pos, size))

