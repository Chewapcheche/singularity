"""3D towers (Pokemon) and creeps (Dota)."""

from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING

from ursina import color, destroy, Entity, lerp, Text, Vec3

from game.config import (
    CREEP_TYPES,
    MAX_TOWER_LEVEL,
    TOWER_TYPES,
    TowerType,
    CreepType,
)
from game.path import grid_to_world, position_on_path

if TYPE_CHECKING:
    from game.waves import WaveController


def _rgb(c: tuple) -> color:
    return color.rgb(c[0] / 255, c[1] / 255, c[2] / 255)


class Projectile(Entity):
    pool: List["Projectile"] = []

    def __init__(self):
        super().__init__(
            model="sphere",
            scale=0.12,
            color=color.azure,
            collider=None,
            enabled=False,
        )
        self.speed = 14.0
        self.damage = 0.0
        self.target: Optional["Creep"] = None
        self._active = False

    @classmethod
    def acquire(cls) -> "Projectile":
        for p in cls.pool:
            if not p._active:
                p._active = True
                p.enabled = True
                return p
        p = cls()
        cls.pool.append(p)
        p._active = True
        p.enabled = True
        return p

    def fire(self, origin: Vec3, target: "Creep", dmg: float, tint):
        self.position = origin + Vec3(0, 0.5, 0)
        self.target = target
        self.damage = dmg
        self.color = tint
        self._active = True
        self.enabled = True

    def update_proj(self, dt: float) -> int:
        """Move projectile; return XP if a creep was killed."""
        if not self._active or not self.target or not self.target.alive:
            self.release()
            return 0
        dest = self.target.position + Vec3(0, 0.35, 0)
        diff = dest - self.position
        dist = diff.length()
        if dist < 0.2:
            reward = self.target.take_damage(self.damage)
            self.release()
            return reward
        self.position += diff.normalized() * min(self.speed * dt, dist)
        return 0

    def release(self):
        self._active = False
        self.enabled = False
        self.target = None


class Creep(Entity):
    def __init__(
        self,
        creep_type: CreepType,
        hp: float,
        speed: float,
        xp: int,
        path_points: List[Vec3],
        seg_lens: List[float],
        path_len: float,
    ):
        self.creep_type = creep_type
        self.max_hp = hp
        self.hp = hp
        self.speed = speed
        self.xp_reward = xp
        self.path_points = path_points
        self.seg_lens = seg_lens
        self.path_len = path_len
        self.path_dist = 0.0
        self.alive = True
        self._flash = 0.0

        body_color = _rgb(creep_type.color)
        super().__init__(
            model="cube",
            position=path_points[0] + Vec3(0, creep_type.scale, 0),
            scale=(creep_type.scale * 1.1, creep_type.scale * 1.4, creep_type.scale),
            color=body_color,
            collider="box",
        )
        self.shader = None
        # "head" for volume
        self.head = Entity(
            parent=self,
            model="sphere",
            y=0.55,
            scale=0.55,
            color=body_color.tint(-0.15),
            collider=None,
        )
        self.label = Text(
            text=creep_type.name.split()[0],
            parent=self,
            y=1.2,
            scale=4,
            origin=(0, 0),
            color=color.white,
            billboard=True,
        )
        self.hp_bar_bg = Entity(
            parent=self,
            model="quad",
            scale=(0.9, 0.08, 1),
            y=1.0,
            color=color.dark_gray,
            billboard=True,
        )
        self.hp_bar = Entity(
            parent=self,
            model="quad",
            scale=(0.88, 0.06, 1),
            y=1.01,
            color=color.red,
            origin=(-0.5, 0),
            billboard=True,
        )

    def take_damage(self, amount: float) -> int:
        """Apply damage; return XP reward if killed."""
        if not self.alive:
            return 0
        self.hp -= amount
        self._flash = 0.12
        ratio = max(0, self.hp / self.max_hp)
        self.hp_bar.scale_x = 0.88 * ratio
        if self.hp <= 0:
            reward = self.xp_reward
            self.die()
            return reward
        return 0

    def die(self):
        self.alive = False
        destroy(self)

    def update_creep(self, dt: float) -> bool:
        """Returns True if reached end."""
        if not self.alive:
            return False
        if self._flash > 0:
            self._flash -= dt
            base = _rgb(self.creep_type.color)
            self.color = lerp(base, color.white, 0.35)
        else:
            self.color = _rgb(self.creep_type.color)

        self.path_dist += self.speed * dt * 1.35
        pos = position_on_path(self.path_points, self.seg_lens, self.path_dist)
        self.position = pos + Vec3(0, self.creep_type.scale, 0)
        if len(self.path_points) > 1:
            ahead = position_on_path(
                self.path_points, self.seg_lens, min(self.path_dist + 0.3, self.path_len)
            )
            self.look_at_2d(ahead, "y")

        if self.path_dist >= self.path_len:
            self.alive = False
            destroy(self)
            return True
        return False


