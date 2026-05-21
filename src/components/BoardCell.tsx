import { Binary, Copy, Orbit, Sparkles, Zap, type LucideIcon } from 'lucide-react';
import { anomalyDescriptions } from '../engine/gameEngine';
import type { AnomalyType, Cell, Player } from '../types';

interface BoardCellProps {
  cell: Cell;
  isSelected: boolean;
  isValidMove: boolean;
  currentPlayer: Player;
  onSelect: (cellId: string) => void;
}

const anomalyIcon: Record<AnomalyType, LucideIcon> = {
  teleport: Orbit,
  destroy: Zap,
  clone: Copy,
};

const anomalyClasses: Record<AnomalyType, string> = {
  teleport: 'from-cyan-400/25 via-sky-500/15 to-blue-500/20 border-cyan-300/70 text-cyan-100 shadow-[0_0_28px_rgba(34,211,238,0.28)]',
  destroy: 'from-rose-500/25 via-red-500/15 to-orange-500/20 border-rose-300/70 text-rose-100 shadow-[0_0_28px_rgba(244,63,94,0.28)]',
  clone: 'from-emerald-400/25 via-teal-400/15 to-lime-400/20 border-emerald-300/70 text-emerald-100 shadow-[0_0_28px_rgba(16,185,129,0.28)]',
};

export function BoardCell({ cell, isSelected, isValidMove, currentPlayer, onSelect }: BoardCellProps) {
  const Icon = cell.anomaly ? anomalyIcon[cell.anomaly.type] : Binary;
  const canActivate = cell.piece === currentPlayer && cell.anomaly;
  const tooltip = cell.anomaly ? anomalyDescriptions[cell.anomaly.type] : null;

  return (
    <button
      type="button"
      aria-label={`Sector ${cell.row + 1}.${cell.col + 1}${cell.piece ? ` occupied by ${cell.piece}` : ''}`}
      title={tooltip ? `${tooltip.label}: ${tooltip.description}` : 'Empty sector'}
      onClick={() => onSelect(cell.id)}
      className={[
        'group relative aspect-square overflow-hidden rounded-2xl border bg-slate-950/80 transition duration-200 ease-out',
        'hover:-translate-y-0.5 hover:border-cyan-300/80 hover:shadow-neon focus:outline-none focus:ring-2 focus:ring-cyan-300/80',
        cell.anomaly
          ? `bg-gradient-to-br ${anomalyClasses[cell.anomaly.type]}`
          : 'border-cyan-500/20 shadow-[inset_0_0_18px_rgba(15,23,42,0.9)]',
        isSelected ? 'scale-[1.03] border-fuchsia-300 shadow-violet ring-2 ring-fuchsia-300/70' : '',
        isValidMove ? 'border-lime-300/80 shadow-[0_0_26px_rgba(190,242,100,0.35)]' : '',
        canActivate ? 'animate-slow-pulse' : '',
      ].join(' ')}
    >
      <span className="absolute inset-px rounded-2xl bg-[radial-gradient(circle_at_50%_0%,rgba(255,255,255,0.16),transparent_38%)] opacity-80" />
      <span className="absolute left-2 top-2 text-[0.58rem] font-semibold tracking-[0.24em] text-slate-400/70">
        {cell.row + 1}.{cell.col + 1}
      </span>

      {cell.anomaly && (
        <span className="absolute right-2 top-2 rounded-full border border-white/15 bg-black/35 p-1 text-current backdrop-blur">
          <Icon size={14} />
        </span>
      )}

      {isValidMove && (
        <span className="absolute inset-0 grid place-items-center">
          <span className="h-4 w-4 rounded-full border border-lime-200 bg-lime-300/30 shadow-[0_0_18px_rgba(190,242,100,0.8)]" />
        </span>
      )}

      {cell.piece && (
        <span
          className={[
            'relative z-10 flex h-full items-center justify-center font-display text-4xl font-black md:text-5xl',
            cell.piece === 'X'
              ? 'text-cyan-100 drop-shadow-[0_0_18px_rgba(34,211,238,0.9)]'
              : 'text-fuchsia-100 drop-shadow-[0_0_18px_rgba(217,70,239,0.9)]',
          ].join(' ')}
        >
          {cell.piece}
        </span>
      )}

      {!cell.piece && !isValidMove && (
        <Sparkles
          size={16}
          className="absolute bottom-2 right-2 text-cyan-200/0 transition group-hover:text-cyan-200/60"
        />
      )}
    </button>
  );
}
