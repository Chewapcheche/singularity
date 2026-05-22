export const BOARD_SIZE = 6;
export const INITIAL_BOARD_SIZE = 4;
export const MID_BOARD_SIZE = 5;
export const FINAL_BOARD_SIZE = 6;
export const FIRST_EXPANSION_MOVE = 4;
export const SECOND_EXPANSION_MOVE = 7;
export const DRAW_MOVE_LIMIT = 13;
export const OPENING_TURN_ACTION_POINTS = 1;
export const STANDARD_TURN_ACTION_POINTS = 2;

export const getActionPointsForTurn = (turn: number): number =>
  turn === 1 ? OPENING_TURN_ACTION_POINTS : STANDARD_TURN_ACTION_POINTS;

export const getBoardSizeForMoveCount = (moveCount: number): number => {
  if (moveCount >= SECOND_EXPANSION_MOVE) return FINAL_BOARD_SIZE;
  if (moveCount >= FIRST_EXPANSION_MOVE) return MID_BOARD_SIZE;
  return INITIAL_BOARD_SIZE;
};

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

export interface DrawState {
  message: string;
}

export interface GameState {
  board: Board;
  activeBoardSize: number;
  moveCount: number;
  currentPlayer: Player;
  actionPoints: number;
  turn: number;
  completedTurns: number;
  victoryCondition: VictoryCondition;
  selectedCellId: string | null;
  events: GameEvent[];
  winner: Winner | null;
  draw: DrawState | null;
}

export interface Coordinate {
  row: number;
  col: number;
}
