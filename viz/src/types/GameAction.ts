import type { TileType } from "./Tile"

export enum GameActionType {
    TAKE_FROM_FACTORY = "TAKE_FROM_FACTORY",
    TAKE_FROM_CENTER = "TAKE_FROM_CENTER"
}
export interface GameAction {
    type: GameActionType
    factory_id?: number
    tile_type: TileType
    pattern_line?: number

}