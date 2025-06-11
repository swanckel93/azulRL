"""
Example usage of the Azul Game State Machine
"""

from azul.game.state_machine import AzulGame
import random


def print_game_state(game: AzulGame):
    """Print current game state"""
    print(f"\n{'='*50}")
    print(f"ROUND {game.round_number} - {game.current_state.name.upper()}")
    print(f"Current Player: {game.current_player + 1}")
    print(f"{'='*50}")

    if game.current_state.name == "factory_offer":
        print("\nFACTORIES:")
        for i, factory in enumerate(game.factories):
            if len(factory) > 0:
                tiles_str = ", ".join([f"{tile.type.name}" for tile in factory._tiles])
                print(f"  Factory {i}: [{tiles_str}]")

        print("\nCENTER:")
        center_tiles = [
            tile for tile in game.board_center._tiles if tile.type.name != "TILE_1"
        ]
        if center_tiles:
            tiles_str = ", ".join([f"{tile.type.name}" for tile in center_tiles])
            print(f"  Center: [{tiles_str}]")
        else:
            print("  Center: [Empty]")

        print(f"  First Player Token Available: {not game.first_player_token_taken}")

    print(f"\nPLAYER BOARDS:")
    for i, player in enumerate(game.players):
        print(f"  Player {i+1} (Score: {player.score}):")

        # Pattern lines
        print("    Pattern Lines:")
        for j, line in enumerate(player.pattern_lines):
            if len(line) > 0:
                tiles_str = ", ".join([f"{tile.type.name}" for tile in line._tiles])
                print(f"      Line {j+1} ({len(line)}/{j+1}): [{tiles_str}]")
            else:
                print(f"      Line {j+1} ({len(line)}/{j+1}): [Empty]")

        # Floor line
        if len(player.floor_line) > 0:
            floor_tiles = ", ".join(
                [f"{tile.type.name}" for tile in player.floor_line._tiles]
            )
            penalty = player.floor_line.calculate_penalty()
            print(f"    Floor Line: [{floor_tiles}] (Penalty: {penalty})")
        else:
            print("    Floor Line: [Empty]")


def simulate_turn(game: AzulGame):
    """Simulate a player turn with random decisions"""
    if game.current_state.name != "Factory offer":
        return

    player_num = game.current_player + 1
    print(f"\n--- Player {player_num}'s Turn ---")

    # Find available moves
    available_moves = []

    # Check factories
    for i, factory in enumerate(game.factories):
        if len(factory) > 0:
            tile_types = set(tile.type for tile in factory._tiles)
            for tile_type in tile_types:
                available_moves.append(("factory", i, tile_type))

    # Check center
    center_tiles = [
        tile for tile in game.board_center._tiles if tile.type.name != "TILE_1"
    ]
    if center_tiles:
        tile_types = set(tile.type for tile in center_tiles)
        for tile_type in tile_types:
            available_moves.append(("center", -1, tile_type))

    if not available_moves:
        print("No moves available!")
        return

    # Choose random move
    move_type, location, tile_type = random.choice(available_moves)

    # Choose pattern line (or floor line = -1)
    pattern_line_options = []
    player = game.players[game.current_player]

    # Check which pattern lines can accept this tile type
    for i in range(5):
        if player.can_place_tile_type_in_pattern_line(i, tile_type):
            pattern_line_options.append(i)

    # Always allow floor line as option
    pattern_line_options.append(-1)

    chosen_line = random.choice(pattern_line_options)

    # Execute move
    try:
        if move_type == "factory":
            print(
                f"Taking {tile_type.name} tiles from Factory {location} to Pattern Line {chosen_line + 1 if chosen_line >= 0 else 'Floor'}"
            )
            game.player_take_from_factory(location, tile_type, chosen_line)
        else:
            print(
                f"Taking {tile_type.name} tiles from Center to Pattern Line {chosen_line + 1 if chosen_line >= 0 else 'Floor'}"
            )
            game.player_take_from_center(tile_type, chosen_line)
    except Exception as e:
        print(f"Error executing move: {e}")


