from typing import List
from dataclasses import dataclass, field
from .data_model import GameStateType
from .components import Container, PlayerBoard, Factory, Bag


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

    def __post_init__(self):
        if not self.factories:
            self.factories = [Factory(i) for i in range(5)]  # 5 factories for 2 players
        if not self.players:
            self.players = [PlayerBoard() for _ in range(2)]
