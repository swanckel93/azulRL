import { BASIC_COLOR_PALLETTE } from "../constants/colors"
import { TileType } from "../types/Tile"
import "./TileComponent.css"
interface TileComponentProps {
    type: TileType
}
export function TileComponent(props: TileComponentProps) {
    return (
        <div className="tile" data-type={props.type}>
            {props.type === TileType.FIRST_PLAYER && "1"}
        </div>
    )
}