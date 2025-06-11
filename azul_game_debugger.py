"""
Azul Game Debugger - Enhanced version with detailed logging
"""

from azul.game.state_machine import AzulGame
import random


def debug_game_state(game: AzulGame):
    """Print detailed game state for debugging"""
    print(f"\n{'='*60}")
    print(f"DEBUG: ROUND {game.round_number} - {game.current_state.name.upper()}")
    print(f"Current Player: {game.current_player + 1}")
    print(f"Starting Player: {game.starting_player + 1}")
    print(f"First Player Token Taken: {game.first_player_token_taken}")
    print(f"{'='*60}")

    # Debug bag state
    print(f"\nBAG STATE:")
    print(f"  Tiles in bag: {len(game.bag) if game.bag else 0}")
    print(f"  Tiles in discard: {len(game.discard_pile)}")

    if game.current_state.name == "factory_offer":
        print(f"\nFACTORIES STATE:")
        total_factory_tiles = 0
        for i, factory in enumerate(game.factories):
            factory_tiles = (
                len(factory._tiles) if hasattr(factory, "_tiles") else len(factory)
            )
            total_factory_tiles += factory_tiles
            if factory_tiles > 0:
                if hasattr(factory, "_tiles"):
                    tiles_str = ", ".join(
                        [f"{tile.type.name}" for tile in factory._tiles]
                    )
                else:
                    # Handle different factory implementation
                    tiles_str = ", ".join([f"{tile.type.name}" for tile in factory])
                print(f"  Factory {i}: [{tiles_str}] ({factory_tiles} tiles)")
            else:
                print(f"  Factory {i}: [Empty]")

        print(f"  Total tiles in factories: {total_factory_tiles}")

        print(f"\nCENTER STATE:")
        center_tiles = []
        special_tiles = []
        if hasattr(game.board_center, "_tiles"):
            for tile in game.board_center._tiles:
                if tile.type.name == "TILE_1":
                    special_tiles.append(tile)
                else:
                    center_tiles.append(tile)

        print(f"  Regular tiles: {len(center_tiles)}")
        print(f"  Special tiles: {len(special_tiles)}")

        if center_tiles:
            tiles_str = ", ".join([f"{tile.type.name}" for tile in center_tiles])
            print(f"  Center regular: [{tiles_str}]")
        if special_tiles:
            print(f"  Center special: [TILE_1 x{len(special_tiles)}]")

        # Check if tiles are available
        tiles_available = game.check_tiles_available()
        print(f"  Tiles available for selection: {tiles_available}")

    print(f"\nPLAYER BOARDS:")
    for i, player in enumerate(game.players):
        print(f"  Player {i+1} (Score: {player.score}):")

        # Pattern lines
        print("    Pattern Lines:")
        for j, line in enumerate(player.pattern_lines):
            line_length = len(line._tiles) if hasattr(line, "_tiles") else len(line)
            if line_length > 0:
                if hasattr(line, "_tiles"):
                    tiles_str = ", ".join([f"{tile.type.name}" for tile in line._tiles])
                else:
                    tiles_str = ", ".join([f"{tile.type.name}" for tile in line])

                # Check if complete
                is_complete = line_length == (j + 1)
                complete_str = " [COMPLETE]" if is_complete else ""
                print(
                    f"      Line {j+1} ({line_length}/{j+1}): [{tiles_str}]{complete_str}"
                )
            else:
                print(f"      Line {j+1} ({line_length}/{j+1}): [Empty]")

        # Wall state
        print("    Wall:")
        wall_tiles = 0
        for row_idx, row in enumerate(player.wall.grid):
            row_tiles = [tile.type.name if tile else "Empty" for tile in row]
            wall_tiles += sum(1 for tile in row if tile is not None)
            print(f"      Row {row_idx+1}: [{', '.join(row_tiles)}]")
        print(f"    Total wall tiles: {wall_tiles}")

        # Floor line
        floor_length = (
            len(player.floor_line._tiles)
            if hasattr(player.floor_line, "_tiles")
            else len(player.floor_line)
        )
        if floor_length > 0:
            if hasattr(player.floor_line, "_tiles"):
                floor_tiles = ", ".join(
                    [f"{tile.type.name}" for tile in player.floor_line._tiles]
                )
            else:
                floor_tiles = ", ".join(
                    [f"{tile.type.name}" for tile in player.floor_line]
                )
            penalty = player.floor_line.calculate_penalty()
            print(f"    Floor Line: [{floor_tiles}] (Penalty: {penalty})")
        else:
            print("    Floor Line: [Empty]")


