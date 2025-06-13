import uuid
from typing import Dict, Optional, Tuple, List
from datetime import datetime, timedelta
from uuid import UUID

from ..azul.game import AzulGame, get_valid_actions
from ..azul.game_state import GameState
from ..azul.data_model import Action, ActionType, CompletionStatus, GameMode, Player, PlayerStatus
from .models import SessionMetadata, SessionStatus


class SessionManager:
    """Manages game sessions with in-memory storage"""
    
    def __init__(self) -> None:
        self.sessions: Dict[UUID, AzulGame] = {}
        self.session_metadata: Dict[UUID, SessionMetadata] = {}
    
    def create_session(self, num_players: int = 2, game_mode: GameMode = GameMode.SELFPLAY, player_name: Optional[str] = None) -> Tuple[UUID, Optional[UUID]]:
        """Create a new game session"""
        if num_players < 2 or num_players > 4:
            raise ValueError("Number of players must be between 2 and 4")
        
        session_id = uuid.uuid4()
        
        # Create new game
        game = AzulGame(num_players)
        
        # Set game mode
        game.game_state.game_mode = game_mode
        game.game_state.max_players = num_players
        
        # Handle player creation based on game mode
        player_id: Optional[UUID] = None
        if game.game_state.game_mode == GameMode.PVP:
            # Create first player for PVP mode
            player_id = uuid.uuid4()
            player = Player(
                id=player_id,
                name=player_name or f"Player 1",
                status=PlayerStatus.CONNECTED,
                player_index=0
            )
            game.game_state.session_players.append(player)
        elif game.game_state.game_mode == GameMode.SELFPLAY:
            # For selfplay, create placeholder players
            for i in range(num_players):
                selfplay_id = uuid.uuid4()  # Use proper UUID even for selfplay
                player = Player(
                    id=selfplay_id,
                    name=f"Player {i+1}",
                    status=PlayerStatus.CONNECTED,
                    player_index=i
                )
                game.game_state.session_players.append(player)
        
        # Populate valid actions
        game.game_state.valid_actions = get_valid_actions(game.game_state)
        
        # Store session
        self.sessions[session_id] = game
        self.session_metadata[session_id] = SessionMetadata(
            created_at=datetime.now(),
            last_activity=datetime.now(),
            num_players=num_players,
            status=SessionStatus.ACTIVE
        )
        
        return session_id, player_id
    
    def get_session(self, session_id: UUID) -> Optional[GameState]:
        """Get game state for a session"""
        if session_id not in self.sessions:
            return None
        
        # Update last activity
        self.session_metadata[session_id].last_activity = datetime.now()
        
        # Ensure valid actions are populated
        game = self.sessions[session_id]
        game.game_state.valid_actions = get_valid_actions(game.game_state)
        
        return game.game_state
    
    def execute_action(self, session_id: UUID, action: Action) -> bool:
        """Execute an action in a session"""
        if session_id not in self.sessions:
            return False
        
        game = self.sessions[session_id]
        
        # Handle abort action
        if action.type == ActionType.ABORT_GAME:
            game.game_state.completion = CompletionStatus.ABORTED
            self.session_metadata[session_id].status = SessionStatus.ABORTED
            return True
        
        # Execute game action
        success = game.execute_action(action)
        
        if success:
            # Update last activity
            self.session_metadata[session_id].last_activity = datetime.now()
            
            # Refresh valid actions after successful action
            game.game_state.valid_actions = get_valid_actions(game.game_state)
        
        return success
    
    def abort_session(self, session_id: UUID) -> bool:
        """Abort a session (mark as aborted, don't delete immediately for cleanup)"""
        if session_id not in self.sessions:
            return False
        
        game = self.sessions[session_id]
        game.game_state.completion = CompletionStatus.ABORTED
        self.session_metadata[session_id].status = SessionStatus.ABORTED
        
        return True
    
    def delete_session(self, session_id: UUID) -> bool:
        """Completely remove a session"""
        if session_id not in self.sessions:
            return False
        
        del self.sessions[session_id]
        del self.session_metadata[session_id]
        return True
    
    def list_sessions(self) -> Dict[UUID, SessionMetadata]:
        """List all sessions with metadata"""
        return self.session_metadata.copy()
    
    def cleanup_old_sessions(self, max_age_hours: int = 24) -> int:
        """Clean up old or completed sessions"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        sessions_to_delete: List[UUID] = []
        
        for session_id, metadata in self.session_metadata.items():
            # Delete if old or aborted/completed
            if (metadata.last_activity < cutoff_time or 
                metadata.status in [SessionStatus.ABORTED, SessionStatus.COMPLETED]):
                sessions_to_delete.append(session_id)
        
        for session_id in sessions_to_delete:
            self.delete_session(session_id)
        
        return len(sessions_to_delete)
    
    def get_session_count(self) -> int:
        """Get total number of active sessions"""
        return len(self.sessions)
    
    def is_session_active(self, session_id: UUID) -> bool:
        """Check if a session is active"""
        if session_id not in self.session_metadata:
            return False
        
        return self.session_metadata[session_id].status == SessionStatus.ACTIVE
    
    def join_session(self, session_id: UUID, player_name: Optional[str] = None) -> Tuple[Optional[UUID], Optional[int]]:
        """Join an existing session (for PVP mode)"""
        if session_id not in self.sessions:
            return None, None
        
        game = self.sessions[session_id]
        
        # Only allow joining PVP games
        if game.game_state.game_mode != GameMode.PVP:
            return None, None
        
        # Check if session is full
        if len(game.game_state.session_players) >= game.game_state.max_players:
            return None, None
        
        # Find next available player index
        taken_indices = {p.player_index for p in game.game_state.session_players if p.player_index is not None}
        player_index: Optional[int] = None
        for i in range(game.game_state.max_players):
            if i not in taken_indices:
                player_index = i
                break
        
        if player_index is None:
            return None, None
        
        # Create new player
        player_id = uuid.uuid4()
        player = Player(
            id=player_id,
            name=player_name or f"Player {player_index + 1}",
            status=PlayerStatus.CONNECTED,
            player_index=player_index
        )
        
        game.game_state.session_players.append(player)
        
        # Update last activity
        self.session_metadata[session_id].last_activity = datetime.now()
        
        return player_id, player_index
    
    def leave_session(self, session_id: UUID, player_id: UUID) -> bool:
        """Leave a session (mark player as left)"""
        if session_id not in self.sessions:
            return False
        
        game = self.sessions[session_id]
        
        # Find and update player status
        for player in game.game_state.session_players:
            if player.id == player_id:
                player.status = PlayerStatus.LEFT
                self.session_metadata[session_id].last_activity = datetime.now()
                return True
        
        return False
    
    def get_session_players(self, session_id: UUID) -> Optional[List[Player]]:
        """Get all players in a session"""
        if session_id not in self.sessions:
            return None
        
        return self.sessions[session_id].game_state.session_players