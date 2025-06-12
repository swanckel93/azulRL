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
                <div className="bag-info">
                    <span className="bag-icon">🎒</span>
                    <span className="bag-label">Bag:</span>
                    <span className="bag-value">{gameState.bag.tiles.length}</span>
                </div>
                <div className="discard-info">
                    <span className="discard-icon">🗑️</span>
                    <span className="discard-label">Discard:</span>
                    <span className="discard-value">{gameState.discard_pile.tiles.length}</span>
                </div>
                {gameState.first_player_token_taken && (
                    <div className="first-player-token">
                        <span>🎯 First Player Token Taken</span>
                    </div>
                )}
                {Object.keys(partialAction).length > 0 && (
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
            </div>
        </header>
    );
}