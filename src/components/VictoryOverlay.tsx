import { Crown, RefreshCw } from 'lucide-react';
import type { Winner } from '../types';

interface VictoryOverlayProps {
  winner: Winner | null;
  onRestart: () => void;
}

export function VictoryOverlay({ winner, onRestart }: VictoryOverlayProps) {
  if (!winner) return null;

  return (
    <div className="fixed inset-0 z-50 grid place-items-center bg-slate-950/80 p-6 backdrop-blur-md">
      <div className="relative w-full max-w-xl overflow-hidden rounded-[2rem] border border-cyan-200/30 bg-slate-950 p-8 text-center shadow-[0_0_90px_rgba(34,211,238,0.35)]">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,rgba(34,211,238,0.2),transparent_38%),radial-gradient(circle_at_bottom,rgba(217,70,239,0.16),transparent_42%)]" />
        <div className="relative z-10">
          <div className="mx-auto mb-5 grid h-20 w-20 place-items-center rounded-full border border-fuchsia-200/50 bg-fuchsia-300/10 text-fuchsia-100 shadow-violet">
            <Crown size={38} />
          </div>
          <p className="text-xs uppercase tracking-[0.45em] text-cyan-100/80">Fracture Stabilized</p>
          <h2 className="mt-4 font-display text-5xl font-black text-white">Player {winner.player} Wins</h2>
          <p className="mt-4 text-lg text-slate-300">{winner.message}</p>
          <p className="mt-2 text-sm text-cyan-100">Protocol: {winner.condition.title}</p>
          <button
            type="button"
            onClick={onRestart}
            className="mt-8 inline-flex items-center justify-center gap-2 rounded-2xl border border-cyan-300/40 bg-cyan-300/10 px-6 py-3 font-display font-bold uppercase tracking-[0.2em] text-cyan-100 transition hover:-translate-y-0.5 hover:bg-cyan-300/20 hover:shadow-neon focus:outline-none focus:ring-2 focus:ring-cyan-200"
          >
            <RefreshCw size={18} /> Restart Game
          </button>
        </div>
      </div>
    </div>
  );
}
