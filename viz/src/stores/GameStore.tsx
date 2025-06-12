import { create } from "zustand"
import { GameStateType, CompletionStatus, type GameState } from "../types/GameState"
import type { Factory } from "../types/Factory"
import { TileType } from "../types/Tile"

interface PartialAction {
    tileType?: TileType;
    factoryId?: number; // -1 for center
    patternLine?: number;
}

interface GameStore {
    gameState: GameState,
    partialAction: PartialAction,
    setGameState: (gameState: GameState) => void,
    getFactoryByIndex: (index: number) => Factory | undefined,
    selectTileFromFactory: (tileType: TileType, factoryId: number) => void,
    selectTileFromCenter: (tileType: TileType) => void,
    selectPatternLine: (patternLine: number) => void,
    clearAction: () => void,
    isActionComplete: () => boolean
}

const useStore = create<GameStore>((set, get) => ({
    gameState: {
        state: GameStateType.SETUP,
        current_player: 0,
        round_number: 1,
        bag: { tiles: [] },
        factories: [
            {
                tiles: [
                    { type: TileType.BLACK },
                    { type: TileType.BLUE },
                    { type: TileType.RED },
                    { type: TileType.WHITE },
                ]
            } as Factory,
            {
                tiles: [
                    { type: TileType.BLACK },
                    { type: TileType.BLACK },
                    { type: TileType.BLACK },
                    { type: TileType.BLACK },
                ]
            } as Factory,
            { tiles: [] } as Factory,
            { tiles: [] } as Factory,
            { tiles: [] } as Factory
        ],
        center: { tiles: [] },
        discard_pile: { tiles: [] },
        players: [
            {
                patternLines: [
                    { capacity: 1, tiles: [] },
                    { capacity: 2, tiles: [] },
                    { capacity: 3, tiles: [] },
                    { capacity: 4, tiles: [] },
                    { capacity: 5, tiles: [] }
                ],
                wall: [
                    [false, false, false, false, false],
                    [false, false, false, false, false],
                    [false, false, false, false, false],
                    [false, false, false, false, false],
                    [false, false, false, false, false]
                ],
                floor: [],
                score: 0
            },
            {
                patternLines: [
                    { capacity: 1, tiles: [] },
                    { capacity: 2, tiles: [] },
                    { capacity: 3, tiles: [] },
                    { capacity: 4, tiles: [] },
                    { capacity: 5, tiles: [] }
                ],
                wall: [
                    [false, false, false, false, false],
                    [false, false, false, false, false],
                    [false, false, false, false, false],
                    [false, false, false, false, false],
                    [false, false, false, false, false]
                ],
                floor: [],
                score: 0
            }
        ],
        first_player_token_taken: false,
        completion: CompletionStatus.NOT_COMPLETED,
        winner: -1,
        validActions: []
    } as GameState,
    partialAction: {},
    setGameState: (gameState) => set({ gameState }),
    getFactoryByIndex: (index: number) => {
        const { gameState } = get()
        return gameState.factories[index]
    },
    selectTileFromFactory: (tileType: TileType, factoryId: number) => {
        const { partialAction } = get()
        // If clicking the same tile that's already selected, deselect it
        if (partialAction.tileType === tileType && partialAction.factoryId === factoryId) {
            set(state => ({
                partialAction: { ...state.partialAction, tileType: undefined, factoryId: undefined }
            }))
            console.log(`Tile ${tileType} deselected from factory ${factoryId}`)
        } else {
            // Otherwise, select the new tile
            set(state => ({
                partialAction: { ...state.partialAction, tileType, factoryId }
            }))
            console.log(`Tile ${tileType} selected from factory ${factoryId}`)
        }
    },
    selectTileFromCenter: (tileType: TileType) => {
        const { partialAction } = get()
        // If clicking the same tile that's already selected from center, deselect it
        if (partialAction.tileType === tileType && partialAction.factoryId === -1) {
            set(state => ({
                partialAction: { ...state.partialAction, tileType: undefined, factoryId: undefined }
            }))
            console.log(`Tile ${tileType} deselected from center`)
        } else {
            // Otherwise, select the new tile from center
            set(state => ({
                partialAction: { ...state.partialAction, tileType, factoryId: -1 }
            }))
            console.log(`Tile ${tileType} selected from center`)
        }
    },
    selectPatternLine: (patternLine: number) => {
        set(state => ({
            partialAction: { ...state.partialAction, patternLine }
        }))
    },
    clearAction: () => set({ partialAction: {} }),
    isActionComplete: () => {
        const { partialAction } = get()
        return partialAction.tileType !== undefined &&
            partialAction.factoryId !== undefined &&
            partialAction.patternLine !== undefined
    }
}))

export default useStore