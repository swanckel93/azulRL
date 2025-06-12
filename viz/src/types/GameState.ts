import type { Factory } from "./Factory";
import type { PlayerBoard } from "./PlayerBoard";
import type { GameAction } from "./GameAction";
import type { Tile } from "./Tile";

export enum GameStateType {
    SETUP = "SETUP",
    FACTORY_FILLING = "FACTORY_FILLING",
    PLAYER_TURN = "PLAYER_TURN",
    ROUND_END = "ROUND_END",
    GAME_END = "GAME_END"
}

export enum CompletionStatus {
    NOT_COMPLETED = "NOT_COMPLETED",
    COMPLETED = "COMPLETED"
}

export interface Container {
    tiles: Tile[];
}

export interface Bag {
    tiles: Tile[];
}

export type GameState = {
    state: GameStateType;
    current_player: number;
    round_number: number;
    bag: Bag;
    factories: Factory[];
    center: Container;
    discard_pile: Container;
    players: PlayerBoard[];
    first_player_token_taken: boolean;
    completion: CompletionStatus;
    winner: number;
    validActions: GameAction[];
}