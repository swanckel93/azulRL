import useStore from "../stores/GameStore";
import { GameStateType } from "../types/GameState";
import "./Header.css";

export function Header() {
    const gameState = useStore(state => state.gameState);
    const partialAction = useStore(state => state.partialAction);
    
    const getStateDisplayName = (state: GameStateType): string => {
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

    return (
        <header className="game-header">
            <div className="game-info">
                <h1>Azul Game</h1>
                <div className="game-state">
                    <span className="state-label">Status:</span>
                    <span className="state-value">{getStateDisplayName(gameState.state)}</span>
                </div>
                <div className="round-info">
                    <span className="round-label">Round:</span>
                    <span className="round-value">{gameState.round_number}</span>
                </div>
                <div className="player-info">
                    <span className="player-label">Current Player:</span>
                    <span className="player-value">Player {gameState.current_player + 1}</span>
                </div>
                {gameState.first_player_token_taken && (
                    <div className="first-player-token">
                        <span>🎯 First Player Token Taken</span>
                    </div>
                )}
            </div>
            
            {Object.keys(partialAction).length > 0 && (
                <div className="action-preview">
                    <h3>Current Action:</h3>
                    {partialAction.tileType && (
                        <span>Tile: {partialAction.tileType}</span>
                    )}
                    {partialAction.factoryId !== undefined && (
                        <span>
                            From: {partialAction.factoryId === -1 ? 'Center' : `Factory ${partialAction.factoryId + 1}`}
                        </span>
                    )}
                    {partialAction.patternLine !== undefined && (
                        <span>To: Pattern Line {partialAction.patternLine + 1}</span>
                    )}
                </div>
            )}
        </header>
    );
}