import type { TilePlaceHolder } from "../types/TilePlaceholder";
import { TILE_PLACEHOLDER_COLOR_MAP, TILE_COLOR_MAP } from "../utils";
import { TileType } from "../types/Tile";
import "./TilePlaceholder.css"

export default function TilePlaceholderComponent({ id, type }: TilePlaceHolder) {
    // Check if type is actually a TileType (passed from wall)
    const isWallTile = Object.values(TileType).includes(type as any);
    const color = isWallTile 
        ? TILE_COLOR_MAP[type as TileType]
        : TILE_PLACEHOLDER_COLOR_MAP[type];

    // For GENERIC placeholders (pattern lines), don't override background - use CSS
    const shouldOverrideBackground = isWallTile || type !== 'generic';

    return (
        <div
            id={id.toString()}
            className="tile-placeholder"
            style={shouldOverrideBackground ? { backgroundColor: color } : {}}>

        </div>

    )
}