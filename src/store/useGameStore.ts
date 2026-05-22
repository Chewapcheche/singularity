import { create } from 'zustand';
import { activateAnomaly, createInitialGameState, placePiece } from '../engine/gameEngine';
import type { GameState } from '../types';

interface GameStore extends GameState {
  validMoveIds: string[];
  selectCell: (cellId: string) => void;
  resetGame: () => void;
}

const withValidMoves = (state: GameState): GameState & { validMoveIds: string[] } => ({
  ...state,
  validMoveIds: [],
});

export const useGameStore = create<GameStore>((set, get) => ({
  ...withValidMoves(createInitialGameState()),
  selectCell: (cellId) => {
    const state = get();
    if (state.winner || state.draw) return;

    const cell = state.board.flat().find((candidate) => candidate.id === cellId);
    if (!cell) return;

    let nextState: GameState | null = null;

    if (cell.piece === state.currentPlayer && cell.anomaly) {
      nextState = activateAnomaly(state, cellId);
    } else if (!cell.piece) {
      nextState = placePiece(state, cellId);
    }

    if (nextState) {
      set(withValidMoves(nextState));
    } else {
      set(withValidMoves({ ...state, selectedCellId: null }));
    }
  },
  resetGame: () => set(withValidMoves(createInitialGameState())),
}));