def run_game_simulation():
    """Run a complete game simulation"""
    print("Starting Azul Game Simulation")
    print("=" * 60)

    # Create game with 2 players
    game = AzulGame(num_players=2, seed=42)

    # Start the game
    game.start_game()

    turn_count = 0
    max_turns = 1000  # Safety limit

    while not game.current_state.name == "game_ended" and turn_count < max_turns:
        print_game_state(game)

        if game.current_state.name == "Factory offer":
            simulate_turn(game)
        elif game.current_state.name == "Wall tiling":
            print("\nExecuting wall tiling phase...")
            game.complete_wall_tiling()
        elif game.current_state.name == "Preparing next round":
            print("\nPreparing next round...")
            game.start_next_round()

        turn_count += 1

    print_game_state(game)
    print(f"\nGame completed in {turn_count} turns!")


def interactive_game():
    """Run an interactive game where human can make decisions"""
    print("Starting Interactive Azul Game")
    print("=" * 60)

    num_players = int(input("Enter number of players (2-4): "))
    game = AzulGame(num_players=num_players)
    game.start_game()

    while not game.current_state.name == "game_ended":
        print_game_state(game)

        if game.current_state.name == "factory_offer":
            player_num = game.current_player + 1
            print(f"\nPlayer {player_num}'s Turn")

            # Show available moves
            print("\nAvailable moves:")
            move_options = []

            # Factory moves
            for i, factory in enumerate(game.factories):
                if len(factory) > 0:
                    tile_types = set(tile.type for tile in factory._tiles)
                    for tile_type in tile_types:
                        move_options.append(("factory", i, tile_type))
                        print(
                            f"{len(move_options)}. Take {tile_type.name} from Factory {i}"
                        )

            # Center moves
            center_tiles = [
                tile for tile in game.board_center._tiles if tile.type.name != "TILE_1"
            ]
            if center_tiles:
                tile_types = set(tile.type for tile in center_tiles)
                for tile_type in tile_types:
                    move_options.append(("center", -1, tile_type))
                    print(f"{len(move_options)}. Take {tile_type.name} from Center")

            if not move_options:
                print("No moves available!")
                break

            # Get player choice
            try:
                choice = int(input(f"Choose move (1-{len(move_options)}): ")) - 1
                if choice < 0 or choice >= len(move_options):
                    print("Invalid choice!")
                    continue

                move_type, location, tile_type = move_options[choice]

                # Choose pattern line
                print("\nChoose destination:")
                player = game.players[game.current_player]

                for i in range(5):
                    can_place = player.can_place_tile_type_in_pattern_line(i, tile_type)
                    status = "✓" if can_place else "✗"
                    current_tiles = len(player.pattern_lines[i])
                    print(f"{i+1}. Pattern Line {i+1} ({current_tiles}/{i+1}) {status}")

                print("6. Floor Line (penalty)")

                line_choice = int(input("Choose line (1-6): ")) - 1
                if line_choice == 5:
                    line_choice = -1  # Floor line
                elif line_choice < 0 or line_choice > 4:
                    print("Invalid choice!")
                    continue

                # Execute move
                if move_type == "factory":
                    game.player_take_from_factory(location, tile_type, line_choice)
                else:
                    game.player_take_from_center(tile_type, line_choice)

            except (ValueError, IndexError) as e:
                print(f"Invalid input: {e}")
                continue

        elif game.current_state.name == "wall_tiling":
            input("\nPress Enter to continue to wall tiling phase...")
            game.complete_wall_tiling()

        elif game.current_state.name == "preparing_next_round":
            input("\nPress Enter to prepare next round...")
            game.start_next_round()

    print_game_state(game)
    print("Game Over!")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        interactive_game()
    else:
        run_game_simulation()
