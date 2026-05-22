import { Copy, Orbit, Shield, X, Zap } from 'lucide-react';
import { anomalyDescriptions } from '../engine/gameEngine';
import { DRAW_MOVE_LIMIT } from '../types';

interface HintsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function HintsModal({ isOpen, onClose }: HintsModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-40 grid place-items-center bg-slate-950/80 p-4 backdrop-blur-md">
      <div className="relative w-full max-w-3xl overflow-hidden rounded-[2rem] border border-cyan-200/30 bg-slate-950 p-5 shadow-[0_0_90px_rgba(34,211,238,0.28)]">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,rgba(34,211,238,0.16),transparent_38%),radial-gradient(circle_at_bottom,rgba(217,70,239,0.13),transparent_42%)]" />
        <div className="relative z-10">
          <div className="mb-4 flex items-start justify-between gap-4">
            <div>
              <p className="text-xs uppercase tracking-[0.4em] text-cyan-100/75">Command Hints</p>
              <h2 className="mt-2 font-display text-3xl font-black text-white">Fracture Protocols</h2>
            </div>
            <button
              type="button"
              onClick={onClose}
              className="rounded-full border border-white/15 bg-white/5 p-2 text-slate-200 transition hover:bg-white/10 focus:outline-none focus:ring-2 focus:ring-cyan-200"
              aria-label="Close hints"
            >
              <X size={20} />
            </button>
          </div>

          <div className="grid gap-3 md:grid-cols-2">
            <section className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
              <h3 className="mb-3 font-display text-lg font-bold text-cyan-100">Turn Rules</h3>
              <ul className="space-y-2 text-sm leading-5 text-slate-300">
                <li className="flex gap-2"><Shield size={16} className="mt-0.5 shrink-0 text-cyan-200" /> X starts with 1 action. Every later turn gives 2 actions.</li>
                <li className="flex gap-2"><Shield size={16} className="mt-0.5 shrink-0 text-fuchsia-200" /> Pieces cannot be moved or dragged after placement.</li>
                <li className="flex gap-2"><Shield size={16} className="mt-0.5 shrink-0 text-emerald-200" /> Adjacent placement is allowed except Player 0 cannot place next to another 0 on their second move.</li>
                <li className="flex gap-2"><Shield size={16} className="mt-0.5 shrink-0 text-amber-200" /> The board starts 4x4, expands after moves 4 and 7, and draws after move {DRAW_MOVE_LIMIT}.</li>
              </ul>
            </section>

            <section className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
              <h3 className="mb-3 font-display text-lg font-bold text-fuchsia-100">Anomalies</h3>
              <div className="space-y-3 text-sm leading-5 text-slate-300">
                <div className="flex gap-2"><Orbit size={17} className="mt-0.5 shrink-0 text-cyan-200" /><span><b className="text-cyan-100">{anomalyDescriptions.teleport.label}:</b> {anomalyDescriptions.teleport.description}</span></div>
                <div className="flex gap-2"><Zap size={17} className="mt-0.5 shrink-0 text-rose-200" /><span><b className="text-rose-100">{anomalyDescriptions.destroy.label}:</b> {anomalyDescriptions.destroy.description}</span></div>
                <div className="flex gap-2"><Copy size={17} className="mt-0.5 shrink-0 text-emerald-200" /><span><b className="text-emerald-100">{anomalyDescriptions.clone.label}:</b> {anomalyDescriptions.clone.description}</span></div>
              </div>
            </section>
          </div>
        </div>
      </div>
    </div>
  );
}
