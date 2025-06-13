import pytest
from fastapi.testclient import TestClient

from src.backend.main import app
from src.backend.session_manager import SessionManager
from src.azul.data_model import Action, ActionType, TileType
from src.backend.models import ActionRequest, SessionStatus


@pytest.mark.integration
class TestBackendIntegration:
    """Integration tests for the backend API"""
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        client = TestClient(app)
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "azul-game-api"

    def test_session_creation_flow(self):
        """Test complete session creation and action flow"""
        client = TestClient(app)
        
        # Create session
        response = client.post("/sessions", json={"num_players": 2})
        assert response.status_code == 200
        
        data = response.json()
        session_id = data["session_id"]
        assert "game_state" in data
        assert len(data["game_state"]["players"]) == 2
        assert "validActions" in data["game_state"]
        
        # Get session
        response = client.get(f"/sessions/{session_id}")
        assert response.status_code == 200
        
        # Get valid actions
        response = client.get(f"/sessions/{session_id}/actions")
        assert response.status_code == 200
        
        actions_data = response.json()
        assert "valid_actions" in actions_data
        assert len(actions_data["valid_actions"]) > 0
        
        # Execute an action
        first_action = actions_data["valid_actions"][0]
        response = client.post(f"/sessions/{session_id}/actions", json=first_action)
        assert response.status_code == 200
        
        action_response = response.json()
        assert action_response["success"] is True
        assert "game_state" in action_response

    def test_session_abort(self):
        """Test session abort functionality"""
        client = TestClient(app)
        
        # Create session
        response = client.post("/sessions", json={"num_players": 2})
        session_id = response.json()["session_id"]
        
        # Abort session
        response = client.delete(f"/sessions/{session_id}")
        assert response.status_code == 200
        
        abort_data = response.json()
        assert "aborted successfully" in abort_data["message"]


@pytest.mark.unit 
class TestSessionManager:
    """Unit tests for session manager"""
    
    def test_session_creation(self):
        """Test session manager creates sessions correctly"""
        manager = SessionManager()
        
        session_id = manager.create_session(num_players=2)
        assert session_id is not None
        
        metadata = manager.session_metadata[session_id]
        assert metadata.num_players == 2
        assert metadata.status == SessionStatus.ACTIVE
        
        game_state = manager.get_session(session_id)
        assert game_state is not None
        assert len(game_state.players) == 2
        assert len(game_state.valid_actions) > 0

    def test_action_conversion(self):
        """Test action conversion between frontend and backend"""
        frontend_action = ActionRequest(
            type="TAKE_FROM_FACTORY",
            factory_id=0,
            tile_type="blue",
            pattern_line=1
        )
        
        backend_action = frontend_action.to_backend_action()
        
        assert backend_action.type == ActionType.TAKE_FROM_FACTORY
        assert backend_action.factory_id == 0
        assert backend_action.tile_type == TileType.BLUE
        assert backend_action.pattern_line == 1