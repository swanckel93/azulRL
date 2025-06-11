from enum import Enum, auto
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import random
from .data_model import TileType


@dataclass
class Tile:
    type: TileType

    def __hash__(self):
        return hash(self.type)

    def __eq__(self, other):
        return isinstance(other, Tile) and self.type == other.type


@dataclass
class Container:
    def __init__(self):
        self.tiles: List[Tile] = []

    def add_tile(self, tile: Tile) -> None:
        self.tiles.append(tile)

    def add_tiles(self, tiles: List[Tile]) -> None:
        self.tiles.extend(tiles)

    def remove_tile(self, tile_type: TileType) -> Optional[Tile]:
        for i, tile in enumerate(self.tiles):
            if tile.type == tile_type:
                return self.tiles.pop(i)
        return None

    def remove_all_tiles(self, tile_type: TileType) -> List[Tile]:
        removed = [tile for tile in self.tiles if tile.type == tile_type]
        self.tiles = [tile for tile in self.tiles if tile.type != tile_type]
        return removed

    def count_by_type(self, tile_type: TileType) -> int:
        return sum(1 for tile in self.tiles if tile.type == tile_type)

    def get_unique_types(self) -> List[TileType]:
        return list(set(tile.type for tile in self.tiles))

    def clear(self) -> List[Tile]:
        tiles = self.tiles.copy()
        self.tiles.clear()
        return tiles

    def is_empty(self) -> bool:
        return len(self.tiles) == 0


@dataclass
class Bag(Container):
    def __post_init__(self):
        super().__init__()
        self._initialize_bag()

    def _initialize_bag(self):
        # 20 tiles of each color
        for tile_type in [
            TileType.BLUE,
            TileType.YELLOW,
            TileType.RED,
            TileType.BLACK,
            TileType.WHITE,
        ]:
            for _ in range(20):
                self.add_tile(Tile(tile_type))
        random.shuffle(self.tiles)

    def draw_tiles(self, count: int) -> List[Tile]:
        drawn = self.tiles[:count]
        self.tiles = self.tiles[count:]
        return drawn


@dataclass
class Factory(Container):
    id: int

    def __post_init__(self):
        super().__init__()

    def fill_from_bag(self, bag: Bag) -> None:
        if bag.is_empty():
            return
        tiles_to_draw = min(4, len(bag.tiles))
        self.add_tiles(bag.draw_tiles(tiles_to_draw))


@dataclass
class PatternLine:
    capacity: int
    tiles: List[Tile] = field(default_factory=list)

    def can_add_tile(self, tile_type: TileType) -> bool:
        if self.is_full():
            return False
        if self.is_empty():
            return True
        return self.tiles[0].type == tile_type

    def add_tiles(self, tiles: List[Tile]) -> int:
        # Returns number of overflow tiles
        if not tiles or not self.can_add_tile(tiles[0].type):
            return len(tiles)

        space_available = self.capacity - len(self.tiles)
        tiles_to_add = min(space_available, len(tiles))
        self.tiles.extend(tiles[:tiles_to_add])
        return len(tiles) - tiles_to_add

    def is_full(self) -> bool:
        return len(self.tiles) == self.capacity

    def is_empty(self) -> bool:
        return len(self.tiles) == 0

    def clear(self) -> List[Tile]:
        tiles = self.tiles.copy()
        self.tiles.clear()
        return tiles

    def get_tile_type(self) -> Optional[TileType]:
        return self.tiles[0].type if self.tiles else None


