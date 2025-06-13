import uuid
from typing import Dict, Optional
from datetime import datetime, timedelta

from ..azul.game import AzulGame, get_valid_actions
from ..azul.game_state import GameState
from ..azul.data_model import Action, ActionType, CompletionStatus
from .models import SessionMetadata, SessionStatus


class SessionManager:
    """Manages game sessions with in-memory storage"""
    
    def __init__(self):
        self.sessions: Dict[str, AzulGame] = {}
        self.session_metadata: Dict[str, SessionMetadata] = {}
    
    def create_session(self, num_players: int = 2) -> str:
        """Create a new game session"""
        if num_players < 2 or num_players > 4:
            raise ValueError("Number of players must be between 2 and 4")
        
        session_id = str(uuid.uuid4())
        
        # Create new game
        game = AzulGame(num_players)
        
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
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[GameState]:
        """Get game state for a session"""
        if session_id not in self.sessions:
            return None
        
        # Update last activity
        self.session_metadata[session_id].last_activity = datetime.now()
        
        # Ensure valid actions are populated
        game = self.sessions[session_id]
        game.game_state.valid_actions = get_valid_actions(game.game_state)
        
        return game.game_state
    
    def execute_action(self, session_id: str, action: Action) -> bool:
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
    
    def abort_session(self, session_id: str) -> bool:
        """Abort a session (mark as aborted, don't delete immediately for cleanup)"""
        if session_id not in self.sessions:
            return False
        
        game = self.sessions[session_id]
        game.game_state.completion = CompletionStatus.ABORTED
        self.session_metadata[session_id].status = SessionStatus.ABORTED
        
        return True
    
    def delete_session(self, session_id: str) -> bool:
        """Completely remove a session"""
        if session_id not in self.sessions:
            return False
        
        del self.sessions[session_id]
        del self.session_metadata[session_id]
        return True
    
    def list_sessions(self) -> Dict[str, SessionMetadata]:
        """List all sessions with metadata"""
        return self.session_metadata.copy()
    
    def cleanup_old_sessions(self, max_age_hours: int = 24):
        """Clean up old or completed sessions"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        sessions_to_delete = []
        
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
    
    def is_session_active(self, session_id: str) -> bool:
        """Check if a session is active"""
        if session_id not in self.session_metadata:
            return False
        
        return self.session_metadata[session_id].status == SessionStatus.ACTIVE