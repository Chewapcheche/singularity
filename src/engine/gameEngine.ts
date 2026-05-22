import {
  BOARD_SIZE,
  DRAW_TURN_LIMIT,
  INITIAL_BOARD_SIZE,
  getActionPointsForTurn,
  getBoardSizeForTurn,
  type Anomaly,
  type AnomalyType,
  type Board,
  type Cell,
  type Coordinate,
  type DrawState,
  type GameEvent,
  type GameState,
  type Player,
  type VictoryCondition,
  type VictoryConditionType,
  type Winner,
} from '../types';

const VICTORY_CONDITIONS: Record<VictoryConditionType, VictoryCondition> = {
  classic: {
    type: 'classic',
    title: 'Classic Vector',
    short: '4 in a row',
    description: 'Create a horizontal or vertical line of four of your symbols.',
  },
  square: {
    type: 'square',
    title: 'Quantum Square',
    short: '2x2 block',
    description: 'Form a 2x2 square using only your symbols.',
  },
  diagonal: {
    type: 'diagonal',
    title: 'Singularity Diagonal',
    short: 'Diagonal 4',
    description: 'Create a diagonal line of four of your symbols.',
  },
  encirclement: {
    type: 'encirclement',
    title: 'Gravity Well',
    short: 'Surround enemy',
    description: 'Surround at least one enemy piece on all four orthogonal sides.',
  },
};

const ANOMALY_TYPES: AnomalyType[] = ['teleport', 'destroy', 'clone'];
const MAX_EVENTS = 9;
const MAX_ANOMALIES = 6;

const randomId = (prefix: string) => `${prefix}-${Math.random().toString(36).slice(2, 9)}`;

const cloneBoard = (board: Board): Board =>
  board.map((row) => row.map((cell) => ({ ...cell, anomaly: cell.anomaly ? { ...cell.anomaly } : null })));

const createEmptyBoard = (): Board =>
  Array.from({ length: BOARD_SIZE }, (_, row) =>
    Array.from({ length: BOARD_SIZE }, (_, col) => ({
      id: `${row}-${col}`,
      row,
      col,
      piece: null,
      anomaly: null,
    })),
  );

const randomItem = <T,>(items: T[]): T => items[Math.floor(Math.random() * items.length)];

export const victoryConditions = Object.values(VICTORY_CONDITIONS);

export const anomalyDescriptions: Record<AnomalyType, { label: string; description: string }> = {
  teleport: {
    label: 'Teleport Rift',
    description: 'Activation jumps the occupying piece to a random free cell.',
  },
  destroy: {
    label: 'Null Pulse',
    description: 'Activation deletes the occupying piece from the board.',
  },
  clone: {
    label: 'Echo Forge',
    description: 'Activation copies the occupying piece into a nearby free cell if possible.',
  },
};

export const getOpponent = (player: Player): Player => (player === 'X' ? 'O' : 'X');

export const getCell = (board: Board, id: string | null): Cell | null => {
  if (!id) return null;
  const [row, col] = id.split('-').map(Number);
  if (!Number.isInteger(row) || !Number.isInteger(col)) return null;
  return board[row]?.[col] ?? null;
};

export const isInsideBoard = ({ row, col }: Coordinate): boolean =>
  row >= 0 && row < BOARD_SIZE && col >= 0 && col < BOARD_SIZE;

export const isInsideActiveBoard = ({ row, col }: Coordinate, activeBoardSize: number): boolean =>
  row >= 0 && row < activeBoardSize && col >= 0 && col < activeBoardSize;

export const getAdjacentCoordinates = (cell: Coordinate, includeDiagonals = true): Coordinate[] => {
  const deltas = includeDiagonals
    ? [-1, 0, 1].flatMap((row) => [-1, 0, 1].map((col) => ({ row, col })))
    : [
        { row: -1, col: 0 },
        { row: 1, col: 0 },
        { row: 0, col: -1 },
        { row: 0, col: 1 },
      ];

  return deltas
    .filter((delta) => delta.row !== 0 || delta.col !== 0)
    .map((delta) => ({ row: cell.row + delta.row, col: cell.col + delta.col }))
    .filter(isInsideBoard);
};

