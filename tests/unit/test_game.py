import pytest
from unittest.mock import patch
from azul.data_model import TileType, ActionType, Action, GameStateType
from azul.components import Tile
from azul.game import AzulGame


@pytest.mark.integration
class TestAzulGame:
    @pytest.fixture
    def game(self):
        return AzulGame(num_players=2)

    def test_game_initialization(self, game):
        assert len(game.game_state.players) == 2
        assert len(game.game_state.factories) == 5  # 5 factories for 2 players
        assert game.game_state.current_player == 0
        assert game.game_state.round_number == 1
        assert game.game_state.state == GameStateType.PLAYER_TURN

    def test_game_initialization_different_player_counts(self):
        game_3p = AzulGame(num_players=3)
        assert len(game_3p.game_state.factories) == 7

        game_4p = AzulGame(num_players=4)
        assert len(game_4p.game_state.factories) == 9

    def test_factories_filled_on_setup(self, game):
        # Each factory should have 4 tiles (or fewer if bag runs out)
        for factory in game.game_state.factories:
            assert len(factory.tiles) <= 4
            if not game.game_state.bag.is_empty():
                assert len(factory.tiles) == 4

    def test_first_player_token_in_center(self, game):
        # First player token should be in center at start
        assert game.game_state.center.count_by_type(TileType.FIRST_PLAYER) == 1

    def test_execute_invalid_action_wrong_state(self, game):
        game.game_state.state = GameStateType.GAME_END
        action = Action(type=ActionType.TAKE_FROM_CENTER)

        result = game.execute_action(action)

        assert not result

    def test_execute_invalid_action_missing_fields(self, game):
        action = Action(type=ActionType.TAKE_FROM_FACTORY)  # Missing required fields

        result = game.execute_action(action)

        assert not result

    def test_take_from_factory(self, game, deterministic_shuffle):
        # Setup a factory with known tiles
        factory = game.game_state.factories[0]
        factory.tiles = [Tile(TileType.BLUE), Tile(TileType.BLUE), Tile(TileType.RED)]

        action = Action(
            type=ActionType.TAKE_FROM_FACTORY,
            factory_id=0,
            tile_type=TileType.BLUE,
            pattern_line=0,
        )

        result = game.execute_action(action)

        assert result
        # Player should have blue tiles in pattern line 0
        player = game.game_state.players[0]
        assert (
            len(player.pattern_lines[0].tiles) == 1
        )  # Capacity 1, so only 1 tile fits
        # Remaining tiles should go to center
        assert game.game_state.center.count_by_type(TileType.RED) == 1

    def test_take_from_center_with_first_player_token(self, game):
        # Add tiles to center
        game.game_state.center.add_tiles([Tile(TileType.BLUE), Tile(TileType.BLUE)])

        action = Action(
            type=ActionType.TAKE_FROM_CENTER,
            tile_type=TileType.BLUE,
            pattern_line=1,  # Second pattern line (capacity 2)
        )

        result = game.execute_action(action)

        assert result
        # Player should have blue tiles
        player = game.game_state.players[0]
        assert len(player.pattern_lines[1].tiles) == 2
        # Player should have first player token on floor
        assert len([t for t in player.floor if t.type == TileType.FIRST_PLAYER]) == 1
        # First player token should be taken
        assert game.game_state.first_player_token_taken