class PokemonTower(Entity):
    def __init__(self, tower_type: TowerType, gx: int, gz: int):
        self.tower_type = tower_type
        self.gx = gx
        self.gz = gz
        self.level = 1
        self.cooldown = 0.0
        pos = grid_to_world(gx, gz)

        base_c = _rgb(tower_type.color)
        accent_c = _rgb(tower_type.accent)
        s = tower_type.model_scale

        super().__init__(
            model="cylinder",
            position=pos,
            scale=(s * 0.9, s * 0.35, s * 0.9),
            color=accent_c,
            collider="box",
        )
        self.body = Entity(
            parent=self,
            model="sphere",
            y=0.55,
            scale=0.85,
            color=base_c,
            collider=None,
        )
        self.ear_l = Entity(
            parent=self.body,
            model="cube",
            position=(-0.35, 0.35, 0),
            scale=(0.2, 0.35, 0.15),
            color=base_c,
            rotation_z=-25,
        )
        self.ear_r = Entity(
            parent=self.body,
            model="cube",
            position=(0.35, 0.35, 0),
            scale=(0.2, 0.35, 0.15),
            color=base_c,
            rotation_z=25,
        )
        self.label = Text(
            text=tower_type.name,
            parent=self,
            y=1.35,
            scale=5,
            origin=(0, 0),
            color=color.white,
            billboard=True,
        )
        self.range_ring = Entity(
            parent=self,
            model="circle",
            scale=tower_type.range * 2,
            y=0.02,
            color=color.rgba(255, 255, 100, 40),
            rotation_x=90,
            enabled=False,
        )

    @property
    def damage(self) -> float:
        return self.tower_type.damage * (1 + 0.35 * (self.level - 1))

    @property
    def attack_range(self) -> float:
        return self.tower_type.range * (1 + 0.08 * (self.level - 1))

    @property
    def attack_rate(self) -> float:
        return self.tower_type.attack_rate * (1 + 0.12 * (self.level - 1))

    def upgrade(self) -> bool:
        if self.level >= MAX_TOWER_LEVEL:
            return False
        self.level += 1
        s = self.tower_type.model_scale * (1 + 0.06 * (self.level - 1))
        self.scale = (s * 0.9, s * 0.35, s * 0.9)
        self.body.scale = 0.85 + 0.05 * self.level
        self.label.text = f"{self.tower_type.name} Lv{self.level}"
        self.range_ring.scale = self.attack_range * 2
        return True

    def update_tower(self, dt: float, creeps: List[Creep]) -> Optional[int]:
        """Attack creeps; return XP gained from kills this frame."""
        xp_gain = 0
        self.cooldown = max(0, self.cooldown - dt)
        if self.cooldown > 0:
            return 0

        target = self._pick_target(creeps)
        if not target:
            return 0

        self.cooldown = 1.0 / self.attack_rate
        proj = Projectile.acquire()
        proj.fire(
            self.position,
            target,
            self.damage,
            _rgb(self.tower_type.color),
        )
        return xp_gain

    def _pick_target(self, creeps: List[Creep]) -> Optional[Creep]:
        best = None
        best_dist = 0
        for c in creeps:
            if not c.alive:
                continue
            d = (c.position - self.position).length()
            if d <= self.attack_range and c.path_dist > best_dist:
                best = c
                best_dist = c.path_dist
        return best
