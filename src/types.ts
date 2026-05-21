export const BOARD_SIZE = 6;
export const TURN_ACTION_POINTS = 2;

export type Player = 'X' | 'O';

export type AnomalyType = 'teleport' | 'destroy' | 'clone';

export interface Anomaly {
  id: string;
  type: AnomalyType;
}

export interface Cell {
  id: string;
  row: number;
  col: number;
  piece: Player | null;
  anomaly: Anomaly | null;
}

export type Board = Cell[][];

export type VictoryConditionType = 'classic' | 'square' | 'diagonal' | 'encirclement';

export interface VictoryCondition {
  type: VictoryConditionType;
  title: string;
  short: string;
  description: string;
}

export interface GameEvent {
  id: string;
  turn: number;
  message: string;
  tone: 'system' | 'player' | 'anomaly' | 'victory';
}

export interface Winner {
  player: Player;
  condition: VictoryCondition;
  message: string;
}

export interface GameState {
  board: Board;
  currentPlayer: Player;
  actionPoints: number;
  turn: number;
  completedTurns: number;
  victoryCondition: VictoryCondition;
  selectedCellId: string | null;
  events: GameEvent[];
  winner: Winner | null;
}

export interface Coordinate {
  row: number;
  col: number;
}
