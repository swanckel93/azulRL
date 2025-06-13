from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum

from ..azul.data_model import Action, TileType, ActionType


class SessionStatus(Enum):
    ACTIVE = "active"
    ABORTED = "aborted"
    COMPLETED = "completed"


@dataclass
class SessionMetadata:
    """Metadata for a game session"""
    created_at: datetime
    last_activity: datetime
    num_players: int
    status: SessionStatus = SessionStatus.ACTIVE
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "num_players": self.num_players,
            "status": self.status.value
        }


@dataclass
class CreateSessionRequest:
    """Request to create a new session"""
    num_players: int = 2


@dataclass
class CreateSessionResponse:
    """Response when creating a new session"""
    session_id: str
    game_state: dict
    message: str


@dataclass
class GetSessionResponse:
    """Response when getting a session"""
    session_id: str
    game_state: dict


@dataclass
class ValidActionsResponse:
    """Response when getting valid actions"""
    session_id: str
    valid_actions: list


@dataclass
class ActionRequest:
    """Request to execute an action"""
    type: str
    factory_id: Optional[int] = None
    tile_type: Optional[str] = None
    pattern_line: Optional[int] = None
    
    def to_backend_action(self) -> Action:
        """Convert to backend Action object"""
        # Map frontend ActionType to backend ActionType
        action_type_mapping = {
            "TAKE_FROM_FACTORY": ActionType.TAKE_FROM_FACTORY,
            "TAKE_FROM_CENTER": ActionType.TAKE_FROM_CENTER,
            "ABORT_GAME": ActionType.ABORT_GAME
        }
        
        # Map frontend TileType strings to backend TileType enum
        tile_type = None
        if self.tile_type:
            tile_type = TileType(self.tile_type.lower())
        
        return Action(
            type=action_type_mapping[self.type],
            factory_id=self.factory_id,
            tile_type=tile_type,
            pattern_line=self.pattern_line
        )


@dataclass
class ActionResponse:
    """Response when executing an action"""
    session_id: str
    success: bool
    game_state: dict


@dataclass
class AbortSessionResponse:
    """Response when aborting a session"""
    session_id: str
    message: str


@dataclass
class ErrorResponse:
    """Error response"""
    detail: str


@dataclass
class WebSocketMessage:
    """Base WebSocket message"""
    type: str


@dataclass
class WebSocketActionMessage(WebSocketMessage):
    """WebSocket message for game actions"""
    type: str = "action"
    action: Optional[ActionRequest] = None


@dataclass
class WebSocketAbortMessage(WebSocketMessage):
    """WebSocket message for aborting game"""
    type: str = "abort_game"


@dataclass
class WebSocketStateUpdateMessage(WebSocketMessage):
    """WebSocket message for game state updates"""
    type: str = "game_state_update"
    session_id: str = ""
    game_state: dict = field(default_factory=dict)


@dataclass
class WebSocketGameAbortedMessage(WebSocketMessage):
    """WebSocket message when game is aborted"""
    type: str = "game_aborted"
    session_id: str = ""
    game_state: dict = field(default_factory=dict)


@dataclass
class WebSocketErrorMessage(WebSocketMessage):
    """WebSocket error message"""
    type: str = "error"
    message: str = ""


def action_to_frontend_format(action: Action) -> dict:
    """Convert backend Action object to frontend format"""
    return {
        "type": action.type.name,  # TAKE_FROM_FACTORY, TAKE_FROM_CENTER, etc.
        "factory_id": action.factory_id,
        "tile_type": action.tile_type.value.upper() if action.tile_type else None,
        "pattern_line": action.pattern_line
    }