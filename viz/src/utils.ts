import { BASIC_COLOR_PALLETTE } from "./constants/colors"
import { TileType } from "./types/Tile"
import { TilePlaceholderType } from "./types/TilePlaceholder"


export const TILE_PLACEHOLDER_COLOR_MAP = {
    [TilePlaceholderType.RED]: BASIC_COLOR_PALLETTE[TilePlaceholderType.RED],
    [TilePlaceholderType.YELLOW]: BASIC_COLOR_PALLETTE[TilePlaceholderType.YELLOW],
    [TilePlaceholderType.BLACK]: BASIC_COLOR_PALLETTE[TilePlaceholderType.BLACK],
    [TilePlaceholderType.WHITE]: BASIC_COLOR_PALLETTE[TilePlaceholderType.WHITE],
    [TilePlaceholderType.BLUE]: BASIC_COLOR_PALLETTE[TilePlaceholderType.BLUE],
    [TilePlaceholderType.GENERIC]: BASIC_COLOR_PALLETTE["white"],

}

export const TILE_COLOR_MAP = {
    [TileType.RED]: BASIC_COLOR_PALLETTE[TileType.RED],
    [TileType.YELLOW]: BASIC_COLOR_PALLETTE[TileType.YELLOW],
    [TileType.BLACK]: BASIC_COLOR_PALLETTE[TileType.BLACK],
    [TileType.WHITE]: BASIC_COLOR_PALLETTE[TileType.WHITE],
    [TileType.BLUE]: BASIC_COLOR_PALLETTE[TileType.BLUE],

}