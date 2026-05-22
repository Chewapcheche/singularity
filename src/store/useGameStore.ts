import { create } from 'zustand';
import { activateAnomaly, createInitialGameState, placePiece } from '../engine/gameEngine';
import type { GameState } from '../types';

interface GameStore extends GameState {
  selectCell: (cellId: string) => void;
  resetGame: () => void;
}

const withDerivedState = (state: GameState): GameState => state;

export const useGameStore = create<GameStore>((set, get) => ({
  ...withDerivedState(createInitialGameState()),
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
      set(withDerivedState(nextState));
    } else {
      set(withDerivedState({ ...state, selectedCellId: null }));
    }
  },
  resetGame: () => set(withDerivedState(createInitialGameState())),
}));
