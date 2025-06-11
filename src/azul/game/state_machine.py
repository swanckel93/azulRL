from statemachine import StateMachine, State
from azul.board_components import (
    Tileholder,
    Bag,
    BoardCenter,
    Factory,
    Floorline,
    PlayerBoard,
    StagingLine,
    Wall,
)
from azul.tile import Tile, get_tile_generator, TileType, SpecialTileType


class AzulGame(StateMachine):
    """State machine for Azul board game"""

    # States
    setup = State(initial=True)
    factory_offer = State()
    wall_tiling = State()
    preparing_next_round = State()
    game_ended = State(final=True)

    # Transitions
    start_game = setup.to(factory_offer)
    complete_factory_phase = factory_offer.to(wall_tiling)
    complete_wall_tiling = wall_tiling.to(
        game_ended, cond="game_should_end"
    ) | wall_tiling.to(preparing_next_round, unless="game_should_end")
    start_next_round = preparing_next_round.to(factory_offer)

    def __init__(self, num_players: int = 2, seed: int = 42):
        if num_players < 2 or num_players > 4:
            raise ValueError("Number of players must be between 2 and 4")

        self.num_players = num_players
        self.current_player = 0
        self.starting_player = 0
        self.round_number = 1

        # Game components
        self.players: list[PlayerBoard] = []
        self.factories: list[Factory] = []
        self.board_center = BoardCenter()
        self.bag = None
        self.discard_pile: list[Tile] = []

        # Game state
        self.first_player_token_taken = False
        self.tiles_available = True

        # Initialize tile generator
        self.tile_generator = get_tile_generator()

        super().__init__()

    def game_should_end(self) -> bool:
        """Check if game should end"""
        return any(player.has_completed_horizontal_line() for player in self.players)

    def on_enter_setup(self):
        """Initialize game components"""
        # Create player boards
        self.players = [PlayerBoard(i) for i in range(self.num_players)]

        # Create factories (2n+1 where n is number of players)
        num_factories = 2 * self.num_players + 1
        self.factories = [Factory(4) for _ in range(num_factories)]

        # Create bag with game tiles
        game_tiles = self.tile_generator.create_game_tiles()
        self.bag = Bag(game_tiles)

        # Add special tile to center
        special_tile = self.tile_generator.create_game_special_tile()
        self.board_center.extend([special_tile])

        print(f"Game setup complete for {self.num_players} players")

    def on_enter_factory_offer(self):
        """Fill factories and prepare for tile selection"""
        # FIXED: Fill factories for round 1 as well
        self.fill_factories()

        self.current_player = self.starting_player
        self.first_player_token_taken = False
        self.tiles_available = True

        print(f"Round {self.round_number}: Factory Offer phase started")
        print(f"Player {self.current_player + 1} starts")

    def fill_factories(self):
        """Fill all factories with tiles from bag"""
        for factory in self.factories:
            # FIXED: Clear factory before filling (in case of leftover tiles)
            factory._tiles.clear()

            if len(self.bag) >= 4:
                tiles = self.bag.pop_random(4)
                factory.extend(tiles)
            elif len(self.bag) > 0:
                # Use remaining tiles from bag
                remaining = self.bag.pop_random(len(self.bag))
                factory.extend(remaining)

                # Refill bag from discard pile if needed
                if self.discard_pile and len(factory) < 4:
                    self.bag.extend(self.discard_pile)
                    self.discard_pile.clear()
                    needed = 4 - len(factory)
                    if len(self.bag) >= needed:
                        additional = self.bag.pop_random(needed)
                        factory.extend(additional)

    def take_tiles_from_factory(
        self, factory_index: int, tile_type: TileType
    ) -> list[Tile]:
        """Take all tiles of specific type from factory"""
        if factory_index < 0 or factory_index >= len(self.factories):
            raise ValueError("Invalid factory index")

        factory = self.factories[factory_index]
        taken_tiles = [tile for tile in factory._tiles if tile.type == tile_type]
        remaining_tiles = [tile for tile in factory._tiles if tile.type != tile_type]

        factory._tiles.clear()
        self.board_center.extend(remaining_tiles)

        return taken_tiles

    def take_tiles_from_center(self, tile_type: TileType) -> list[Tile]:
        """Take all tiles of specific type from center"""
        taken_tiles = [
            tile for tile in self.board_center._tiles if tile.type == tile_type
        ]
        remaining_tiles = [
            tile for tile in self.board_center._tiles if tile.type != tile_type
        ]

        self.board_center._tiles.clear()
        self.board_center.extend(remaining_tiles)

        # Handle first player token
        if not self.first_player_token_taken:
            special_tiles = [
                tile for tile in taken_tiles if tile.type == SpecialTileType.TILE_1
            ]
            if special_tiles:
                self.starting_player = self.current_player
                self.first_player_token_taken = True
                # Add to floor line
                self.players[self.current_player].floor_line.extend(special_tiles)
                taken_tiles = [
                    tile for tile in taken_tiles if tile.type != SpecialTileType.TILE_1
                ]

        return taken_tiles

    def place_tiles_on_player_board(
        self, player_index: int, tiles: list[Tile], pattern_line_index: int
    ):
        """Place tiles on player's pattern line"""
        player = self.players[player_index]

        if pattern_line_index < 0 or pattern_line_index >= 5:
            # All tiles go to floor line
            overflow = player.floor_line.add_tiles(tiles)
            self.discard_pile.extend(overflow)
            return

        pattern_line = player.pattern_lines[pattern_line_index]

        if tiles and player.can_place_tile_type_in_pattern_line(
            pattern_line_index, tiles[0].type
        ):
            # Add as many as possible to pattern line
            overflow = pattern_line.add_partially(tiles)
            # Rest go to floor line
            floor_overflow = player.floor_line.add_tiles(overflow)
            self.discard_pile.extend(floor_overflow)
        else:
            # All tiles go to floor line
            overflow = player.floor_line.add_tiles(tiles)
            self.discard_pile.extend(overflow)

    def next_player(self):
        """Move to next player"""
        self.current_player = (self.current_player + 1) % self.num_players

    def check_tiles_available(self) -> bool:
        """Check if any tiles are still available for selection"""
        center_has_tiles = (
            len(
                [
                    t
                    for t in self.board_center._tiles
                    if t.type != SpecialTileType.TILE_1
                ]
            )
            > 0
        )
        factories_have_tiles = any(len(factory) > 0 for factory in self.factories)
        return center_has_tiles or factories_have_tiles

    def on_enter_wall_tiling(self):
        """Wall-tiling phase: move tiles from pattern lines to wall"""
        print("Wall-tiling phase started")

        for player in self.players:
            points_scored = 0

            # Process each pattern line
            for i, pattern_line in enumerate(player.pattern_lines):
                if pattern_line.is_complete():
                    # Move rightmost tile to wall
                    tile = pattern_line._tiles[-1]
                    points = player.wall.place_tile(i, tile)
                    points_scored += points

                    # Discard remaining tiles from pattern line
                    self.discard_pile.extend(pattern_line._tiles[:-1])
                    pattern_line._tiles.clear()

            # Apply floor line penalties
            penalty = player.floor_line.calculate_penalty()
            points_scored += penalty  # penalty is negative

            # Update score (minimum 0)
            player.score = max(0, player.score + points_scored)

            # Clear floor line
            self.discard_pile.extend(player.floor_line._tiles)
            player.floor_line._tiles.clear()

            print(
                f"Player {player.player_id + 1} scored {points_scored} points (total: {player.score})"
            )

    def on_enter_preparing_next_round(self):
        """Prepare for next round"""
        self.round_number += 1

        # Clear board center (keep special tile if not taken)
        if not self.first_player_token_taken:
            special_tiles = [
                t for t in self.board_center._tiles if t.type == SpecialTileType.TILE_1
            ]
        else:
            special_tiles = [self.tile_generator.create_game_special_tile()]

        self.discard_pile.extend(
            [t for t in self.board_center._tiles if t.type != SpecialTileType.TILE_1]
        )
        self.board_center._tiles.clear()
        self.board_center.extend(special_tiles)

        print(f"Preparing round {self.round_number}")

    def on_enter_game_ended(self):
        """Calculate final scores and determine winner"""
        print("Game ended! Calculating final scores...")

        for player in self.players:
            bonus_points = 0

            # Bonus for complete horizontal lines (2 points each)
            for row in player.wall.grid:
                if all(tile is not None for tile in row):
                    bonus_points += 2

            # Bonus for complete vertical lines (7 points each)
            for col in range(5):
                if all(player.wall.grid[row][col] is not None for row in range(5)):
                    bonus_points += 7

            # Bonus for complete color sets (10 points each)
            for tile_type in TileType:
                type_count = sum(
                    1
                    for row in player.wall.grid
                    for tile in row
                    if tile and tile.type == tile_type
                )
                if type_count == 5:
                    bonus_points += 10

            player.score += bonus_points
            print(
                f"Player {player.player_id + 1}: {player.score} points (bonus: {bonus_points})"
            )

        # Determine winner
        winner = max(self.players, key=lambda p: p.score)
        print(f"Player {winner.player_id + 1} wins with {winner.score} points!")

    # Player action methods
    def player_take_from_factory(
        self, factory_index: int, tile_type: TileType, pattern_line_index: int
    ):
        """Player takes tiles from factory"""
        if not self.current_state == self.factory_offer:
            raise ValueError("Not in factory offer phase")

        tiles = self.take_tiles_from_factory(factory_index, tile_type)
        self.place_tiles_on_player_board(self.current_player, tiles, pattern_line_index)

        self.next_player()

        if not self.check_tiles_available():
            self.complete_factory_phase()

    def player_take_from_center(self, tile_type: TileType, pattern_line_index: int):
        """Player takes tiles from center"""
        if not self.current_state == self.factory_offer:
            raise ValueError("Not in factory offer phase")

        tiles = self.take_tiles_from_center(tile_type)
        self.place_tiles_on_player_board(self.current_player, tiles, pattern_line_index)

        self.next_player()

        if not self.check_tiles_available():
            self.complete_factory_phase()
