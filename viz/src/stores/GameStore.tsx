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
    playerId: string | null,
    isLoading: boolean,
    error: string | null,
    setGameState: (gameState: GameState) => void,
    getFactoryByIndex: (index: number) => Factory | undefined,
    selectTileFromFactory: (tileType: TileType, factoryId: number) => void,
    selectTileFromCenter: (tileType: TileType) => void,
    selectPatternLine: (patternLine: number) => void,
    clearAction: () => void,
    isActionComplete: () => boolean,
    isActionValid: (tileType: TileType, factoryId: number, patternLine: number) => boolean,
    setError: (error: string | null) => void,
    startNewGame: (numPlayers?: number, gameMode?: string, playerName?: string) => Promise<string>,
    joinSession: (sessionId: string, playerName?: string) => Promise<void>,
    leaveSession: () => Promise<void>,
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
    playerId: null,
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
    clearAction: () => set({ partialAction: {}, error: null }),
    setError: (error: string | null) => set({ error }),
    isActionComplete: () => {
        const { partialAction } = get()
        return partialAction && 
            partialAction.tileType !== undefined &&
            partialAction.factoryId !== undefined &&
            partialAction.patternLine !== undefined
    },
    
    isActionValid: (tileType: TileType, factoryId: number, patternLine: number) => {
        const { gameState } = get()
        if (!gameState.validActions) return false
        
        const actionType = factoryId === -1 ? 'TAKE_FROM_CENTER' : 'TAKE_FROM_FACTORY'
        
        console.log('Checking action validity:', { tileType, factoryId, patternLine, actionType })
        console.log('Available validActions:', gameState.validActions)
        
        const isValid = gameState.validActions.some(action => 
            action.type === actionType &&
            action.tile_type === tileType.toUpperCase() &&
            (factoryId === -1 ? true : action.factory_id === factoryId) &&
            action.pattern_line === patternLine
        )
        
        console.log('Action is valid:', isValid)
        return isValid
    },
    
    // Backend API functions
    startNewGame: async (numPlayers = 2, gameMode = 'SELFPLAY', playerName?: string) => {
        set({ isLoading: true, error: null })
        try {
            const requestBody: any = { 
                num_players: numPlayers,
                game_mode: gameMode
            }
            
            if (playerName) {
                requestBody.player_name = playerName
            }
            
            const response = await axios.post(`${API_BASE_URL}/sessions`, requestBody)
            const { session_id, game_state, player_id } = response.data
            
            console.log('Received response:', { session_id, game_state, player_id })
            
            set({ 
                sessionId: session_id,
                playerId: player_id || null,
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

    joinSession: async (sessionId: string, playerName?: string) => {
        set({ isLoading: true, error: null })
        try {
            const requestBody: any = {}
            if (playerName) {
                requestBody.player_name = playerName
            }
            
            const response = await axios.post(`${API_BASE_URL}/sessions/${sessionId}/join`, requestBody)
            const { player_id, player_index, game_state } = response.data
            
            set({ 
                sessionId: sessionId,
                playerId: player_id,
                gameState: game_state,
                partialAction: {},
                isLoading: false,
                error: null
            })
            
            console.log(`Joined session ${sessionId} as player ${player_index}`)
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Failed to join session'
            set({ isLoading: false, error: errorMessage })
            console.error('Failed to join session:', error)
            throw error
        }
    },

    leaveSession: async () => {
        const { sessionId, playerId } = get()
        if (!sessionId || !playerId) {
            set({ error: 'No active session to leave' })
            return
        }

        set({ isLoading: true, error: null })
        try {
            await axios.post(`${API_BASE_URL}/sessions/${sessionId}/leave/${playerId}`)
            
            set({ 
                sessionId: null,
                playerId: null,
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
            
            console.log('Left session successfully')
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Failed to leave session'
            set({ isLoading: false, error: errorMessage })
            console.error('Failed to leave session:', error)
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
        const { sessionId, partialAction, isActionComplete, isActionValid } = get()
        
        if (!sessionId) {
            set({ error: 'No active game session' })
            return
        }

        if (!isActionComplete()) {
            set({ error: 'Action is not complete' })
            return
        }

        // Validate action against validActions before sending
        if (!isActionValid(partialAction.tileType!, partialAction.factoryId!, partialAction.patternLine!)) {
            set({ error: 'Invalid action - not allowed by game rules' })
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