export const createGameEvent = (turn: number, message: string, tone: GameEvent['tone'] = 'system'): GameEvent => ({
  id: randomId('event'),
  turn,
  message,
  tone,
});

export const addEvent = (events: GameEvent[], event: GameEvent): GameEvent[] => [event, ...events].slice(0, MAX_EVENTS);

const getActiveCells = (board: Board, activeBoardSize: number): Cell[] =>
  board.flat().filter((cell) => isInsideActiveBoard(cell, activeBoardSize));

const countAnomalies = (board: Board, activeBoardSize: number): number =>
  getActiveCells(board, activeBoardSize).filter((cell) => cell.anomaly).length;

const getAvailableAnomalyCells = (board: Board, activeBoardSize: number): Cell[] =>
  getActiveCells(board, activeBoardSize).filter((cell) => !cell.piece && !cell.anomaly);

export const spawnAnomaly = (
  board: Board,
  activeBoardSize: number,
): { board: Board; anomaly: Anomaly | null; cell: Cell | null } => {
  if (countAnomalies(board, activeBoardSize) >= MAX_ANOMALIES) {
    return { board, anomaly: null, cell: null };
  }

  const openCells = getAvailableAnomalyCells(board, activeBoardSize);
  if (openCells.length === 0) {
    return { board, anomaly: null, cell: null };
  }

  const nextBoard = cloneBoard(board);
  const target = randomItem(openCells);
  const anomaly: Anomaly = { id: randomId('anomaly'), type: randomItem(ANOMALY_TYPES) };
  nextBoard[target.row][target.col].anomaly = anomaly;

  return { board: nextBoard, anomaly, cell: nextBoard[target.row][target.col] };
};

const seedAnomalies = (board: Board, activeBoardSize: number, amount = 2): Board => {
  let seededBoard = board;
  for (let i = 0; i < amount; i += 1) {
    seededBoard = spawnAnomaly(seededBoard, activeBoardSize).board;
  }
  return seededBoard;
};

const selectVictoryCondition = (): VictoryCondition => randomItem(victoryConditions);

export const createInitialGameState = (): GameState => {
  const victoryCondition = selectVictoryCondition();
  return {
    board: seedAnomalies(createEmptyBoard(), INITIAL_BOARD_SIZE),
    activeBoardSize: INITIAL_BOARD_SIZE,
    currentPlayer: 'X',
    actionPoints: getActionPointsForTurn(1),
    turn: 1,
    completedTurns: 0,
    victoryCondition,
    selectedCellId: null,
    winner: null,
    draw: null,
    events: [
      createGameEvent(
        1,
        `Victory protocol online: ${victoryCondition.title}. ${victoryCondition.description}`,
        'system',
      ),
      createGameEvent(1, 'Initial 4x4 fracture grid is online. It expands on Turns 4 and 7.', 'system'),
      createGameEvent(1, 'Opening initiative: Player X receives 1 AP, then all turns grant 2 AP.', 'system'),
    ],
  };
};

const hasClassicLine = (board: Board, player: Player, activeBoardSize: number): boolean => {
  const directions = [
    { row: 0, col: 1 },
    { row: 1, col: 0 },
  ];
  return hasLine(board, player, directions, activeBoardSize);
};

const hasDiagonalLine = (board: Board, player: Player, activeBoardSize: number): boolean => {
  const directions = [
    { row: 1, col: 1 },
    { row: 1, col: -1 },
  ];
  return hasLine(board, player, directions, activeBoardSize);
};

const hasLine = (board: Board, player: Player, directions: Coordinate[], activeBoardSize: number): boolean =>
  getActiveCells(board, activeBoardSize).some((cell) =>
    directions.some((direction) =>
      Array.from({ length: 4 }, (_, index) => ({
        row: cell.row + direction.row * index,
        col: cell.col + direction.col * index,
      })).every((coord) => isInsideActiveBoard(coord, activeBoardSize) && board[coord.row][coord.col].piece === player),
    ),
  );

const hasSquare = (board: Board, player: Player, activeBoardSize: number): boolean => {
  for (let row = 0; row < activeBoardSize - 1; row += 1) {
    for (let col = 0; col < activeBoardSize - 1; col += 1) {
      if (
        board[row][col].piece === player &&
        board[row + 1][col].piece === player &&
        board[row][col + 1].piece === player &&
        board[row + 1][col + 1].piece === player
      ) {
        return true;
      }
    }
  }

  return false;
};

