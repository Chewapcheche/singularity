"""Level data, tower types, creep types, and balance."""

from dataclasses import dataclass, field
from typing import List, Tuple

# Grid: build tiles exclude path cells
GRID_W, GRID_H = 14, 10
CELL = 1.0
MAP_OFFSET = (-GRID_W * CELL / 2, 0, -GRID_H * CELL / 2)

# Path waypoints (world coords, y=0) — serpentine across map
PATH_WAYPOINTS: List[Tuple[float, float, float]] = [
    (-5.5, 0, -4.0),
    (-5.5, 0, 0.0),
    (-2.0, 0, 0.0),
    (-2.0, 0, 3.5),
    (2.0, 0, 3.5),
    (2.0, 0, 0.0),
    (5.5, 0, 0.0),
    (5.5, 0, -4.0),
]

# Cells occupied by path (grid coords)
PATH_CELLS = {
    (1, 1), (1, 2), (1, 3), (1, 4), (1, 5),
    (2, 5), (3, 5), (4, 5), (5, 5), (6, 5), (7, 5),
    (7, 4), (7, 3), (7, 2),
    (8, 2), (9, 2), (10, 2), (11, 2), (12, 2),
    (12, 3), (12, 4), (12, 5), (12, 6), (12, 7), (12, 8),
}


@dataclass(frozen=True)
class TowerType:
    id: str
    name: str
    place_cost: int
    damage: float
    range: float
    attack_rate: float
    color: Tuple[int, int, int]
    accent: Tuple[int, int, int]
    model_scale: float = 0.55


TOWER_TYPES = {
    "pikachu": TowerType(
        "pikachu", "Pikachu", 20, 12, 3.2, 0.45,
        (255, 220, 60), (180, 140, 20),
    ),
    "charmander": TowerType(
        "charmander", "Charmander", 28, 18, 2.8, 0.7,
        (255, 120, 50), (200, 60, 20),
    ),
    "squirtle": TowerType(
        "squirtle", "Squirtle", 26, 10, 3.0, 0.55,
        (80, 160, 255), (40, 80, 180),
    ),
    "bulbasaur": TowerType(
        "bulbasaur", "Bulbasaur", 24, 8, 3.5, 0.5,
        (100, 200, 90), (50, 120, 40),
    ),
    "snorlax": TowerType(
        "snorlax", "Snorlax", 35, 28, 2.2, 1.1,
        (120, 130, 150), (70, 75, 90), 0.75,
    ),
}

UPGRADE_COSTS = (15, 30, 50)
MAX_TOWER_LEVEL = 4


@dataclass(frozen=True)
class CreepType:
    id: str
    name: str
    base_hp: float
    base_speed: float
    xp_reward: int
    color: Tuple[int, int, int]
    scale: float = 0.4


CREEP_TYPES = {
    "melee": CreepType("melee", "Melee Creep", 40, 1.0, 6, (180, 140, 90)),
    "ranged": CreepType("ranged", "Ranged Creep", 32, 1.15, 8, (140, 100, 70), 0.38),
    "siege": CreepType("siege", "Siege Creep", 90, 0.65, 14, (100, 90, 110), 0.5),
    "super": CreepType("super", "Super Creep", 120, 0.85, 20, (200, 60, 60), 0.48),
    "ancient": CreepType("ancient", "Ancient Creep", 200, 0.55, 35, (80, 40, 120), 0.6),
}


@dataclass
class WaveSpec:
    creep_id: str
    count: int
    spawn_delay: float = 0.65


@dataclass
class LevelSpec:
    index: int
    name: str
    waves: List[List[WaveSpec]]
    hp_mult: float = 1.0
    speed_mult: float = 1.0
    xp_bonus: int = 0
    start_xp: int = 45
    lives: int = 20


def _wave(*entries: Tuple[str, int, float]) -> List[WaveSpec]:
    return [WaveSpec(c, n, d) for c, n, d in entries]


