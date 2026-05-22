"""Map geometry — ground, path tiles, build markers."""

from ursina import Entity, Vec3, color, destroy

from game.config import CELL, GRID_H, GRID_W, MAP_OFFSET, PATH_CELLS
from game.path import grid_to_world


def _cell_color(gx: int, gz: int) -> color:
    if (gx, gz) in PATH_CELLS:
        return color.rgb(0.35, 0.28, 0.22)
    return color.rgb(0.2, 0.55, 0.25) if (gx + gz) % 2 == 0 else color.rgb(0.18, 0.48, 0.22)


class GameWorld:
    def __init__(self):
        self.entities: list[Entity] = []
        ox, _, oz = MAP_OFFSET
        w = GRID_W * CELL
        h = GRID_H * CELL

        ground = Entity(
            model="plane",
            scale=(w + 2, 1, h + 2),
            position=Vec3(0, 0, 0),
            color=color.rgb(0.12, 0.35, 0.15),
            texture="white_cube",
            collider="box",
        )
        self.entities.append(ground)

        for gx in range(GRID_W):
            for gz in range(GRID_H):
                tile = Entity(
                    model="cube",
                    position=grid_to_world(gx, gz) - Vec3(0, 0.08, 0),
                    scale=(CELL * 0.96, 0.12, CELL * 0.96),
                    color=_cell_color(gx, gz),
                    collider=None,
                )
                self.entities.append(tile)

        # Spawn / end markers
        from game.config import PATH_WAYPOINTS

        start = Vec3(*PATH_WAYPOINTS[0])
        end = Vec3(*PATH_WAYPOINTS[-1])
        for pos, col, label in (
            (start, color.azure, "Spawn"),
            (end, color.red, "Core"),
        ):
            marker = Entity(
                model="sphere",
                position=pos + Vec3(0, 0.25, 0),
                scale=0.5,
                color=col,
            )
            self.entities.append(marker)

        # Border walls (volume)
        for edge in (
            (Vec3(-w / 2 - 0.5, 0.4, 0), (0.3, 0.8, h + 1)),
            (Vec3(w / 2 + 0.5, 0.4, 0), (0.3, 0.8, h + 1)),
            (Vec3(0, 0.4, -h / 2 - 0.5), (w + 1, 0.8, 0.3)),
            (Vec3(0, 0.4, h / 2 + 0.5), (w + 1, 0.8, 0.3)),
        ):
            wall = Entity(model="cube", position=edge[0], scale=edge[1], color=color.gray)
            self.entities.append(wall)

    def destroy_all(self):
        for e in self.entities:
            if e:
                destroy(e)
        self.entities.clear()