const hasEncirclement = (board: Board, player: Player, activeBoardSize: number): boolean => {
  const opponent = getOpponent(player);
  return getActiveCells(board, activeBoardSize).some((cell) => {
    if (cell.piece !== opponent) return false;
    const orthogonal = getAdjacentCoordinates(cell, false).filter((coord) => isInsideActiveBoard(coord, activeBoardSize));
    return orthogonal.length === 4 && orthogonal.every(({ row, col }) => board[row][col].piece === player);
  });
};

export const checkVictory = (
  board: Board,
  player: Player,
  condition: VictoryCondition,
  activeBoardSize: number,
): Winner | null => {
  const hasWon =
    condition.type === 'classic'
      ? hasClassicLine(board, player, activeBoardSize)
      : condition.type === 'square'
        ? hasSquare(board, player, activeBoardSize)
        : condition.type === 'diagonal'
          ? hasDiagonalLine(board, player, activeBoardSize)
          : hasEncirclement(board, player, activeBoardSize);

  if (!hasWon) return null;

  return {
    player,
    condition,
    message: `${player} stabilized the fracture through ${condition.title}.`,
  };
};

const hasAdjacentOwnPiece = (board: Board, cell: Cell, player: Player, activeBoardSize: number): boolean =>
  getAdjacentCoordinates(cell, true)
    .filter((coord) => isInsideActiveBoard(coord, activeBoardSize))
    .some(({ row, col }) => board[row][col].piece === player);

const createDrawState = (): DrawState => ({
  message: `Turn ${DRAW_TURN_LIMIT} reached before either side stabilized the fracture.`,
});

const resolveAction = (state: GameState, board: Board, event: GameEvent): GameState => {
  const nextActionPoints = state.actionPoints - 1;
  const winner = checkVictory(board, state.currentPlayer, state.victoryCondition, state.activeBoardSize);
  let nextState: GameState = {
    ...state,
    board,
    actionPoints: nextActionPoints,
    selectedCellId: null,
    winner,
    events: addEvent(state.events, event),
  };

  if (winner) {
    return {
      ...nextState,
      events: addEvent(nextState.events, createGameEvent(state.turn, winner.message, 'victory')),
    };
  }

  if (nextActionPoints <= 0) {
    nextState = endTurn(nextState);
  }

  return nextState;
};

export const endTurn = (state: GameState): GameState => {
  if (state.winner || state.draw) return state;

  const completedTurns = state.completedTurns + 1;
  const nextTurn = state.turn + 1;
  const nextPlayer = getOpponent(state.currentPlayer);
  const nextActiveBoardSize = getBoardSizeForTurn(nextTurn);
  let nextBoard = state.board;
  let events = addEvent(
    state.events,
    createGameEvent(state.turn, `${state.currentPlayer} expended all AP. ${nextPlayer} enters the breach.`, 'system'),
  );

  if (nextActiveBoardSize > state.activeBoardSize) {
    events = addEvent(
      events,
      createGameEvent(
        nextTurn,
        `The fracture expands to a ${nextActiveBoardSize}x${nextActiveBoardSize} board on Turn ${nextTurn}.`,
        'system',
      ),
    );
  }

  const draw = nextTurn >= DRAW_TURN_LIMIT ? createDrawState() : null;

  if (!draw && completedTurns % 2 === 0) {
    const spawned = spawnAnomaly(nextBoard, nextActiveBoardSize);
    nextBoard = spawned.board;
    if (spawned.anomaly && spawned.cell) {
      events = addEvent(
        events,
        createGameEvent(
          nextTurn,
          `${anomalyDescriptions[spawned.anomaly.type].label} appeared at sector ${spawned.cell.row + 1}.${spawned.cell.col + 1}.`,
          'anomaly',
        ),
      );
    }
  }

  const nextState: GameState = {
    ...state,
    board: nextBoard,
    activeBoardSize: nextActiveBoardSize,
    currentPlayer: nextPlayer,
    actionPoints: getActionPointsForTurn(nextTurn),
    turn: nextTurn,
    completedTurns,
    selectedCellId: null,
    draw,
    events,
  };

  if (draw) {
    return {
      ...nextState,
      events: addEvent(nextState.events, createGameEvent(nextTurn, draw.message, 'victory')),
    };
  }

  return nextState;
};

