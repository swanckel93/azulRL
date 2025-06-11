from .components import *
from .game_state import GameState
from .data_model import GameStateType, Action, ActionType, TileType


class AzulGame:
    def __init__(self, num_players: int = 2):
        self.game_state = GameState()
        self.game_state.players = [PlayerBoard() for _ in range(num_players)]

        # Adjust number of factories based on player count
        factory_count = {2: 5, 3: 7, 4: 9}[num_players]
        self.game_state.factories = [Factory(i) for i in range(factory_count)]

        self._setup_round()

    def _setup_round(self):
        # Fill factories
        for factory in self.game_state.factories:
            factory.fill_from_bag(self.game_state.bag)

        # Add first player token to center
        if not self.game_state.first_player_token_taken:
            self.game_state.center.add_tile(Tile(TileType.FIRST_PLAYER))

        self.game_state.state = GameStateType.PLAYER_TURN

    def execute_action(self, action: Action) -> bool:
        if self.game_state.state != GameStateType.PLAYER_TURN:
            return False

        player = self.game_state.players[self.game_state.current_player]

        if action.type == ActionType.TAKE_FROM_FACTORY:
            if (
                action.factory_id is None
                or action.tile_type is None
                or action.pattern_line is None
            ):
                return False
            return self._take_from_factory(
                action.factory_id, action.tile_type, action.pattern_line
            )
        elif action.type == ActionType.TAKE_FROM_CENTER:
            if action.tile_type is None or action.pattern_line is None:
                return False
            return self._take_from_center(action.tile_type, action.pattern_line)

        return False

    def _take_from_factory(
        self, factory_id: int, tile_type: TileType, pattern_line: int
    ) -> bool:
        factory = self.game_state.factories[factory_id]
        player = self.game_state.players[self.game_state.current_player]

        if factory.count_by_type(tile_type) == 0:
            return False

        if pattern_line != -1 and not player.can_place_in_pattern_line(
            pattern_line, tile_type
        ):
            return False

        # Take tiles of specified type
        taken_tiles = factory.remove_all_tiles(tile_type)

        # Move remaining tiles to center
        remaining_tiles = factory.clear()
        self.game_state.center.add_tiles(remaining_tiles)

        # Add tiles to player board
        player.add_tiles_to_pattern_line(pattern_line, taken_tiles)

        self._next_turn()
        return True

    def _take_from_center(self, tile_type: TileType, pattern_line: int) -> bool:
        player = self.game_state.players[self.game_state.current_player]

        if self.game_state.center.count_by_type(tile_type) == 0:
            return False

        if pattern_line != -1 and not player.can_place_in_pattern_line(
            pattern_line, tile_type
        ):
            return False

        # Take tiles of specified type
        taken_tiles = self.game_state.center.remove_all_tiles(tile_type)

        # Handle first player token
        if (
            not self.game_state.first_player_token_taken
            and self.game_state.center.count_by_type(TileType.FIRST_PLAYER) > 0
        ):
            self.game_state.center.remove_tile(TileType.FIRST_PLAYER)
            player.floor.append(Tile(TileType.FIRST_PLAYER))
            self.game_state.first_player_token_taken = True
            self.game_state.current_player = 0  # This player goes first next round

        # Add tiles to player board
        player.add_tiles_to_pattern_line(pattern_line, taken_tiles)

        self._next_turn()
        return True

    def _next_turn(self):
        # Check if round is over
        if self._is_round_over():
            self._end_round()
        else:
            self.game_state.current_player = (self.game_state.current_player + 1) % len(
                self.game_state.players
            )

    def _is_round_over(self) -> bool:
        # Round over when all factories and center are empty
        return (
            all(factory.is_empty() for factory in self.game_state.factories)
            and self.game_state.center.is_empty()
        )

    def _end_round(self):
        # Move completed pattern lines to wall and score
        for player in self.game_state.players:
            discarded = player.move_completed_lines_to_wall()
            self.game_state.discard_pile.add_tiles(discarded)

            # Calculate score
            round_score = player.calculate_round_score()
            player.score = max(0, player.score + round_score)

            # Clear floor
            floor_tiles = player.clear_floor()
            # Remove first player token, add rest to discard
            floor_tiles = [
                tile for tile in floor_tiles if tile.type != TileType.FIRST_PLAYER
            ]
            self.game_state.discard_pile.add_tiles(floor_tiles)

        # Check for game end
        if any(player.has_complete_row() for player in self.game_state.players):
            self.game_state.state = GameStateType.GAME_END
        else:
            # Setup next round
            self.game_state.round_number += 1
            self.game_state.first_player_token_taken = False

            # Refill bag if needed
            if self.game_state.bag.is_empty():
                discarded_tiles = self.game_state.discard_pile.clear()
                self.game_state.bag.add_tiles(discarded_tiles)
                random.shuffle(self.game_state.bag.tiles)

            self._setup_round()


def get_valid_actions(game_state: GameState) -> List[Action]:
    """Returns list of all valid actions for current player given game state"""
    if game_state.state != GameStateType.PLAYER_TURN:
        return []

    actions = []
    player = game_state.players[game_state.current_player]

    # Actions from factories
    for factory in game_state.factories:
        if not factory.is_empty():
            unique_types = factory.get_unique_types()
            for tile_type in unique_types:
                if tile_type != TileType.FIRST_PLAYER:
                    # Try each pattern line
                    for line_idx in range(5):
                        if player.can_place_in_pattern_line(line_idx, tile_type):
                            actions.append(
                                Action(
                                    type=ActionType.TAKE_FROM_FACTORY,
                                    factory_id=factory.id,
                                    tile_type=tile_type,
                                    pattern_line=line_idx,
                                )
                            )

                    # Floor line is always valid
                    actions.append(
                        Action(
                            type=ActionType.TAKE_FROM_FACTORY,
                            factory_id=factory.id,
                            tile_type=tile_type,
                            pattern_line=-1,
                        )
                    )

    # Actions from center
    if not game_state.center.is_empty():
        unique_types = game_state.center.get_unique_types()
        for tile_type in unique_types:
            if tile_type != TileType.FIRST_PLAYER:
                # Try each pattern line
                for line_idx in range(5):
                    if player.can_place_in_pattern_line(line_idx, tile_type):
                        actions.append(
                            Action(
                                type=ActionType.TAKE_FROM_CENTER,
                                tile_type=tile_type,
                                pattern_line=line_idx,
                            )
                        )

                # Floor line is always valid
                actions.append(
                    Action(
                        type=ActionType.TAKE_FROM_CENTER,
                        tile_type=tile_type,
                        pattern_line=-1,
                    )
                )

    return actions