LEVELS: List[LevelSpec] = [
    # Level 1 — tutorial easy, exactly 3 waves
    LevelSpec(1, "Route 1", [
        _wave(("melee", 4, 0.8)),
        _wave(("melee", 5, 0.7), ("ranged", 2, 1.0)),
        _wave(("melee", 6, 0.65), ("ranged", 3, 0.9)),
    ], hp_mult=0.7, speed_mult=0.85, start_xp=55, lives=25),
    # Level 2 — still easy
    LevelSpec(2, "Viridian Path", [
        _wave(("melee", 5, 0.75)),
        _wave(("melee", 4, 0.7), ("ranged", 4, 0.85)),
        _wave(("ranged", 6, 0.7), ("siege", 1, 1.5)),
        _wave(("melee", 8, 0.6)),
    ], hp_mult=0.85, speed_mult=0.9, start_xp=50, lives=22),
    LevelSpec(3, "Cerulean Lane", [
        _wave(("melee", 6, 0.7)),
        _wave(("ranged", 5, 0.65), ("melee", 4, 0.7)),
        _wave(("siege", 2, 1.2), ("melee", 6, 0.6)),
        _wave(("ranged", 8, 0.55)),
    ], hp_mult=1.0, speed_mult=1.0, start_xp=45),
    LevelSpec(4, "Rock Tunnel", [
        _wave(("melee", 8, 0.65)),
        _wave(("ranged", 6, 0.6), ("siege", 2, 1.0)),
        _wave(("super", 2, 1.3), ("melee", 6, 0.55)),
        _wave(("ranged", 10, 0.5)),
    ], hp_mult=1.15, speed_mult=1.05),
    LevelSpec(5, "Lavender Crossing", [
        _wave(("ranged", 8, 0.6)),
        _wave(("siege", 3, 1.0), ("melee", 8, 0.55)),
        _wave(("super", 3, 1.1)),
        _wave(("ancient", 1, 2.0), ("melee", 6, 0.5)),
    ], hp_mult=1.25, speed_mult=1.08),
    LevelSpec(6, "Seafoam Gauntlet", [
        _wave(("melee", 10, 0.55)),
        _wave(("ranged", 10, 0.5)),
        _wave(("siege", 4, 0.9), ("super", 2, 1.0)),
        _wave(("super", 4, 0.85)),
    ], hp_mult=1.35, speed_mult=1.1),
    LevelSpec(7, "Cinnabar Siege", [
        _wave(("siege", 4, 0.85)),
        _wave(("super", 5, 0.75)),
        _wave(("ancient", 2, 1.5), ("ranged", 8, 0.5)),
        _wave(("melee", 12, 0.45)),
    ], hp_mult=1.45, speed_mult=1.12),
    LevelSpec(8, "Indigo Plateau", [
        _wave(("ranged", 12, 0.48)),
        _wave(("super", 6, 0.7)),
        _wave(("ancient", 3, 1.2), ("siege", 4, 0.8)),
        _wave(("super", 8, 0.6)),
    ], hp_mult=1.55, speed_mult=1.15),
    LevelSpec(9, "Champion Road", [
        _wave(("siege", 5, 0.75)),
        _wave(("super", 8, 0.65)),
        _wave(("ancient", 4, 1.0)),
        _wave(("super", 6, 0.55), ("ancient", 2, 1.2)),
    ], hp_mult=1.7, speed_mult=1.18),
    LevelSpec(10, "Master League", [
        _wave(("melee", 14, 0.42)),
        _wave(("ranged", 14, 0.4)),
        _wave(("ancient", 5, 0.9), ("super", 6, 0.55)),
        _wave(("ancient", 4, 0.85), ("siege", 6, 0.7)),
        _wave(("ancient", 3, 1.0), ("super", 10, 0.45)),
    ], hp_mult=1.9, speed_mult=1.22, xp_bonus=2),
]

TOTAL_LEVELS = len(LEVELS)
