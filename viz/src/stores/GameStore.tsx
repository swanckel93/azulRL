import { create } from "zustand"
import axios from "axios"
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
    sessionId: string | null,
    isLoading: boolean,
    error: string | null,
    setGameState: (gameState: GameState) => void,
    getFactoryByIndex: (index: number) => Factory | undefined,
    selectTileFromFactory: (tileType: TileType, factoryId: number) => void,
    selectTileFromCenter: (tileType: TileType) => void,
    selectPatternLine: (patternLine: number) => void,
    clearAction: () => void,
    isActionComplete: () => boolean,
    startNewGame: (numPlayers?: number) => Promise<string>,
    abortGame: () => Promise<void>,
    executeAction: () => Promise<void>,
    restoreSession: (sessionId: string) => Promise<void>,
}

// Backend API configuration
// Use the same host as the frontend, but port 8000 for the backend
const API_BASE_URL = `${window.location.protocol}//${window.location.hostname}:8000`;

const useStore = create<GameStore>((set, get) => ({
    gameState: {
        state: GameStateType.SETUP,
        current_player: 0,
        round_number: 1,
        bag: { tiles: [] },
        factories: [],
        center: { tiles: [] },
        discard_pile: { tiles: [] },
        players: [],
        first_player_token_taken: false,
        completion: CompletionStatus.NOT_COMPLETED,
        winner: -1,
        validActions: []
    } as GameState,
    partialAction: {},
    sessionId: null,
    isLoading: false,
    error: null,
    setGameState: (gameState) => set({ gameState }),
    getFactoryByIndex: (index: number) => {
        const { gameState } = get()
        return gameState.factories?.[index]
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
        return partialAction && 
            partialAction.tileType !== undefined &&
            partialAction.factoryId !== undefined &&
            partialAction.patternLine !== undefined
    },
    
    // Backend API functions
    startNewGame: async (numPlayers = 2) => {
        set({ isLoading: true, error: null })
        try {
            const response = await axios.post(`${API_BASE_URL}/sessions`, { num_players: numPlayers })
            const { session_id, game_state } = response.data
            
            console.log('Received response:', { session_id, game_state })
            
            set({ 
                sessionId: session_id,
                gameState: game_state,
                partialAction: {},
                isLoading: false,
                error: null
            })
            
            console.log(`New game started with session ID: ${session_id}`)
            console.log('Updated gameState:', game_state)
            
            return session_id
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Failed to start new game'
            set({ isLoading: false, error: errorMessage })
            console.error('Failed to start new game:', error)
            throw error
        }
    },

    abortGame: async () => {
        const { sessionId } = get()
        if (!sessionId) {
            set({ error: 'No active game to abort' })
            return
        }

        set({ isLoading: true, error: null })
        try {
            await axios.delete(`${API_BASE_URL}/sessions/${sessionId}`)
            
            set({ 
                sessionId: null,
                gameState: {
                    state: GameStateType.GAME_END,
                    current_player: 0,
                    round_number: 1,
                    bag: { tiles: [] },
                    factories: [],
                    center: { tiles: [] },
                    discard_pile: { tiles: [] },
                    players: [],
                    first_player_token_taken: false,
                    completion: CompletionStatus.NOT_COMPLETED,
                    winner: -1,
                    validActions: []
                } as GameState,
                partialAction: {},
                isLoading: false,
                error: null
            })
            
            console.log('Game aborted successfully')
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Failed to abort game'
            set({ isLoading: false, error: errorMessage })
            console.error('Failed to abort game:', error)
        }
    },

    executeAction: async () => {
        const { sessionId, partialAction, isActionComplete } = get()
        
        if (!sessionId) {
            set({ error: 'No active game session' })
            return
        }

        if (!isActionComplete()) {
            set({ error: 'Action is not complete' })
            return
        }

        set({ isLoading: true, error: null })
        try {
            const action = {
                type: partialAction.factoryId === -1 ? 'TAKE_FROM_CENTER' : 'TAKE_FROM_FACTORY',
                factory_id: partialAction.factoryId === -1 ? undefined : partialAction.factoryId,
                tile_type: partialAction.tileType,
                pattern_line: partialAction.patternLine
            }

            const response = await axios.post(`${API_BASE_URL}/sessions/${sessionId}/actions`, action)
            const { game_state } = response.data
            
            set({ 
                gameState: game_state,
                partialAction: {},
                isLoading: false,
                error: null
            })
            
            console.log('Action executed successfully')
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Failed to execute action'
            set({ isLoading: false, error: errorMessage })
            console.error('Failed to execute action:', error)
        }
    },

    restoreSession: async (sessionId: string) => {
        set({ isLoading: true, error: null })
        try {
            const response = await axios.get(`${API_BASE_URL}/sessions/${sessionId}`)
            const { game_state } = response.data
            
            set({ 
                sessionId: sessionId,
                gameState: game_state,
                partialAction: {},
                isLoading: false,
                error: null
            })
            
            console.log(`Session restored: ${sessionId}`)
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Failed to restore session'
            set({ isLoading: false, error: errorMessage })
            console.error('Failed to restore session:', error)
            
            // If session is invalid, redirect to home (this will be handled by the component)
            throw new Error('Session not found or expired')
        }
    }
}))

export default useStore