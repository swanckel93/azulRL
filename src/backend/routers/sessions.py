from fastapi import APIRouter, HTTPException
from uuid import UUID

from ..session_manager import SessionManager
from ..models import (
    CreateSessionRequest, CreateSessionResponse, GetSessionResponse,
    ValidActionsResponse, ActionRequest, ActionResponse, AbortSessionResponse,
    JoinSessionRequest, JoinSessionResponse, LeaveSessionResponse,
    action_to_frontend_format
)

router = APIRouter(
    prefix="/sessions",
    tags=["sessions"]
)

# Initialize session manager
session_manager = SessionManager()


@router.post("", response_model=CreateSessionResponse)
async def create_session(request: CreateSessionRequest = CreateSessionRequest()):
    """Create a new game session"""
    try:
        session_id, player_id = session_manager.create_session(
            request.num_players, 
            request.get_game_mode(), 
            request.player_name
        )
        game_state = session_manager.get_session(session_id)
        
        if not game_state:
            raise HTTPException(status_code=500, detail="Failed to retrieve created session")
        
        return CreateSessionResponse(
            session_id=str(session_id),
            game_state=game_state.to_dict(),
            message=f"Session created with {request.num_players} players in {request.game_mode} mode",
            player_id=str(player_id) if player_id else None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")


@router.get("/{session_id}", response_model=GetSessionResponse)
async def get_session(session_id: str):
    """Get current game state for a session"""
    try:
        session_uuid = UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")
    
    game_state = session_manager.get_session(session_uuid)
    if not game_state:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return GetSessionResponse(
        session_id=str(session_uuid),
        game_state=game_state.to_dict()
    )


@router.get("/{session_id}/actions", response_model=ValidActionsResponse)
async def get_valid_actions(session_id: str):
    """Get valid actions for current player in session"""
    try:
        session_uuid = UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")
    
    game_state = session_manager.get_session(session_uuid)
    if not game_state:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return ValidActionsResponse(
        session_id=str(session_uuid),
        valid_actions=[action_to_frontend_format(action) for action in game_state.valid_actions]
    )


@router.post("/{session_id}/actions", response_model=ActionResponse)
async def execute_action(session_id: str, action: ActionRequest):
    """Execute an action in a session"""
    try:
        session_uuid = UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")
    
    try:
        # Convert frontend action format to backend format
        action_obj = action.to_backend_action()
        
        # Execute action
        success = session_manager.execute_action(session_uuid, action_obj)
        
        if not success:
            raise HTTPException(status_code=400, detail="Invalid action")
        
        # Get updated game state
        game_state = session_manager.get_session(session_uuid)
        
        if not game_state:
            raise HTTPException(status_code=404, detail="Session not found after action")
        
        return ActionResponse(
            session_id=str(session_uuid),
            success=True,
            game_state=game_state.to_dict()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Action execution failed: {str(e)}")


@router.delete("/{session_id}", response_model=AbortSessionResponse)
async def abort_session(session_id: str):
    """Abort/delete a game session"""
    try:
        session_uuid = UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")
    
    success = session_manager.abort_session(session_uuid)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return AbortSessionResponse(
        session_id=str(session_uuid),
        message="Session aborted successfully"
    )


@router.post("/{session_id}/join", response_model=JoinSessionResponse)
async def join_session(session_id: str, request: JoinSessionRequest = JoinSessionRequest()):
    """Join an existing session (PVP mode)"""
    try:
        session_uuid = UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")
    
    try:
        player_id, player_index = session_manager.join_session(session_uuid, request.player_name)
        
        if player_id is None:
            raise HTTPException(status_code=400, detail="Cannot join session (full, wrong mode, or not found)")
        
        game_state = session_manager.get_session(session_uuid)
        if not game_state:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return JoinSessionResponse(
            session_id=str(session_uuid),
            player_id=str(player_id),
            player_index=player_index,
            game_state=game_state.to_dict(),
            message=f"Successfully joined session as Player {player_index + 1}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to join session: {str(e)}")


@router.post("/{session_id}/leave/{player_id}", response_model=LeaveSessionResponse)
async def leave_session(session_id: str, player_id: str):
    """Leave a session"""
    try:
        session_uuid = UUID(session_id)
        player_uuid = UUID(player_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID or player ID format")
    
    success = session_manager.leave_session(session_uuid, player_uuid)
    if not success:
        raise HTTPException(status_code=404, detail="Session or player not found")
    
    return LeaveSessionResponse(
        session_id=str(session_uuid),
        message="Successfully left session"
    )