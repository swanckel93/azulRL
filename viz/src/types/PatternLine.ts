import { type Tile, TileType } from "./Tile";

export interface PatternLine {
    capacity: number;
    tiles: Tile[];
}