// types/PlayerBoard.ts
import { type Tile, TileType } from "./Tile";
import { type PatternLine } from "./PatternLine.ts";

export interface PlayerBoard {
    patternLines: PatternLine[];
    wall: boolean[][]; // Represents whether a tile is placed at each position
    floor: Tile[];
    score: number;
}