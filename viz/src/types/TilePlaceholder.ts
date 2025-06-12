export enum TilePlaceholderType {
    BLUE = 'blue',
    YELLOW = 'yellow',
    RED = 'red',
    BLACK = 'black',
    WHITE = 'white',
    GENERIC = 'generic'
}

export interface TilePlaceHolder {
    id: number
    type: TilePlaceholderType
}