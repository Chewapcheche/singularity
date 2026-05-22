import { useState } from 'react';
import { GameBoard } from './components/GameBoard';
import { HintsModal } from './components/HintsModal';
import { StatusPanel } from './components/StatusPanel';
import { VictoryOverlay } from './components/VictoryOverlay';
import { useGameStore } from './store/useGameStore';
import { getActionPointsForTurn } from './types';

function App() {
  const [isHintsOpen, setIsHintsOpen] = useState(false);
  const {
    board,
    activeBoardSize,
    selectedCellId,
    currentPlayer,
    actionPoints,
    turn,
    victoryCondition,
    winner,
    draw,
    selectCell,
    resetGame,
  } = useGameStore();
  const maxActionPoints = getActionPointsForTurn(turn);

  return (
    <main className="h-dvh max-h-dvh overflow-hidden bg-slate-950 text-slate-100">
      <div className="pointer-events-none fixed inset-0 bg-[radial-gradient(circle_at_15%_10%,rgba(34,211,238,0.2),transparent_28%),radial-gradient(circle_at_85%_20%,rgba(217,70,239,0.16),transparent_30%),linear-gradient(135deg,rgba(15,23,42,0.9),rgba(2,6,23,1))]" />
      <div className="pointer-events-none fixed inset-0 opacity-[0.14] [background-image:linear-gradient(rgba(255,255,255,0.08)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.08)_1px,transparent_1px)] [background-size:42px_42px]" />

      <div className="relative z-10 mx-auto grid h-full max-w-[1500px] grid-rows-[auto_minmax(0,1fr)] gap-3 px-3 py-3 sm:px-4">
        <header className="flex shrink-0 flex-col justify-between gap-2 rounded-[1.5rem] border border-white/10 bg-white/[0.035] px-4 py-3 backdrop-blur-xl md:flex-row md:items-end">
          <div>
            <p className="text-[0.65rem] uppercase tracking-[0.42em] text-cyan-200/75">Local tactical prototype</p>
            <h1 className="mt-1 font-display text-3xl font-black tracking-tight text-white md:text-5xl">
              Singularity <span className="text-cyan-200 drop-shadow-[0_0_20px_rgba(34,211,238,0.7)]">Fractures</span>
            </h1>
          </div>
          <div className="rounded-2xl border border-fuchsia-300/25 bg-fuchsia-300/10 px-3 py-2 text-sm text-fuchsia-100 shadow-violet">
            4x4 to 6x6 fracture grid. Draw on Turn 17.
          </div>
        </header>

        <div className="grid min-h-0 items-stretch gap-3 lg:grid-cols-[minmax(0,1fr)_minmax(300px,360px)]">
          <div className="flex min-h-0 items-center justify-start">
            <GameBoard
              board={board}
              activeBoardSize={activeBoardSize}
              selectedCellId={selectedCellId}
              currentPlayer={currentPlayer}
              onSelectCell={selectCell}
            />
          </div>
          <div className="flex min-h-0 items-start justify-stretch overflow-hidden">
            <StatusPanel
              currentPlayer={currentPlayer}
              actionPoints={actionPoints}
              maxActionPoints={maxActionPoints}
              turn={turn}
              activeBoardSize={activeBoardSize}
              victoryCondition={victoryCondition}
              onOpenHints={() => setIsHintsOpen(true)}
              onRestart={resetGame}
            />
          </div>
        </div>
      </div>

      <HintsModal isOpen={isHintsOpen} onClose={() => setIsHintsOpen(false)} />
      <VictoryOverlay winner={winner} draw={draw} onRestart={resetGame} />
    </main>
  );
}

export default App;
