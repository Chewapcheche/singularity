import { BoardCell } from './BoardCell';
import type { Board, Player } from '../types';

interface GameBoardProps {
  board: Board;
  activeBoardSize: number;
  selectedCellId: string | null;
  currentPlayer: Player;
  onSelectCell: (cellId: string) => void;
}

export function GameBoard({
  board,
  activeBoardSize,
  selectedCellId,
  currentPlayer,
  onSelectCell,
}: GameBoardProps) {
  const visibleCells = board
    .slice(0, activeBoardSize)
    .flatMap((row) => row.slice(0, activeBoardSize));

  return (
    <section
      className="relative flex aspect-square w-full max-w-full rounded-[1.6rem] border border-cyan-300/20 bg-slate-950/55 p-2 shadow-[0_0_70px_rgba(8,145,178,0.18)] backdrop-blur-xl sm:p-3"
      style={{ width: 'min(100%, calc(100dvh - 8.75rem))' }}
    >
      <div className="absolute -inset-px -z-10 rounded-[1.6rem] bg-gradient-to-br from-cyan-500/30 via-fuchsia-500/10 to-indigo-500/25 blur-xl" />
      <div
        className="grid min-h-0 flex-1 gap-1.5 sm:gap-2"
        style={{ gridTemplateColumns: `repeat(${activeBoardSize}, minmax(0, 1fr))` }}
      >
        {visibleCells.map((cell) => (
          <BoardCell
            key={cell.id}
            cell={cell}
            currentPlayer={currentPlayer}
            isSelected={selectedCellId === cell.id}
            onSelect={onSelectCell}
          />
        ))}
      </div>
    </section>
  );
}
