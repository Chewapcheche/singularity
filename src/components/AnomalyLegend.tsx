import { Copy, Orbit, Zap, type LucideIcon } from 'lucide-react';
import { anomalyDescriptions } from '../engine/gameEngine';
import type { AnomalyType } from '../types';

const legend: Array<{ type: AnomalyType; icon: LucideIcon; classes: string }> = [
  { type: 'teleport', icon: Orbit, classes: 'border-cyan-300/40 bg-cyan-300/10 text-cyan-100' },
  { type: 'destroy', icon: Zap, classes: 'border-rose-300/40 bg-rose-300/10 text-rose-100' },
  { type: 'clone', icon: Copy, classes: 'border-emerald-300/40 bg-emerald-300/10 text-emerald-100' },
];

export function AnomalyLegend() {
  return (
    <section className="grid gap-3 md:grid-cols-3">
      {legend.map(({ type, icon: Icon, classes }) => (
        <article key={type} title={anomalyDescriptions[type].description} className={`rounded-2xl border p-4 backdrop-blur-xl ${classes}`}>
          <div className="mb-2 flex items-center gap-2 font-display font-bold">
            <Icon size={18} /> {anomalyDescriptions[type].label}
          </div>
          <p className="text-sm leading-5 opacity-80">{anomalyDescriptions[type].description}</p>
        </article>
      ))}
    </section>
  );
}
