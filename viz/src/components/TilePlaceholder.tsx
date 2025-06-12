import type { TilePlaceHolder } from "../types/TilePlaceholder";
import { TILE_PLACEHOLDER_COLOR_MAP } from "../utils";
import "./TilePlaceholder.css"

export default function TilePlaceholderComponent({ id, type }: TilePlaceHolder) {

    return (
        <div
            id={id.toString()}
            className="tile-placeholder"
            style={{ backgroundColor: TILE_PLACEHOLDER_COLOR_MAP[type] }}>

        </div>

    )
}