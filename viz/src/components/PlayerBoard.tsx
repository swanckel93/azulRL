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
                <div className="pattern-lines-section">
                    <h3>Pattern Lines</h3>
                    {playerState.patternLines.map((line, lineIndex) => (
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
                                            {slotIndex < line.tiles.length ? (
                                                <TileComponent type={line.tiles[slotIndex].type} />
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
                                    return (
                                        <div key={`wall-tile-${colIndex}`} className="wall-tile">
                                            {isPlaced ? (
                                                <TileComponent type={tileType} />
                                            ) : (
                                                <div className="wall-empty" />
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
                    {playerState.floor.map((tile, index) => (
                        <TileComponent key={`floor-tile-${index}`} type={tile.type} />
                    ))}
                    {/* Show empty floor line slots */}
                    {Array.from({ length: Math.max(0, 7 - playerState.floor.length) }).map((_, index) => (
                        <div key={`floor-empty-${index}`} className="floor-empty-slot" />
                    ))}
                </div>
            </div>
        </div>
    );
}