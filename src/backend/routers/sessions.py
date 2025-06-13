from fastapi import APIRouter, HTTPException

from ..session_manager import SessionManager
from ..models import (
    CreateSessionRequest, CreateSessionResponse, GetSessionResponse,
    ValidActionsResponse, ActionRequest, ActionResponse, AbortSessionResponse,
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
        session_id = session_manager.create_session(request.num_players)
        game_state = session_manager.get_session(session_id)
        
        if not game_state:
            raise HTTPException(status_code=500, detail="Failed to retrieve created session")
        
        return CreateSessionResponse(
            session_id=session_id,
            game_state=game_state.to_dict(),
            message=f"Session created with {request.num_players} players"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")


@router.get("/{session_id}", response_model=GetSessionResponse)
async def get_session(session_id: str):
    """Get current game state for a session"""
    game_state = session_manager.get_session(session_id)
    if not game_state:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return GetSessionResponse(
        session_id=session_id,
        game_state=game_state.to_dict()
    )


@router.get("/{session_id}/actions", response_model=ValidActionsResponse)
async def get_valid_actions(session_id: str):
    """Get valid actions for current player in session"""
    game_state = session_manager.get_session(session_id)
    if not game_state:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return ValidActionsResponse(
        session_id=session_id,
        valid_actions=[action_to_frontend_format(action) for action in game_state.valid_actions]
    )


@router.post("/{session_id}/actions", response_model=ActionResponse)
async def execute_action(session_id: str, action: ActionRequest):
    """Execute an action in a session"""
    try:
        # Convert frontend action format to backend format
        action_obj = action.to_backend_action()
        
        # Execute action
        success = session_manager.execute_action(session_id, action_obj)
        
        if not success:
            raise HTTPException(status_code=400, detail="Invalid action")
        
        # Get updated game state
        game_state = session_manager.get_session(session_id)
        
        if not game_state:
            raise HTTPException(status_code=404, detail="Session not found after action")
        
        return ActionResponse(
            session_id=session_id,
            success=True,
            game_state=game_state.to_dict()
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Action execution failed: {str(e)}")


@router.delete("/{session_id}", response_model=AbortSessionResponse)
async def abort_session(session_id: str):
    """Abort/delete a game session"""
    success = session_manager.abort_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return AbortSessionResponse(
        session_id=session_id,
        message="Session aborted successfully"
    )