export const placePiece = (state: GameState, cellId: string): GameState => {
  if (state.winner || state.draw || state.actionPoints <= 0) return state;
  const cell = getCell(state.board, cellId);
  if (!cell || cell.piece || !isInsideActiveBoard(cell, state.activeBoardSize)) return state;

  const isPlayerZeroSecondAction = state.currentPlayer === 'O' && state.turn === 2 && state.actionPoints === 1;
  const isAdjacentToOwnPiece = hasAdjacentOwnPiece(state.board, cell, state.currentPlayer, state.activeBoardSize);

  if (isPlayerZeroSecondAction && isAdjacentToOwnPiece) {
    return {
      ...state,
      selectedCellId: null,
      events: addEvent(
        state.events,
        createGameEvent(
          state.turn,
          'Player 0 cannot place next to another 0 on Turn 2.',
          'system',
        ),
      ),
    };
  }

  const board = cloneBoard(state.board);
  board[cell.row][cell.col].piece = state.currentPlayer;
  const anomalyNote = cell.anomaly ? ` on a dormant ${anomalyDescriptions[cell.anomaly.type].label}` : '';

  return resolveAction(
    state,
    board,
    createGameEvent(
      state.turn,
      `${state.currentPlayer} placed a marker at sector ${cell.row + 1}.${cell.col + 1}${anomalyNote}.`,
      'player',
    ),
  );
};

const getRandomEmptyCell = (board: Board, activeBoardSize: number): Cell | null => {
  const cells = getActiveCells(board, activeBoardSize).filter((cell) => !cell.piece);
  return cells.length ? randomItem(cells) : null;
};

const getNearbyFreeCell = (board: Board, origin: Cell, activeBoardSize: number): Cell | null => {
  const freeCells = getAdjacentCoordinates(origin, true)
    .filter((coord) => isInsideActiveBoard(coord, activeBoardSize))
    .map(({ row, col }) => board[row][col])
    .filter((cell) => !cell.piece);
  return freeCells.length ? randomItem(freeCells) : null;
};

export const activateAnomaly = (state: GameState, cellId: string): GameState => {
  if (state.winner || state.draw || state.actionPoints <= 0) return state;

  const cell = getCell(state.board, cellId);
  if (!cell?.anomaly || cell.piece !== state.currentPlayer || !isInsideActiveBoard(cell, state.activeBoardSize)) return state;

  const board = cloneBoard(state.board);
  const target = board[cell.row][cell.col];
  const anomaly = target.anomaly;
  if (!anomaly || !target.piece) return state;

  let message = '';

  if (anomaly.type === 'teleport') {
    target.piece = null;
    target.anomaly = null;
    const destination = getRandomEmptyCell(board, state.activeBoardSize);
    if (destination) {
      board[destination.row][destination.col].piece = state.currentPlayer;
      message = `${state.currentPlayer} triggered Teleport Rift and jumped to sector ${destination.row + 1}.${destination.col + 1}.`;
    } else {
      target.piece = state.currentPlayer;
      message = `${state.currentPlayer} triggered Teleport Rift, but no free sector accepted the jump.`;
    }
  }

  if (anomaly.type === 'destroy') {
    target.piece = null;
    target.anomaly = null;
    message = `${state.currentPlayer} triggered Null Pulse at ${cell.row + 1}.${cell.col + 1}; the marker was erased.`;
  }

  if (anomaly.type === 'clone') {
    target.anomaly = null;
    const cloneCell = getNearbyFreeCell(board, target, state.activeBoardSize);
    if (cloneCell) {
      board[cloneCell.row][cloneCell.col].piece = state.currentPlayer;
      message = `${state.currentPlayer} activated Echo Forge and cloned into sector ${cloneCell.row + 1}.${cloneCell.col + 1}.`;
    } else {
      message = `${state.currentPlayer} activated Echo Forge, but every neighboring sector was occupied.`;
    }
  }

  return resolveAction(state, board, createGameEvent(state.turn, message, 'anomaly'));
};
