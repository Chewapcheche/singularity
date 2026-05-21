import { RadioTower } from 'lucide-react';
import type { GameEvent } from '../types';

interface EventLogProps {
  events: GameEvent[];
}

const toneClasses: Record<GameEvent['tone'], string> = {
  system: 'border-slate-500/30 bg-slate-500/10 text-slate-200',
  player: 'border-cyan-400/30 bg-cyan-400/10 text-cyan-100',
  anomaly: 'border-amber-300/30 bg-amber-300/10 text-amber-100',
  victory: 'border-fuchsia-300/40 bg-fuchsia-300/10 text-fuchsia-100',
};

export function EventLog({ events }: EventLogProps) {
  return (
    <section className="rounded-3xl border border-white/10 bg-slate-950/65 p-5 backdrop-blur-xl">
      <div className="mb-4 flex items-center justify-between">
        <div className="flex items-center gap-2 text-sm font-semibold uppercase tracking-[0.24em] text-slate-300">
          <RadioTower size={16} className="text-cyan-200" /> Recent Events
        </div>
        <span className="rounded-full border border-cyan-300/20 px-3 py-1 text-xs text-cyan-100">Live</span>
      </div>
      <div className="max-h-72 space-y-2 overflow-auto pr-1">
        {events.map((event) => (
          <article key={event.id} className={`rounded-2xl border p-3 text-sm leading-5 ${toneClasses[event.tone]}`}>
            <div className="mb-1 text-[0.65rem] uppercase tracking-[0.22em] opacity-70">Turn {event.turn}</div>
            {event.message}
          </article>
        ))}
      </div>
    </section>
  );
}
