"""Wave spawning and level progression."""

from __future__ import annotations

from typing import List, Optional

from game.config import CREEP_TYPES, LEVELS, LevelSpec, WaveSpec
from game.entities import Creep
from game.path import build_path_segments, path_total_length


class WaveController:
    def __init__(self, level: LevelSpec):
        self.level = level
        self.wave_index = 0
        self.queue: List[WaveSpec] = []
        self.spawn_timer = 0.0
        self.between_waves = 2.5
        self.break_timer = 0.0
        self.state = "break"  # break | spawning | done
        self.path_points, self.seg_lens = build_path_segments()
        self.path_len = path_total_length(self.seg_lens)
        self.creeps: List[Creep] = []
        self._pending: List[WaveSpec] = []
        self._start_next_wave()

    @property
    def waves_total(self) -> int:
        return len(self.level.waves)

    @property
    def wave_display(self) -> int:
        return min(self.wave_index + 1, self.waves_total)

    def _start_next_wave(self):
        if self.wave_index >= len(self.level.waves):
            self.state = "done"
            return
        specs = self.level.waves[self.wave_index]
        self._pending = []
        for spec in specs:
            for _ in range(spec.count):
                self._pending.append(spec)
        self.queue = list(self._pending)
        self.spawn_timer = 0.5
        self.state = "spawning"

    def _scaled_hp(self, base: float, wave_idx: int) -> float:
        wave_bonus = 1 + 0.06 * wave_idx
        return base * self.level.hp_mult * wave_bonus

    def _scaled_speed(self, base: float, wave_idx: int) -> float:
        return base * self.level.speed_mult * (1 + 0.02 * wave_idx)

    def spawn_one(self) -> Optional[Creep]:
        if not self.queue:
            return None
        spec = self.queue.pop(0)
        ctype = CREEP_TYPES[spec.creep_id]
        hp = self._scaled_hp(ctype.base_hp, self.wave_index)
        spd = self._scaled_speed(ctype.base_speed, self.wave_index)
        xp = ctype.xp_reward + self.level.xp_bonus
        creep = Creep(
            ctype, hp, spd, xp,
            self.path_points, self.seg_lens, self.path_len,
        )
        self.creeps.append(creep)
        return creep

    def update_waves(self, dt: float) -> tuple[int, int, bool]:
        """
        Returns (leaks, xp_from_kills, level_complete).
        Process spawning and creep movement.
        """
        leaks = 0
        xp = 0

        if self.state == "break":
            self.break_timer -= dt
            if self.break_timer <= 0:
                self._start_next_wave()
            return leaks, xp, False

        if self.state == "spawning":
            self.spawn_timer -= dt
            if self.spawn_timer <= 0 and self.queue:
                spec = self.queue[0]
                self.spawn_one()
                self.spawn_timer = spec.spawn_delay
            alive_count = sum(1 for c in self.creeps if c.alive)
            if not self.queue and alive_count == 0:
                self.wave_index += 1
                if self.wave_index >= len(self.level.waves):
                    self.state = "done"
                else:
                    self.state = "break"
                    self.break_timer = self.between_waves

        for c in list(self.creeps):
            if not c.alive:
                continue
            leaked = c.update_creep(dt)
            if leaked:
                leaks += 1

        self.creeps = [c for c in self.creeps if c.alive]

        return leaks, xp, self.state == "done" and not self.creeps
