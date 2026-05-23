from .entities import Wall, Trap, Portal, Key, Door, Player, Winpad, Light, SubMapPortal
from .utils import optimise_walls
from .settings import WALL_THICKNESS, BANNED_BUILDING_CHARACTERS, TILE_SIZE

class Maze:
    def __init__(self, layout, tp_order, player, game, map_index: int = 0, submap_routes: dict = None):
        assert isinstance(player, Player)

        self.special_objs   = []
        self.spawn_point    = player.default_pos
        self.enemy_spawns   = []
        self.sub_portal_count = 0
        self.submap_routes  = submap_routes or {}

        wall_thickness = WALL_THICKNESS
        offset         = (game.tile_size // 2) - (wall_thickness // 2)

        raw_walls = []

        for row_id, row in enumerate(layout):
            for col_id, char in enumerate(row):
                x = col_id * game.tile_size
                y = row_id * game.tile_size

                result = self._parse_tile(
                    char, x, y, row_id, col_id,
                    layout, tp_order, game, map_index,
                    wall_thickness, offset,
                )

                if result == "spawn":
                    self.spawn_point = (x, y)
                elif result == "enemy_spawn":
                    self.enemy_spawns.append((x, y))
                elif isinstance(result, Wall):
                    raw_walls.append(result)
                elif isinstance(result, list):          # multiple walls from one tile
                    raw_walls.extend(result)
                elif result is not None:                # any special object
                    self.special_objs.append(result)

        self.walls = optimise_walls(raw_walls)

    # ------------------------------------------------------------------
    # tile parser – one method, one responsibility
    # ------------------------------------------------------------------

    def _parse_tile(
        self, char, x, y, row_id, col_id,
        layout, tp_order, game, map_index,
        wall_thickness, offset,
    ):
        """
        Returns:
          - "spawn"       → caller sets self.spawn_point
          - Wall / list   → added to raw_walls
          - entity object → added to special_objs
          - None          → empty tile, nothing to do
        """

        # ── Empty / space ───────────────────────────────────────────────
        if char == " ":
            return None

        # ── Wall ────────────────────────────────────────────────────────
        if char == "W":
            return self._build_wall_segments(
                x, y, row_id, col_id, layout, game.tile_size, wall_thickness, offset
            )

        # ── Player spawn ────────────────────────────────────────────────
        if char == "P":
            return "spawn"

        # ── Victory pad ─────────────────────────────────────────────────
        if char == "V":
            return Winpad(x, y, game.assets["winpad"])

        # ── Trap ────────────────────────────────────────────────────────
        if char == "T":
            return Trap(x, y, game.assets["trap"])

        # ── Light / torch ───────────────────────────────────────────────
        if char == "L":
            return Light(x, y, game.assets["torch"])

        # ── Sub-map portal ──────────────────────────────────────────────
        if char == "S":
            return self._build_submap_portal(x, y, game, map_index)
        
        # ── Enemy ───────────────────────────────────────────────────────
        if char == "E":
            return "enemy_spawn"

        # ── Teleport portal (digit) ─────────────────────────────────────
        if char.isdigit():
            idx = int(char)
            return Portal(x, y, idx, tp_order[idx], game.assets["tp1"], game.assets["tp2"])

        # ── Key (lowercase letter) ──────────────────────────────────────
        if char.islower():
            return Key(x, y, char, game.assets["key"])

        # ── Door (uppercase letter, not W/P/V/T/L/S) ───────────────────
        if char.isupper():
            return self._build_door(x, y, row_id, col_id, layout, game)

        return None

    # ------------------------------------------------------------------
    # Wall geometry helpers
    # ------------------------------------------------------------------

    def _build_wall_segments(
        self, x, y, row_id, col_id, layout, tile_size, wall_thickness, offset
    ):
        """Returns a list of Wall segments for a 'W' tile."""
        banned = BANNED_BUILDING_CHARACTERS

        def _upper_not_banned(ch):
            return ch.isupper() and ch not in banned

        down  = row_id < len(layout) - 1 and _upper_not_banned(layout[row_id + 1][col_id])
        up    = row_id > 0              and _upper_not_banned(layout[row_id - 1][col_id])
        right = col_id < len(layout[row_id]) - 1 and _upper_not_banned(layout[row_id][col_id + 1])
        left  = col_id > 0                        and _upper_not_banned(layout[row_id][col_id - 1])

        segments = []

        # 1. Vertical segment
        if up or down:
            v_start  = y if up  else y + offset
            v_height = tile_size if (up and down) else (tile_size // 2 + wall_thickness // 2)
            segments.append(Wall(x + offset, v_start, wall_thickness, v_height))

        # 2. Horizontal segment
        if left or right:
            h_start = x if left else x + offset
            h_width = tile_size if (left and right) else (tile_size // 2 + wall_thickness // 2)
            segments.append(Wall(h_start, y + offset, h_width, wall_thickness))

        # 3. Isolated dot
        if not (up or down or left or right):
            segments.append(Wall(x + offset, y + offset, wall_thickness, wall_thickness))

        return segments

    def _build_door(self, x, y, row_id, col_id, layout, game):
        """Returns a Door (or a list of two Doors) for an uppercase letter tile."""
        doors = []
        ts    = game.tile_size

        cond_vertical   = (
            0 < row_id < len(layout) - 1
            and layout[row_id + 1][col_id] == "W"
            and layout[row_id - 1][col_id] == "W"
        )
        cond_horizontal = (
            0 < col_id < len(layout[row_id]) - 1
            and layout[row_id][col_id + 1] == "W"
            and layout[row_id][col_id - 1] == "W"
        )

        char = layout[row_id][col_id]

        if cond_vertical:
            doors.append(Door(x + ts / 2 - 5, y, 10, ts, char))
        if cond_horizontal:
            doors.append(Door(x, y + ts / 2 - 5, ts, 10, char))

        # Return a single object when possible so the caller can append/extend uniformly
        if len(doors) == 1:
            return doors[0]
        return doors if doors else None

    def _build_submap_portal(self, x, y, game, map_index):
        """Returns a SubMapPortal if a route is configured, else None."""
        level_id = game.maze
        routes   = self.submap_routes

        # Convert map_index to string (keys in JSON are strings)
        map_index_str = str(map_index)
        portal_index_str = str(self.sub_portal_count)

        config = None
        if (
            level_id in routes
            and map_index_str in routes[level_id]
            and portal_index_str in routes[level_id][map_index_str]
        ):
            config = routes[level_id][map_index_str][portal_index_str]

        if config:
            # Convert grid coordinates to pixels if spawn_pos is in grid format
            spawn_pos = config["spawn_pos"]
            if isinstance(spawn_pos, (list, tuple)) and len(spawn_pos) == 2:
                spawn_pixels = (spawn_pos[0] * TILE_SIZE, spawn_pos[1] * TILE_SIZE)
            else:
                spawn_pixels = spawn_pos
            
            portal = SubMapPortal(
                x, y,
                config["target_map"],
                spawn_pixels,
                game.assets["tp3"],
            )
            self.sub_portal_count += 1
            return portal

        return None