@dataclass
class PlayerBoard:
    pattern_lines: List[PatternLine] = field(
        default_factory=lambda: [PatternLine(i + 1) for i in range(5)]
    )
    wall: List[List[bool]] = field(
        default_factory=lambda: [[False] * 5 for _ in range(5)]
    )
    floor: List[Tile] = field(default_factory=list)
    score: int = 0

    # Wall pattern (row, col) -> TileType
    WALL_PATTERN = [
        [TileType.BLUE, TileType.YELLOW, TileType.RED, TileType.BLACK, TileType.WHITE],
        [TileType.WHITE, TileType.BLUE, TileType.YELLOW, TileType.RED, TileType.BLACK],
        [TileType.BLACK, TileType.WHITE, TileType.BLUE, TileType.YELLOW, TileType.RED],
        [TileType.RED, TileType.BLACK, TileType.WHITE, TileType.BLUE, TileType.YELLOW],
        [TileType.YELLOW, TileType.RED, TileType.BLACK, TileType.WHITE, TileType.BLUE],
    ]

    FLOOR_PENALTIES = [-1, -1, -2, -2, -2, -3, -3]

    def can_place_in_pattern_line(self, line_idx: int, tile_type: TileType) -> bool:
        if line_idx < 0 or line_idx >= 5:
            return False

        pattern_line = self.pattern_lines[line_idx]
        if not pattern_line.can_add_tile(tile_type):
            return False

        # Check if this tile type can go on the wall at this row
        wall_col = self.WALL_PATTERN[line_idx].index(tile_type)
        return not self.wall[line_idx][wall_col]

    def add_tiles_to_pattern_line(self, line_idx: int, tiles: List[Tile]) -> None:
        if line_idx == -1:  # Floor line
            self.floor.extend(tiles)
        else:
            overflow = self.pattern_lines[line_idx].add_tiles(tiles)
            if overflow > 0:
                self.floor.extend(tiles[-overflow:])

    def move_completed_lines_to_wall(self) -> List[Tile]:
        # Returns tiles to be discarded
        discarded = []

        for i, pattern_line in enumerate(self.pattern_lines):
            if pattern_line.is_full():
                tile_type = pattern_line.get_tile_type()
                if tile_type is None:
                    continue  # Should never happen for full lines, but type safety
                wall_col = self.WALL_PATTERN[i].index(tile_type)

                # Place one tile on wall
                self.wall[i][wall_col] = True

                # Discard the rest
                tiles = pattern_line.clear()
                discarded.extend(tiles[1:])  # Keep one for wall, discard rest

        return discarded

    def calculate_round_score(self) -> int:
        points = 0

        # Score wall placements
        for row in range(5):
            for col in range(5):
                if self.wall[row][col]:
                    # Check if this was placed this round (simplified - in real game you'd track this)
                    points += self._calculate_tile_score(row, col)

        # Floor penalties
        floor_penalty = sum(
            self.FLOOR_PENALTIES[i]
            for i in range(min(len(self.floor), len(self.FLOOR_PENALTIES)))
        )
        points += floor_penalty

        return points

    def _calculate_tile_score(self, row: int, col: int) -> int:
        # Simplified scoring - count adjacent tiles
        score = 1

        # Check horizontal
        left = col - 1
        while left >= 0 and self.wall[row][left]:
            score += 1
            left -= 1

        right = col + 1
        while right < 5 and self.wall[row][right]:
            score += 1
            right += 1

        # Check vertical
        up = row - 1
        while up >= 0 and self.wall[up][col]:
            score += 1
            up -= 1

        down = row + 1
        while down < 5 and self.wall[down][col]:
            score += 1
            down += 1

        return score

    def clear_floor(self) -> List[Tile]:
        tiles = self.floor.copy()
        self.floor.clear()
        return tiles

    def has_complete_row(self) -> bool:
        return any(all(self.wall[row]) for row in range(5))

    def count_complete_horizontal_lines(self) -> int:
        """Count the number of complete horizontal lines (rows) on the wall"""
        return sum(1 for row in range(5) if all(self.wall[row]))

    def count_complete_vertical_lines(self) -> int:
        """Count the number of complete vertical lines (columns) on the wall"""
        return sum(
            1 for col in range(5) if all(self.wall[row][col] for row in range(5))
        )

    def count_complete_color_sets(self) -> int:
        """Count the number of complete color sets (all 5 tiles of one color)"""
        color_counts = {
            tile_type: 0 for tile_type in TileType if tile_type != TileType.FIRST_PLAYER
        }

        # Count tiles of each color on the wall
        for row in range(5):
            for col in range(5):
                if self.wall[row][col]:
                    tile_type = self.WALL_PATTERN[row][col]
                    if tile_type in color_counts:
                        color_counts[tile_type] += 1

        # Count how many colors have all 5 tiles placed
        return sum(1 for count in color_counts.values() if count == 5)

    def calculate_final_score(self) -> int:
        """Calculate the final score including bonus points"""
        final_score = self.score  # Start with current score

        # Bonus points for complete horizontal lines (2 points each)
        final_score += self.count_complete_horizontal_lines() * 2

        # Bonus points for complete vertical lines (7 points each)
        final_score += self.count_complete_vertical_lines() * 7

        # Bonus points for complete color sets (10 points each)
        final_score += self.count_complete_color_sets() * 10

        return max(0, final_score)  # Score cannot go below 0
