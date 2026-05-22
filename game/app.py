"""Main Ursina application — UI, input, game loop, clean shutdown."""

from __future__ import annotations

import atexit
import sys
from typing import List, Optional

from ursina import (
    Button,
    Entity,
    Text,
    Vec3,
    application,
    camera,
    color,
    destroy,
    mouse,
    scene,
    time,
)

from game.config import (
    LEVELS,
    TOWER_TYPES,
    TOTAL_LEVELS,
    UPGRADE_COSTS,
)
from game.entities import PokemonTower, Projectile
from game.path import can_build, grid_to_world, world_to_grid
from game.waves import WaveController
from game.world import GameWorld


class TDGame:
    def __init__(self, ursina_app=None):
        self.app = ursina_app
        self._shutting_down = False

        self._setup_camera()
        self.world: Optional[GameWorld] = None
        self.waves: Optional[WaveController] = None
        self.towers: List[PokemonTower] = []
        self.level_index = 0
        self.xp = 0
        self.lives = 20
        self.selected_tower_type = "pikachu"
        self.placing = False
        self.selected_tower: Optional[PokemonTower] = None
        self.state = "menu"
        self._ghost: Optional[Entity] = None

        self._build_ui()
        self.show_menu()

    def _setup_camera(self):
        camera.orthographic = False
        camera.position = Vec3(0, 16, -10)
        camera.rotation_x = 52
        camera.fov = 45

    def _build_ui(self):
        self.ui_root = Entity(parent=camera.ui)

        self.title = Text(
            parent=self.ui_root,
            text="Pokemon vs Dota TD",
            y=0.42,
            scale=2.5,
            origin=(0, 0),
            color=color.gold,
        )
        self.subtitle = Text(
            parent=self.ui_root,
            text="Top-down 3D Tower Defense",
            y=0.36,
            scale=1.2,
            origin=(0, 0),
        )
        self.status = Text(
            parent=self.ui_root,
            text="",
            y=0.48,
            x=-0.85,
            scale=1,
            origin=(-0.5, 0),
        )
        self.hint = Text(
            parent=self.ui_root,
            text="",
            y=-0.46,
            scale=0.9,
            origin=(0, 0),
            color=color.light_gray,
        )

        self.btn_start = Button(
            parent=self.ui_root,
            text="Start Level 1",
            y=0.1,
            scale=(0.35, 0.08),
            color=color.azure.tint(-0.1),
            on_click=self._on_start_click,
        )
        self.btn_next = Button(
            parent=self.ui_root,
            text="Next Level",
            y=0.0,
            scale=(0.35, 0.08),
            color=color.lime.tint(-0.1),
            on_click=self._on_next_level,
        )
        self.btn_retry = Button(
            parent=self.ui_root,
            text="Retry",
            y=-0.1,
            scale=(0.35, 0.08),
            color=color.orange,
            on_click=self._retry_level,
        )
        self.btn_quit = Button(
            parent=self.ui_root,
            text="Quit",
            y=-0.22,
            scale=(0.3, 0.07),
            color=color.red.tint(-0.1),
            on_click=self.shutdown,
        )

        tower_names = list(TOWER_TYPES.keys())
        self.tower_buttons: List[Button] = []
        for i, tid in enumerate(tower_names):
            tt = TOWER_TYPES[tid]
            btn = Button(
                parent=self.ui_root,
                text=f"{tt.name}\n({tt.place_cost} XP)",
                x=-0.82 + i * 0.22,
                y=-0.38,
                scale=(0.18, 0.07),
                color=color.rgb(tt.color[0] / 255, tt.color[1] / 255, tt.color[2] / 255),
                on_click=lambda t=tid: self._select_tower_type(t),
            )
            self.tower_buttons.append(btn)

        self.btn_place = Button(
            parent=self.ui_root,
            text="Place",
            x=0.35,
            y=-0.38,
            scale=(0.12, 0.06),
            on_click=self._toggle_place,
        )
        self.btn_upgrade = Button(
            parent=self.ui_root,
            text="Upgrade",
            x=0.5,
            y=-0.38,
            scale=(0.12, 0.06),
            on_click=self._upgrade_selected,
        )
        self.btn_sell = Button(
            parent=self.ui_root,
            text="Sell",
            x=0.65,
            y=-0.38,
            scale=(0.1, 0.06),
            on_click=self._sell_selected,
        )

        self._hide_game_ui()

    def _hide_game_ui(self):
        for b in self.tower_buttons:
            b.visible = False
        self.btn_place.visible = False
        self.btn_upgrade.visible = False
        self.btn_sell.visible = False
        self.status.visible = False
        self.hint.visible = False

    def _show_game_ui(self):
        for b in self.tower_buttons:
            b.visible = True
        self.btn_place.visible = True
        self.btn_upgrade.visible = True
        self.btn_sell.visible = True
        self.status.visible = True
        self.hint.visible = True

    def show_menu(self):
        self.state = "menu"
        self.title.visible = True
        self.subtitle.visible = True
        self.btn_start.visible = True
        self.btn_start.text = f"Start Level {self.level_index + 1}"
        self.btn_next.visible = False
        self.btn_retry.visible = False
        self._hide_game_ui()
        self._clear_level()

    def _on_start_click(self):
        self.start_level(self.level_index)

    def _on_next_level(self):
        if self.level_index + 1 < TOTAL_LEVELS:
            self.level_index += 1
            self.start_level(self.level_index)
        else:
            self.level_index = 0
            self.show_menu()

    def _retry_level(self):
        self.start_level(self.level_index)

    def _clear_level(self):
        if self.world:
            self.world.destroy_all()
            self.world = None
        if self.waves:
            for c in list(self.waves.creeps):
                if c:
                    destroy(c)
            self.waves = None
        for t in self.towers:
            destroy(t)
        self.towers.clear()
        for p in list(Projectile.pool):
            p.release()
        if self._ghost:
            destroy(self._ghost)
            self._ghost = None

    def start_level(self, index: int):
        self._clear_level()
        level = LEVELS[index]
        self.level_index = index
        self.state = "play"
        self.xp = level.start_xp
        self.lives = level.lives

        self.title.visible = False
        self.subtitle.visible = False
        self.btn_start.visible = False
        self.btn_next.visible = False
        self.btn_retry.visible = False
        self._show_game_ui()

        self.world = GameWorld()
        self.waves = WaveController(level)
        self._update_hud()

    def _select_tower_type(self, tid: str):
        self.selected_tower_type = tid
        self.placing = True
        self.selected_tower = None
        self._refresh_ghost()

    def _toggle_place(self):
        self.placing = not self.placing
        if self.placing:
            self.selected_tower = None
        self._refresh_ghost()

    def _upgrade_selected(self):
        if not self.selected_tower or self.state != "play":
            return
        t = self.selected_tower
        if t.level > len(UPGRADE_COSTS):
            return
        cost = UPGRADE_COSTS[t.level - 1]
        if self.xp < cost:
            return
        if t.upgrade():
            self.xp -= cost
            self._update_hud()

    def _sell_selected(self):
        if not self.selected_tower:
            return
        tt = self.selected_tower.tower_type
        refund = max(5, int(tt.place_cost * 0.5))
        self.xp += refund
        destroy(self.selected_tower)
        self.towers.remove(self.selected_tower)
        self.selected_tower = None
        self._update_hud()

    def _refresh_ghost(self):
        if self._ghost:
            destroy(self._ghost)
            self._ghost = None
        if not self.placing or self.state != "play":
            return
        tt = TOWER_TYPES[self.selected_tower_type]
        self._ghost = Entity(
            model="sphere",
            scale=tt.model_scale,
            color=color.rgba(tt.color[0], tt.color[1], tt.color[2], 120),
            collider=None,
        )

    def _try_place(self):
        if not self.placing or self.state != "play" or not self.waves:
            return
        if not mouse.world_point:
            return
        gx, gz = world_to_grid(mouse.world_point)
        if not can_build(gx, gz):
            return
        if any(t.gx == gx and t.gz == gz for t in self.towers):
            return
        tt = TOWER_TYPES[self.selected_tower_type]
        if self.xp < tt.place_cost:
            return
        tower = PokemonTower(tt, gx, gz)
        self.towers.append(tower)
        self.xp -= tt.place_cost
        self.placing = False
        if self._ghost:
            destroy(self._ghost)
            self._ghost = None
        self._update_hud()

    def _pick_tower(self):
        if not mouse.world_point:
            return
        gx, gz = world_to_grid(mouse.world_point)
        for t in self.towers:
            t.range_ring.enabled = False
            if t.gx == gx and t.gz == gz:
                self.selected_tower = t
                t.range_ring.enabled = True
                self.placing = False
                if self._ghost:
                    destroy(self._ghost)
                    self._ghost = None
                return

    def _update_hud(self):
        if not self.waves:
            return
        lvl = LEVELS[self.level_index]
        self.status.text = (
            f"Level {lvl.index}: {lvl.name}  |  "
            f"Wave {self.waves.wave_display}/{self.waves.waves_total}  |  "
            f"XP: {self.xp}  |  Lives: {self.lives}"
        )
        up_cost = ""
        if self.selected_tower and self.selected_tower.level <= len(UPGRADE_COSTS):
            up_cost = f"  |  Upgrade: {UPGRADE_COSTS[self.selected_tower.level - 1]} XP"
        self.hint.text = (
            "LMB: place/select  |  P: place mode  |  U: upgrade  |  ESC: quit"
            + up_cost
        )

    def _level_won(self):
        self.state = "win"
        self.btn_next.visible = True
        self.btn_retry.visible = True
        if self.level_index + 1 >= TOTAL_LEVELS:
            self.subtitle.text = "All 10 levels cleared!"
            self.subtitle.visible = True
            self.btn_next.text = "Back to Menu"
        else:
            self.subtitle.text = "Level complete!"
            self.subtitle.visible = True
            self.btn_next.text = f"Level {self.level_index + 2}"

    def _level_lost(self):
        self.state = "lose"
        self.subtitle.text = "Defeat — creeps reached the core"
        self.subtitle.visible = True
        self.btn_retry.visible = True

    def update(self):
        if self._shutting_down:
            return

        if self.state != "play" or not self.waves:
            return

        dt = min(0.05, time.dt)

        leaks, wave_xp, complete = self.waves.update_waves(dt)
        self.lives -= leaks
        self.xp += wave_xp

        for p in Projectile.pool:
            if p._active:
                self.xp += p.update_proj(dt)

        for t in self.towers:
            t.update_tower(dt, self.waves.creeps)

        if self._ghost and self.placing and mouse.world_point:
            gx, gz = world_to_grid(mouse.world_point)
            self._ghost.position = grid_to_world(gx, gz) + Vec3(0, 0.5, 0)

        self._update_hud()

        if self.lives <= 0:
            self._level_lost()
        elif complete:
            self._level_won()

    def input(self, key):
        if self._shutting_down:
            return
        if key == "escape":
            self.shutdown()
            return
        if self.state == "play":
            if key == "p":
                self._toggle_place()
            elif key == "u":
                self._upgrade_selected()
            elif key == "left mouse down":
                if self.placing:
                    self._try_place()
                else:
                    self._pick_tower()

    def shutdown(self):
        if self._shutting_down:
            return
        self._shutting_down = True

        self._clear_level()
        for p in list(Projectile.pool):
            destroy(p)
        Projectile.pool.clear()

        if getattr(self, "ui_root", None):
            destroy(self.ui_root)

        for e in list(scene.entities):
            destroy(e)

        application.quit()
        sys.exit(0)
