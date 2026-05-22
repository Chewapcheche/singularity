"""Path sampling and grid helpers."""

from typing import List, Tuple

from ursina import Vec3

from game.config import CELL, GRID_H, GRID_W, MAP_OFFSET, PATH_CELLS, PATH_WAYPOINTS


def grid_to_world(gx: int, gz: int) -> Vec3:
    ox, _, oz = MAP_OFFSET
    return Vec3(ox + (gx + 0.5) * CELL, 0.15, oz + (gz + 0.5) * CELL)


def world_to_grid(pos: Vec3) -> Tuple[int, int]:
    ox, _, oz = MAP_OFFSET
    gx = int((pos.x - ox) / CELL)
    gz = int((pos.z - oz) / CELL)
    return gx, gz


def can_build(gx: int, gz: int) -> bool:
    if gx < 0 or gz < 0 or gx >= GRID_W or gz >= GRID_H:
        return False
    return (gx, gz) not in PATH_CELLS


def build_path_segments() -> Tuple[List[Vec3], List[float]]:
    """Return waypoint list and cumulative distances for arc-length movement."""
    points = [Vec3(*p) for p in PATH_WAYPOINTS]
    seg_lens: List[float] = []
    total = 0.0
    for i in range(len(points) - 1):
        d = (points[i + 1] - points[i]).length()
        seg_lens.append(d)
        total += d
    return points, seg_lens


def position_on_path(points: List[Vec3], seg_lens: List[float], dist: float) -> Vec3:
    if dist <= 0:
        return points[0]
    traveled = 0.0
    for i, seg in enumerate(seg_lens):
        if traveled + seg >= dist:
            t = (dist - traveled) / seg if seg > 0 else 0
            return points[i].lerp(points[i + 1], t)
        traveled += seg
    return points[-1]


def path_total_length(seg_lens: List[float]) -> float:
    return sum(seg_lens)
