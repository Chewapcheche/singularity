import { AnomalyLegend } from './components/AnomalyLegend';
import { EventLog } from './components/EventLog';
import { GameBoard } from './components/GameBoard';
import { StatusPanel } from './components/StatusPanel';
import { VictoryOverlay } from './components/VictoryOverlay';
import { useGameStore } from './store/useGameStore';

function App() {
  const {
    board,
    selectedCellId,
    validMoveIds,
    currentPlayer,
    actionPoints,
    turn,
    victoryCondition,
    events,
    winner,
    selectCell,
    resetGame,
  } = useGameStore();

  return (
    <main className="min-h-screen overflow-hidden bg-slate-950 text-slate-100">
      <div className="pointer-events-none fixed inset-0 bg-[radial-gradient(circle_at_15%_10%,rgba(34,211,238,0.2),transparent_28%),radial-gradient(circle_at_85%_20%,rgba(217,70,239,0.16),transparent_30%),linear-gradient(135deg,rgba(15,23,42,0.9),rgba(2,6,23,1))]" />
      <div className="pointer-events-none fixed inset-0 opacity-[0.14] [background-image:linear-gradient(rgba(255,255,255,0.08)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.08)_1px,transparent_1px)] [background-size:42px_42px]" />

      <div className="relative z-10 mx-auto flex min-h-screen max-w-7xl flex-col gap-6 px-4 py-6 sm:px-6 lg:px-8">
        <header className="flex flex-col justify-between gap-4 rounded-[2rem] border border-white/10 bg-white/[0.035] p-5 backdrop-blur-xl md:flex-row md:items-end">
          <div>
            <p className="text-xs uppercase tracking-[0.5em] text-cyan-200/75">Local tactical prototype</p>
            <h1 className="mt-2 font-display text-4xl font-black tracking-tight text-white md:text-6xl">
              Singularity <span className="text-cyan-200 drop-shadow-[0_0_20px_rgba(34,211,238,0.7)]">Fractures</span>
            </h1>
            <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-300 md:text-base">
              A 6x6 neon battle grid where X and O spend action points to place, move, and weaponize unstable anomalies.
            </p>
          </div>
          <div className="rounded-2xl border border-fuchsia-300/25 bg-fuchsia-300/10 px-4 py-3 text-sm text-fuchsia-100 shadow-violet">
            Two players, one device. Hot-seat ready.
          </div>
        </header>

        <div className="grid flex-1 gap-6 lg:grid-cols-[minmax(0,1fr)_360px]">
          <div className="space-y-5">
            <GameBoard
              board={board}
              selectedCellId={selectedCellId}
              validMoveIds={validMoveIds}
              currentPlayer={currentPlayer}
              onSelectCell={selectCell}
            />
            <AnomalyLegend />
          </div>
          <div className="space-y-5">
            <StatusPanel
              currentPlayer={currentPlayer}
              actionPoints={actionPoints}
              turn={turn}
              victoryCondition={victoryCondition}
              onRestart={resetGame}
            />
            <EventLog events={events} />
          </div>
        </div>
      </div>

      <VictoryOverlay winner={winner} onRestart={resetGame} />
    </main>
  );
}

export default App;
