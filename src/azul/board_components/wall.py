from azul.tile import Tile, TileType
from .tileholder import Tileholder


class Wall(Tileholder):

    WALL_PATTERN = [
        [TileType.BLUE, TileType.YELLOW, TileType.RED, TileType.BLACK, TileType.WHITE],
        [TileType.WHITE, TileType.BLUE, TileType.YELLOW, TileType.RED, TileType.BLACK],
        [TileType.BLACK, TileType.WHITE, TileType.BLUE, TileType.YELLOW, TileType.RED],
        [TileType.RED, TileType.BLACK, TileType.WHITE, TileType.BLUE, TileType.YELLOW],
        [TileType.YELLOW, TileType.RED, TileType.BLACK, TileType.WHITE, TileType.BLUE],
    ]

    def __init__(self):
        super().__init__()
        self.grid = [[None for _ in range(5)] for _ in range(5)]

    def has_tile_type_in_row(self, row: int, tile_type: TileType) -> bool:
        """Check if tile type exists in given row"""
        return any(tile and tile.type == tile_type for tile in self.grid[row])

    def has_complete_horizontal_line(self) -> bool:
        """Check if any horizontal line is complete"""
        return any(all(tile is not None for tile in row) for row in self.grid)

    def place_tile(self, row: int, tile: Tile) -> int:
        """Place tile on wall and return points scored"""
        col = self.WALL_PATTERN[row].index(tile.type)
        self.grid[row][col] = tile
        return self.calculate_points(row, col)

    def calculate_points(self, row: int, col: int) -> int:
        """Calculate points for placing tile at position"""
        points = 0

        # Count horizontal connected tiles
        horizontal_count = 1
        # Count left
        for c in range(col - 1, -1, -1):
            if self.grid[row][c] is not None:
                horizontal_count += 1
            else:
                break
        # Count right
        for c in range(col + 1, 5):
            if self.grid[row][c] is not None:
                horizontal_count += 1
            else:
                break

        # Count vertical connected tiles
        vertical_count = 1
        # Count up
        for r in range(row - 1, -1, -1):
            if self.grid[r][col] is not None:
                vertical_count += 1
            else:
                break
        # Count down
        for r in range(row + 1, 5):
            if self.grid[r][col] is not None:
                vertical_count += 1
            else:
                break

        # Score points
        if horizontal_count > 1:
            points += horizontal_count
        if vertical_count > 1:
            points += vertical_count
        if horizontal_count == 1 and vertical_count == 1:
            points = 1

        return points
