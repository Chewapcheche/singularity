import { Activity, BadgeInfo, Crosshair, RefreshCw, Shield } from 'lucide-react';
import type { Player, VictoryCondition } from '../types';

interface StatusPanelProps {
  currentPlayer: Player;
  actionPoints: number;
  maxActionPoints: number;
  turn: number;
  victoryCondition: VictoryCondition;
  onRestart: () => void;
}

export function StatusPanel({
  currentPlayer,
  actionPoints,
  maxActionPoints,
  turn,
  victoryCondition,
  onRestart,
}: StatusPanelProps) {
  return (
    <aside className="space-y-4">
      <div className="rounded-3xl border border-cyan-300/20 bg-slate-950/65 p-5 shadow-neon backdrop-blur-xl">
        <div className="mb-4 flex items-center justify-between gap-3">
          <div>
            <p className="text-xs uppercase tracking-[0.34em] text-cyan-200/70">Active Operative</p>
            <div className="mt-2 flex items-center gap-3">
              <span
                className={[
                  'grid h-14 w-14 place-items-center rounded-2xl border font-display text-3xl font-black',
                  currentPlayer === 'X'
                    ? 'border-cyan-200/60 bg-cyan-400/10 text-cyan-100 shadow-[0_0_28px_rgba(34,211,238,0.35)]'
                    : 'border-fuchsia-200/60 bg-fuchsia-400/10 text-fuchsia-100 shadow-[0_0_28px_rgba(217,70,239,0.35)]',
                ].join(' ')}
              >
                {currentPlayer}
              </span>
              <div>
                <p className="font-display text-2xl font-bold text-white">Player {currentPlayer}</p>
                <p className="text-sm text-slate-400">Turn cycle {turn}</p>
              </div>
            </div>
          </div>
          <Activity className="text-cyan-200" />
        </div>

        <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
          <div className="mb-3 flex items-center justify-between text-sm text-slate-300">
            <span>Action Points</span>
            <span>
              {actionPoints}/{maxActionPoints}
            </span>
          </div>
          <div className="grid grid-cols-2 gap-3">
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
      </div>

      <div className="rounded-3xl border border-fuchsia-300/20 bg-slate-950/65 p-5 shadow-violet backdrop-blur-xl">
        <div className="flex items-start gap-3">
          <Crosshair className="mt-1 text-fuchsia-200" />
          <div>
            <p className="text-xs uppercase tracking-[0.34em] text-fuchsia-200/70">Victory Protocol</p>
            <h2 className="mt-2 font-display text-2xl font-bold text-white">{victoryCondition.title}</h2>
            <p className="mt-1 text-sm font-semibold text-cyan-100">{victoryCondition.short}</p>
            <p className="mt-3 text-sm leading-6 text-slate-300">{victoryCondition.description}</p>
          </div>
        </div>
      </div>

      <div className="rounded-3xl border border-white/10 bg-slate-950/65 p-5 backdrop-blur-xl">
        <div className="mb-3 flex items-center gap-2 text-sm font-semibold uppercase tracking-[0.24em] text-slate-300">
          <BadgeInfo size={16} /> Command Rules
        </div>
        <ul className="space-y-2 text-sm leading-6 text-slate-400">
          <li className="flex gap-2"><Shield size={16} className="mt-1 text-cyan-200" /> Turn 1 grants X 1 AP; every later turn grants 2 AP.</li>
          <li className="flex gap-2"><Shield size={16} className="mt-1 text-cyan-200" /> Place a marker: 1 AP.</li>
          <li className="flex gap-2"><Shield size={16} className="mt-1 text-fuchsia-200" /> Select your marker, then move to a glowing adjacent cell: 1 AP.</li>
          <li className="flex gap-2"><Shield size={16} className="mt-1 text-emerald-200" /> Click your marker on an anomaly to activate it: 1 AP.</li>
        </ul>
      </div>

      <button
        type="button"
        onClick={onRestart}
        className="flex w-full items-center justify-center gap-2 rounded-2xl border border-cyan-300/40 bg-cyan-300/10 px-5 py-3 font-display font-bold uppercase tracking-[0.2em] text-cyan-100 transition hover:-translate-y-0.5 hover:bg-cyan-300/20 hover:shadow-neon focus:outline-none focus:ring-2 focus:ring-cyan-200"
      >
        <RefreshCw size={18} /> Restart Game
      </button>
    </aside>
  );
}
