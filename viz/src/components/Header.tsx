import { useNavigate } from "react-router-dom";
import useStore from "../stores/GameStore";
import { GameStateType } from "../types/GameState";
import "./Header.css";

export function Header() {
    const navigate = useNavigate();
    const gameState = useStore(state => state.gameState);
    const partialAction = useStore(state => state.partialAction);
    const sessionId = useStore(state => state.sessionId);
    const isLoading = useStore(state => state.isLoading);
    const error = useStore(state => state.error);
    const startNewGame = useStore(state => state.startNewGame);
    const abortGame = useStore(state => state.abortGame);
    const executeAction = useStore(state => state.executeAction);
    const isActionComplete = useStore(state => state.isActionComplete);
    
    const getStateDisplayName = (state: GameStateType): string => {
        if (!sessionId) {
            return "No active game";
        }
        
        switch (state) {
            case GameStateType.SETUP:
                return "Setting up game";
            case GameStateType.FACTORY_FILLING:
                return "Filling factories";
            case GameStateType.PLAYER_TURN:
                return "Player turn";
            case GameStateType.ROUND_END:
                return "Round ending";
            case GameStateType.GAME_END:
                return "Game finished";
            default:
                return "Unknown state";
        }
    };

    const handleStartNewGame = async () => {
        try {
            const sessionId = await startNewGame(2); // Default to 2 players
            navigate(`/game/${sessionId}`);
        } catch (error) {
            console.error('Failed to start new game:', error);
        }
    };

    const handleAbortGame = async () => {
        try {
            await abortGame();
            navigate('/');
        } catch (error) {
            console.error('Failed to abort game:', error);
        }
    };

    const handleExecuteAction = async () => {
        await executeAction();
    };

    return (
        <header className="game-header">
            <div className="game-info">
                <h1>Azul Game</h1>
                <div className="game-state">
                    <span className="state-label">Status:</span>
                    <span className="state-value">{getStateDisplayName(gameState.state)}</span>
                </div>
                {sessionId && (
                    <div className="round-info">
                        <span className="round-label">Round:</span>
                        <span className="round-value">{gameState.round_number}</span>
                    </div>
                )}
                {sessionId && gameState.players?.length > 0 && (
                    <div className="player-info">
                        <span className="player-label">Current Player:</span>
                        <span className="player-value">Player {gameState.current_player + 1}</span>
                    </div>
                )}
                {sessionId && (
                    <div className="bag-info">
                        <span className="bag-icon">🎒</span>
                        <span className="bag-label">Bag:</span>
                        <span className="bag-value">{gameState.bag?.tiles?.length || 0}</span>
                    </div>
                )}
                {sessionId && (
                    <div className="discard-info">
                        <span className="discard-icon">🗑️</span>
                        <span className="discard-label">Discard:</span>
                        <span className="discard-value">{gameState.discard_pile?.tiles?.length || 0}</span>
                    </div>
                )}
                {gameState.first_player_token_taken && (
                    <div className="first-player-token">
                        <span>🎯 First Player Token Taken</span>
                    </div>
                )}
                {partialAction && Object.keys(partialAction).length > 0 && (
                    <div className="action-preview">
                        <div className="action-preview-title">Current Action</div>
                        <div className="action-preview-description">
                            {[
                                partialAction.tileType && `Tile: ${partialAction.tileType}`,
                                partialAction.factoryId !== undefined && `From: ${partialAction.factoryId === -1 ? 'Center' : `Factory ${partialAction.factoryId + 1}`}`,
                                partialAction.patternLine !== undefined && `To: Pattern Line ${partialAction.patternLine + 1}`
                            ].filter(Boolean).join(' | ')}
                        </div>
                    </div>
                )}
                
                {/* Game Controls */}
                <div className="game-controls">
                    <button 
                        className="control-button start-game"
                        onClick={handleStartNewGame}
                        disabled={isLoading}
                    >
                        {isLoading ? 'Starting...' : 'Start New Game'}
                    </button>
                    
                    {sessionId && (
                        <button 
                            className="control-button abort-game"
                            onClick={handleAbortGame}
                            disabled={isLoading}
                        >
                            {isLoading ? 'Aborting...' : 'Abort Game'}
                        </button>
                    )}
                    
                    {sessionId && isActionComplete && isActionComplete() && (
                        <button 
                            className="control-button execute-action"
                            onClick={handleExecuteAction}
                            disabled={isLoading}
                        >
                            {isLoading ? 'Executing...' : 'Execute Action'}
                        </button>
                    )}
                </div>
                
                {/* Error Display */}
                {error && (
                    <div className="error-message">
                        <span className="error-icon">⚠️</span>
                        <span className="error-text">{error}</span>
                    </div>
                )}
                
                {/* Session Info */}
                {sessionId && (
                    <div className="session-info">
                        <span className="session-label">Session:</span>
                        <span className="session-value">{sessionId.slice(0, 8)}...</span>
                    </div>
                )}
            </div>
        </header>
    );
}