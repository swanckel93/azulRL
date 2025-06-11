import json
from dataclasses import dataclass, field, asdict
from typing import List, Optional

from .data_model import GameStateType, CompletionStatus
from .components import Bag, Container, Factory, PlayerBoard


@dataclass
class GameState:
    state: GameStateType = GameStateType.SETUP
    current_player: int = 0
    round_number: int = 1
    bag: Bag = field(default_factory=Bag)
    factories: List[Factory] = field(default_factory=list)
    center: Container = field(default_factory=Container)
    discard_pile: Container = field(default_factory=Container)
    players: List[PlayerBoard] = field(default_factory=list)
    first_player_token_taken: bool = False
    completion: CompletionStatus = CompletionStatus.NOT_COMPLETED
    winner: int = -1

    def __post_init__(self):
        if not self.factories:
            self.factories = [Factory(i) for i in range(5)]  # 5 factories for 2 players
        if not self.players:
            self.players = [PlayerBoard() for _ in range(2)]

    def to_json(self, indent: Optional[int] = None) -> str:
        """
        Convert the GameState to JSON string.

        Args:
            indent: Number of spaces for indentation (None for compact JSON)

        Returns:
            JSON string representation of the game state
        """
        return json.dumps(self.to_dict(), indent=indent, default=self._json_serializer)

    def to_dict(self) -> dict:
        """
        Convert the GameState to a dictionary.

        Returns:
            Dictionary representation of the game state
        """
        # Use dataclass asdict but handle special cases
        game_dict = asdict(self)

        # Convert enum to its value
        if hasattr(self.state, "value"):
            game_dict["state"] = self.state.value

        return game_dict

    @staticmethod
    def _json_serializer(obj):
        """
        Custom JSON serializer for objects that aren't JSON serializable by default.
        """
        # Handle enums
        if hasattr(obj, "value"):
            return obj.value

        # Handle other custom objects by converting to dict if they have asdict support
        if hasattr(obj, "__dict__"):
            return obj.__dict__

        # For objects that can't be serialized, return their string representation
        return str(obj)

    def save_to_file(self, filename: str, indent: int = 2) -> None:
        """
        Save the game state to a JSON file.

        Args:
            filename: Path to the output JSON file
            indent: Number of spaces for indentation
        """
        with open(filename, "w") as f:
            f.write(self.to_json(indent=indent))

    @classmethod
    def from_json(cls, json_str: str) -> "GameState":
        """
        Create a GameState from JSON string.

        Args:
            json_str: JSON string representation

        Returns:
            GameState instance
        """
        data = json.loads(json_str)
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: dict) -> "GameState":
        """
        Create a GameState from dictionary.

        Args:
            data: Dictionary representation

        Returns:
            GameState instance
        """
        # Convert state back to enum if needed
        if "state" in data:
            if isinstance(data["state"], str):
                # Handle string representation of enum
                for state_type in GameStateType:
                    if str(state_type.value) == data["state"]:
                        data["state"] = state_type
                        break
            elif isinstance(data["state"], int):
                # Handle integer representation of enum
                data["state"] = GameStateType(data["state"])

        # Handle reconstruction of nested objects
        # You'll need to implement similar logic for Bag, Factory, Container, PlayerBoard
        # based on their structure

        return cls(**data)

    @classmethod
    def load_from_file(cls, filename: str) -> "GameState":
        """
        Load a GameState from a JSON file.

        Args:
            filename: Path to the JSON file

        Returns:
            GameState instance
        """
        with open(filename, "r") as f:
            return cls.from_json(f.read())


# Example usage:
if __name__ == "__main__":
    # Create a game state
    game = GameState()

    # Convert to JSON
    json_output = game.to_json(indent=2)
    print("Game State JSON:")
    print(json_output)

    # Save to file
    game.save_to_file("game_state.json")

    # Load from file
    loaded_game = GameState.load_from_file("game_state.json")
    print("\nLoaded game state current player:", loaded_game.current_player)
