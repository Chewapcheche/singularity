import { Activity, Crosshair, HelpCircle, RefreshCw } from 'lucide-react';
import { DRAW_TURN_LIMIT, type Player, type VictoryCondition } from '../types';

interface StatusPanelProps {
  currentPlayer: Player;
  actionPoints: number;
  maxActionPoints: number;
  turn: number;
  activeBoardSize: number;
  victoryCondition: VictoryCondition;
  onOpenHints: () => void;
  onRestart: () => void;
}

export function StatusPanel({
  currentPlayer,
  actionPoints,
  maxActionPoints,
  turn,
  activeBoardSize,
  victoryCondition,
  onOpenHints,
  onRestart,
}: StatusPanelProps) {
  return (
    <aside className="grid gap-3">
      <div className="rounded-3xl border border-cyan-300/20 bg-slate-950/70 p-4 shadow-neon backdrop-blur-xl">
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <span
              className={[
                'grid h-14 w-14 place-items-center rounded-2xl border font-display text-4xl font-black leading-none',
                currentPlayer === 'X'
                  ? 'border-cyan-200/60 bg-cyan-400/10 text-cyan-100 shadow-[0_0_28px_rgba(34,211,238,0.35)]'
                  : 'border-fuchsia-200/60 bg-fuchsia-400/10 text-fuchsia-100 shadow-[0_0_28px_rgba(217,70,239,0.35)]',
              ].join(' ')}
            >
              {currentPlayer === 'O' ? '0' : currentPlayer}
            </span>
            <div>
              <p className="text-[0.65rem] uppercase tracking-[0.28em] text-cyan-200/70">Current Turn</p>
              <p className="font-display text-2xl font-bold text-white">Player {currentPlayer === 'O' ? '0' : currentPlayer}</p>
              <p className="text-sm text-slate-400">Turn {turn}/{DRAW_TURN_LIMIT}</p>
            </div>
          </div>
          <Activity className="hidden text-cyan-200 sm:block" />
        </div>

        <div className="mt-4 rounded-2xl border border-white/10 bg-white/[0.03] p-3">
          <div className="mb-2 flex items-center justify-between text-sm text-slate-300">
            <span>Actions</span>
            <span className="font-semibold text-cyan-100">
              {actionPoints}/{maxActionPoints}
            </span>
          </div>
          <div className="grid gap-2" style={{ gridTemplateColumns: `repeat(${maxActionPoints}, minmax(0, 1fr))` }}>
            {Array.from({ length: maxActionPoints }, (_, index) => (
              <span
                key={index}
                className={[
                  'h-3 rounded-full transition-all duration-300',
                  index < actionPoints
                    ? 'bg-gradient-to-r from-cyan-300 to-fuchsia-300 shadow-[0_0_18px_rgba(34,211,238,0.7)]'
                    : 'bg-slate-800',
                ].join(' ')}
              />
            ))}
          </div>
        </div>

        <div className="mt-3 grid grid-cols-2 gap-2 text-sm">
          <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-3">
            <p className="text-slate-400">Board</p>
            <p className="font-display text-xl font-bold text-white">{activeBoardSize}x{activeBoardSize}</p>
          </div>
          <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-3">
            <p className="text-slate-400">Draw Turn</p>
            <p className="font-display text-xl font-bold text-white">{turn}/{DRAW_TURN_LIMIT}</p>
          </div>
        </div>
      </div>

      <div className="rounded-3xl border border-fuchsia-300/20 bg-slate-950/70 p-4 shadow-violet backdrop-blur-xl">
        <div className="flex items-start gap-3">
          <Crosshair className="mt-1 shrink-0 text-fuchsia-200" />
          <div>
            <p className="text-[0.65rem] uppercase tracking-[0.28em] text-fuchsia-200/70">Victory Protocol</p>
            <h2 className="mt-1 font-display text-xl font-bold text-white">{victoryCondition.title}</h2>
            <p className="text-sm font-semibold text-cyan-100">{victoryCondition.short}</p>
            <p className="mt-2 text-sm leading-5 text-slate-300">{victoryCondition.description}</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-2">
        <button
          type="button"
          onClick={onOpenHints}
          className="flex items-center justify-center gap-2 rounded-2xl border border-fuchsia-300/40 bg-fuchsia-300/10 px-4 py-3 font-display text-sm font-bold uppercase tracking-[0.14em] text-fuchsia-100 transition hover:-translate-y-0.5 hover:bg-fuchsia-300/20 hover:shadow-violet focus:outline-none focus:ring-2 focus:ring-fuchsia-200"
        >
          <HelpCircle size={17} /> Hints
        </button>
        <button
          type="button"
          onClick={onRestart}
          className="flex items-center justify-center gap-2 rounded-2xl border border-cyan-300/40 bg-cyan-300/10 px-4 py-3 font-display text-sm font-bold uppercase tracking-[0.14em] text-cyan-100 transition hover:-translate-y-0.5 hover:bg-cyan-300/20 hover:shadow-neon focus:outline-none focus:ring-2 focus:ring-cyan-200"
        >
          <RefreshCw size={17} /> Restart
        </button>
      </div>
    </aside>
  );
}
