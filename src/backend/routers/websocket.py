from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List
import json
from dataclasses import asdict

from ..models import (
    ActionRequest, WebSocketStateUpdateMessage, WebSocketGameAbortedMessage,
    WebSocketErrorMessage
)

router = APIRouter(tags=["websocket"])


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        self.active_connections[session_id].append(websocket)

    def disconnect(self, websocket: WebSocket, session_id: str):
        if session_id in self.active_connections:
            if websocket in self.active_connections[session_id]:
                self.active_connections[session_id].remove(websocket)
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]

    async def broadcast_to_session(self, session_id: str, message: dict):
        if session_id in self.active_connections:
            for connection in self.active_connections[session_id][:]:  # Copy list to avoid modification during iteration
                try:
                    await connection.send_text(json.dumps(message))
                except:
                    # Remove broken connections
                    self.active_connections[session_id].remove(connection)


manager = ConnectionManager()


@router.websocket("/sessions/{session_id}/ws")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time game updates"""
    # Import here to avoid circular imports
    from ..routers.sessions import session_manager
    
    # Check if session exists
    game_state = session_manager.get_session(session_id)
    if not game_state:
        await websocket.close(code=4004)
        return

    await manager.connect(websocket, session_id)
    
    try:
        # Send current game state immediately upon connection
        initial_message = WebSocketStateUpdateMessage(
            session_id=session_id,
            game_state=game_state.to_dict()
        )
        await websocket.send_text(json.dumps(asdict(initial_message)))
        
        while True:
            # Wait for messages from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "action":
                # Execute action via session manager
                action_data = message.get("action")
                action_request = ActionRequest(**action_data)
                action_obj = action_request.to_backend_action()
                
                success = session_manager.execute_action(session_id, action_obj)
                
                if success:
                    # Broadcast updated game state to all connected clients
                    updated_game_state = session_manager.get_session(session_id)
                    if updated_game_state:
                        update_message = WebSocketStateUpdateMessage(
                            session_id=session_id,
                            game_state=updated_game_state.to_dict()
                        )
                        await manager.broadcast_to_session(session_id, asdict(update_message))
                else:
                    # Send error back to client
                    error_message = WebSocketErrorMessage(message="Invalid action")
                    await websocket.send_text(json.dumps(asdict(error_message)))
            
            elif message.get("type") == "abort_game":
                # Handle abort game request
                success = session_manager.abort_session(session_id)
                if success:
                    # Broadcast game aborted to all connected clients
                    updated_game_state = session_manager.get_session(session_id)
                    if updated_game_state:
                        abort_message = WebSocketGameAbortedMessage(
                            session_id=session_id,
                            game_state=updated_game_state.to_dict()
                        )
                        await manager.broadcast_to_session(session_id, asdict(abort_message))
                else:
                    error_message = WebSocketErrorMessage(message="Failed to abort game")
                    await websocket.send_text(json.dumps(asdict(error_message)))
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id)