import { BoardCell } from './BoardCell';
import type { Board, Player } from '../types';

interface GameBoardProps {
  board: Board;
  selectedCellId: string | null;
  validMoveIds: string[];
  currentPlayer: Player;
  onSelectCell: (cellId: string) => void;
}

export function GameBoard({ board, selectedCellId, validMoveIds, currentPlayer, onSelectCell }: GameBoardProps) {
  return (
    <section className="relative rounded-[2rem] border border-cyan-300/20 bg-slate-950/55 p-3 shadow-[0_0_70px_rgba(8,145,178,0.18)] backdrop-blur-xl md:p-5">
      <div className="absolute -inset-px -z-10 rounded-[2rem] bg-gradient-to-br from-cyan-500/30 via-fuchsia-500/10 to-indigo-500/25 blur-xl" />
      <div className="grid grid-cols-6 gap-2 md:gap-3">
        {board.flat().map((cell) => (
          <BoardCell
            key={cell.id}
            cell={cell}
            currentPlayer={currentPlayer}
            isSelected={selectedCellId === cell.id}
            isValidMove={validMoveIds.includes(cell.id)}
            onSelect={onSelectCell}
          />
        ))}
      </div>
    </section>
  );
}
