from enum import Enum, auto


class TileID(Enum):
    WALL = auto()


char_to_tile_id = {
    "#": TileID.WALL,
}


tile_health = {
    TileID.WALL: 100,
}


class Tile:
    def __init__(self, pos: tuple[int, int], tile_id: str):
        self.pos = pos
        self.id = char_to_tile_id[tile_id]
        self.health = tile_health.get(self.id, 100)
