import { TileComponent } from "./TileComponent";
import { TileType } from "../types/Tile";
import useStore from "../stores/GameStore";
import "./BoardCenter.css";

export function BoardCenter() {
    const center = useStore(state => state.gameState.center);
    const selectTileFromCenter = useStore(state => state.selectTileFromCenter);
    const partialAction = useStore(state => state.partialAction);

    // Aggregate tiles by type
    const aggregatedTiles = center.tiles.reduce((acc, tile) => {
        acc[tile.type] = (acc[tile.type] || 0) + 1;
        return acc;
    }, {} as Record<TileType, number>);

    const handleTileClick = (tileType: TileType) => {
        selectTileFromCenter(tileType);
    };

    return (
        <div className="board-center">
            <h3>Center</h3>
            <div className="center-tiles">
                {Object.entries(aggregatedTiles).map(([tileType, count]) => (
                    <div 
                        key={tileType}
                        className={`center-tile-group ${
                            partialAction.tileType === tileType && partialAction.factoryId === -1 
                                ? 'selected' 
                                : ''
                        }`}
                        onClick={() => handleTileClick(tileType as TileType)}
                    >
                        <TileComponent type={tileType as TileType} />
                        <div className="tile-count">{count}</div>
                    </div>
                ))}
                {center.tiles.length === 0 && (
                    <div className="empty-center">Center is empty</div>
                )}
            </div>
        </div>
    );
}