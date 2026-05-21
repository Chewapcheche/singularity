import { create } from 'zustand';
import { activateAnomaly, createInitialGameState, getValidMoves, movePiece, placePiece } from '../engine/gameEngine';
import type { GameState } from '../types';

interface GameStore extends GameState {
  validMoveIds: string[];
  selectCell: (cellId: string) => void;
  resetGame: () => void;
}

const withValidMoves = (state: GameState): GameState & { validMoveIds: string[] } => ({
  ...state,
  validMoveIds: getValidMoves(state.board, state.selectedCellId),
});

export const useGameStore = create<GameStore>((set, get) => ({
  ...withValidMoves(createInitialGameState()),
  selectCell: (cellId) => {
    const state = get();
    if (state.winner) return;

    const cell = state.board.flat().find((candidate) => candidate.id === cellId);
    if (!cell) return;

    const selected = state.selectedCellId
      ? state.board.flat().find((candidate) => candidate.id === state.selectedCellId)
      : null;

    let nextState: GameState;

    if (selected && state.validMoveIds.includes(cellId)) {
      nextState = movePiece(state, selected.id, cellId);
      set(withValidMoves(nextState));
      return;
    }

    if (cell.piece === state.currentPlayer && cell.anomaly) {
      nextState = activateAnomaly(state, cellId);
      set(withValidMoves(nextState));
      return;
    }

    if (cell.piece === state.currentPlayer) {
      set(withValidMoves({ ...state, selectedCellId: state.selectedCellId === cellId ? null : cellId }));
      return;
    }

    if (!cell.piece) {
      nextState = placePiece(state, cellId);
      set(withValidMoves(nextState));
    }
  },
  resetGame: () => set(withValidMoves(createInitialGameState())),
}));