def debug_simulate_turn(game: AzulGame):
    """Simulate a player turn with detailed debugging"""
    if game.current_state.name != "factory_offer":
        print(
            f"DEBUG: Not in factory_offer state, current state: {game.current_state.name}"
        )
        return

    player_num = game.current_player + 1
    print(f"\n--- DEBUG: Player {player_num}'s Turn ---")

    # Find available moves
    available_moves = []

    # Check factories
    print("DEBUG: Checking factories for moves...")
    for i, factory in enumerate(game.factories):
        factory_length = (
            len(factory._tiles) if hasattr(factory, "_tiles") else len(factory)
        )
        if factory_length > 0:
            if hasattr(factory, "_tiles"):
                tile_types = set(tile.type for tile in factory._tiles)
            else:
                tile_types = set(tile.type for tile in factory)

            print(
                f"  Factory {i}: {factory_length} tiles, types: {[t.name for t in tile_types]}"
            )
            for tile_type in tile_types:
                available_moves.append(("factory", i, tile_type))

    # Check center
    print("DEBUG: Checking center for moves...")
    center_tiles = []
    if hasattr(game.board_center, "_tiles"):
        center_tiles = [
            tile for tile in game.board_center._tiles if tile.type.name != "TILE_1"
        ]

    if center_tiles:
        tile_types = set(tile.type for tile in center_tiles)
        print(
            f"  Center: {len(center_tiles)} tiles, types: {[t.name for t in tile_types]}"
        )
        for tile_type in tile_types:
            available_moves.append(("center", -1, tile_type))
    else:
        print("  Center: No regular tiles available")

    print(f"DEBUG: Total available moves: {len(available_moves)}")

    if not available_moves:
        print("DEBUG: No moves available! Checking why...")
        tiles_available = game.check_tiles_available()
        print(f"DEBUG: game.check_tiles_available() returns: {tiles_available}")
        return

    # Choose random move
    move_type, location, tile_type = random.choice(available_moves)
    print(f"DEBUG: Chosen move: {move_type} {location} {tile_type.name}")

    # Choose pattern line (or floor line = -1)
    pattern_line_options = []
    player = game.players[game.current_player]

    # Check which pattern lines can accept this tile type
    print("DEBUG: Checking pattern line options...")
    for i in range(5):
        can_place = player.can_place_tile_type_in_pattern_line(i, tile_type)
        line_length = (
            len(player.pattern_lines[i]._tiles)
            if hasattr(player.pattern_lines[i], "_tiles")
            else len(player.pattern_lines[i])
        )
        print(
            f"  Line {i+1}: can_place={can_place}, current_length={line_length}/{i+1}"
        )
        if can_place:
            pattern_line_options.append(i)

    # Always allow floor line as option
    pattern_line_options.append(-1)
    print(
        f"DEBUG: Pattern line options: {[i+1 if i >= 0 else 'Floor' for i in pattern_line_options]}"
    )

    chosen_line = random.choice(pattern_line_options)

    # Execute move
    try:
        if move_type == "factory":
            print(
                f"DEBUG: Taking {tile_type.name} tiles from Factory {location} to Pattern Line {chosen_line + 1 if chosen_line >= 0 else 'Floor'}"
            )
            game.player_take_from_factory(location, tile_type, chosen_line)
        else:
            print(
                f"DEBUG: Taking {tile_type.name} tiles from Center to Pattern Line {chosen_line + 1 if chosen_line >= 0 else 'Floor'}"
            )
            game.player_take_from_center(tile_type, chosen_line)

        print("DEBUG: Move executed successfully")

    except Exception as e:
        print(f"DEBUG: Error executing move: {e}")
        import traceback

        traceback.print_exc()


def run_debug_simulation():
    """Run a game simulation with detailed debugging"""
    print("Starting Azul Game DEBUG Simulation")
    print("=" * 80)

    # Create game with 2 players
    game = AzulGame(num_players=2, seed=42)

    # Start the game
    print("DEBUG: Starting game...")
    game.start_game()
    print(f"DEBUG: Game started, initial state: {game.current_state.name}")

    turn_count = 0
    max_turns = 50  # Reduced for debugging

    while not game.current_state.name == "game_ended" and turn_count < max_turns:
        debug_game_state(game)

        if game.current_state.name == "factory_offer":
            debug_simulate_turn(game)
        elif game.current_state.name == "wall_tiling":
            print("\nDEBUG: Executing wall tiling phase...")
            game.complete_wall_tiling()
            print(f"DEBUG: After wall tiling, state: {game.current_state.name}")
        elif game.current_state.name == "preparing_next_round":
            print("\nDEBUG: Preparing next round...")
            game.start_next_round()
            print(
                f"DEBUG: After preparing next round, state: {game.current_state.name}"
            )

        turn_count += 1
        print(f"\nDEBUG: Completed turn {turn_count}")

    debug_game_state(game)
    print(f"\nDEBUG: Simulation ended after {turn_count} turns!")
    print(f"DEBUG: Final state: {game.current_state.name}")

    if turn_count >= max_turns:
        print("DEBUG: Simulation stopped due to max turns limit")


if __name__ == "__main__":
    run_debug_simulation()
