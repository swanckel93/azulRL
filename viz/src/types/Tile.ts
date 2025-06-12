export enum TileType {
    BLUE = 'blue',
    YELLOW = 'yellow',
    RED = 'red',
    BLACK = 'black',
    WHITE = 'white',
    FIRST_PLAYER = 'first_player',
}

export interface Tile {
    type: TileType
}