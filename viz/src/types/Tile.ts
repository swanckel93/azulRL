export enum TileType {
    BLUE = 'blue',
    YELLOW = 'yellow',
    RED = 'red',
    BLACK = 'black',
    WHITE = 'white',
}
export enum SpecialTileType {
    THE_ONE = "white"
}

export interface Tile {
    type: TileType
}