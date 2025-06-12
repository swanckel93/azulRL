import { BASIC_COLOR_PALLETTE } from "../constants/colors"
import type { TileType } from "../types/Tile"
import "./TileComponent.css"
interface TileComponentProps {
    type: TileType
}
export function TileComponent(props: TileComponentProps) {

    return (
        <div className="tile" style={{ backgroundColor: BASIC_COLOR_PALLETTE[props.type] }}>

        </div>
    )
}