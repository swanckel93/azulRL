// PlayerBoard.tsx
import { TileType } from "../types/Tile";
import { TileComponent } from "./TileComponent";
import TilePlaceholderComponent from "./TilePlaceholder";
import { TilePlaceholderType } from "../types/TilePlaceholder";
import useStore from "../stores/GameStore";
import "./PlayerBoard.css";
import { type PlayerBoard as PlayerBoardType } from "../types/PlayerBoard.ts";

interface PlayerBoardProps {
    playerIndex: number;
}

export function PlayerBoard({ playerIndex }: PlayerBoardProps) {
    const playerState = useStore(state => state.gameState.players[playerIndex]) as PlayerBoardType;
    const selectPatternLine = useStore(state => state.selectPatternLine);
    const partialAction = useStore(state => state.partialAction);
    const currentPlayer = useStore(state => state.gameState.current_player);
    
    if (!playerState) {
        return <div className="player-board">Loading player...</div>;
    }

    // Wall configuration - matches the Python WALL_PATTERN
    const WALL_PATTERN: TileType[][] = [
        [TileType.BLUE, TileType.YELLOW, TileType.RED, TileType.BLACK, TileType.WHITE],
        [TileType.WHITE, TileType.BLUE, TileType.YELLOW, TileType.RED, TileType.BLACK],
        [TileType.BLACK, TileType.WHITE, TileType.BLUE, TileType.YELLOW, TileType.RED],
        [TileType.RED, TileType.BLACK, TileType.WHITE, TileType.BLUE, TileType.YELLOW],
        [TileType.YELLOW, TileType.RED, TileType.BLACK, TileType.WHITE, TileType.BLUE]
    ];

    // Convert TileType to TilePlaceholderType
    const tileTypeToPlaceholderType = (tileType: TileType): TilePlaceholderType => {
        switch (tileType) {
            case TileType.BLUE:
                return TilePlaceholderType.BLUE;
            case TileType.YELLOW:
                return TilePlaceholderType.YELLOW;
            case TileType.RED:
                return TilePlaceholderType.RED;
            case TileType.BLACK:
                return TilePlaceholderType.BLACK;
            case TileType.WHITE:
                return TilePlaceholderType.WHITE;
            default:
                return TilePlaceholderType.GENERIC;
        }
    };

    const handlePatternLineClick = (lineIndex: number) => {
        // Only allow pattern line selection for the current player
        if (isCurrentPlayer) {
            selectPatternLine(lineIndex);
        }
    };

    const isCurrentPlayer = currentPlayer === playerIndex;

    return (
        <div className={`player-board ${isCurrentPlayer ? 'current-player' : ''}`}>
            <div className="player-info">
                <h2>Player {playerIndex + 1} {isCurrentPlayer ? '(Current)' : ''}</h2>
                <div className="score-display">Score: {playerState.score}</div>
            </div>
            
            <div className="board-main">
                <div className="board-headers">
                    <h3 className="pattern-lines-header">Pattern Lines</h3>
                    <h3 className="wall-header">Wall</h3>
                </div>
                
                <div className="pattern-lines-and-wall-section">
                    {(playerState.patternLines || []).map((line, lineIndex) => (
                        <div key={`pattern-line-${lineIndex}`} className="board-row">
                            <div
                                className={`pattern-line ${partialAction.patternLine === lineIndex && isCurrentPlayer ? 'selected' : ''} ${!isCurrentPlayer ? 'disabled' : ''}`}
                                onClick={() => handlePatternLineClick(lineIndex)}
                            >
                                {/* Create slots for pattern line, aligned right */}
                                {Array.from({ length: lineIndex + 1 }).map((_, i) => {
                                    // Calculate position from right (reverse index)
                                    const slotIndex = lineIndex - i;
                                    return (
                                        <div key={`placeholder-${i}`} className="pattern-line-slot">
                                            {slotIndex < (line.tiles || []).length ? (
                                                <TileComponent type={line.tiles?.[slotIndex]?.type} />
                                            ) : (
                                                <TilePlaceholderComponent
                                                    id={i}
                                                    type={TilePlaceholderType.GENERIC}
                                                />
                                            )}
                                        </div>
                                    );
                                })}
                            </div>
                            
                            {/* Wall row aligned horizontally with pattern line */}
                            <div className="wall-row">
                                {WALL_PATTERN[lineIndex].map((tileType, colIndex) => {
                                    const isPlaced = playerState.wall[lineIndex]?.[colIndex];
                                    
                                    // String-based gradient mapping (matching TileComponent.css)
                                    const getGradientByString = (typeString: string): string => {
                                        switch (typeString) {
                                            case 'blue': return 'linear-gradient(135deg, #1e40af 0%, #3b82f6 100%)';
                                            case 'yellow': return 'linear-gradient(135deg, #eab308 0%, #fbbf24 100%)';
                                            case 'red': return 'linear-gradient(135deg, #dc2626 0%, #ef4444 100%)';
                                            case 'black': return 'linear-gradient(135deg, #1f2937 0%, #374151 100%)';
                                            case 'white': return 'linear-gradient(135deg, #f9fafb 0%, #e5e7eb 100%)';
                                            default: return 'linear-gradient(135deg, #ff0000 0%, #ff4444 100%)';
                                        }
                                    };
                                    
                                    return (
                                        <div key={`wall-tile-${colIndex}`} style={{ 
                                            width: '54px',
                                            height: '54px',
                                            display: 'flex',
                                            alignItems: 'center',
                                            justifyContent: 'center'
                                        }}>
                                            {isPlaced ? (
                                                <TileComponent type={tileType} />
                                            ) : (
                                                <div 
                                                    style={{ 
                                                        background: getGradientByString(tileType),
                                                        width: '50px',
                                                        height: '50px',
                                                        border: '2px dashed #9ca3af',
                                                        borderRadius: '4px',
                                                        opacity: 0.6
                                                    }}
                                                />
                                            )}
                                        </div>
                                    );
                                })}
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            <div className="board-section floor-line">
                <h3>Floor Line</h3>
                <div className="floor-tiles">
                    {Array.from({ length: 7 }).map((_, index) => {
                        const penalties = [-1, -1, -2, -2, -2, -3, -3];
                        const tile = (playerState.floor || [])[index];
                        return (
                            <div key={`floor-slot-${index}`} className="floor-slot">
                                {tile ? (
                                    <TileComponent type={tile.type} />
                                ) : (
                                    <div className="floor-empty-slot" />
                                )}
                                <div className="floor-penalty">{penalties[index]}</div>
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
}