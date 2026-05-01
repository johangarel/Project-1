from .entities import Key, Door
from .maze import Maze
from .utils import load_map, generate_custom_maze
from .settings import (
    NB_LEVELS, TILE_SIZE, VISION_RADIUS
)


class LevelManager:
    """Loads, resets, and exposes data for each level."""

    def __init__(self, player, level_configs: dict):
        self._player = player
        self.level_configs = level_configs
        for cfg in self.level_configs.values():
            cfg["loaded"] = False

        # Data per level (0-based indexed lists, level N → index N-1)
        self.wall_list         = [[] for _ in range(NB_LEVELS)]
        self.special_objs_list = [[] for _ in range(NB_LEVELS)]
        self.level_map_list    = [None for _ in range(NB_LEVELS)]

        self.vision_radius = VISION_RADIUS

    # ------------------------------------------------------------------
    # Current access
    # ------------------------------------------------------------------

    def walls(self, maze_id: int) -> list:
        return self.wall_list[maze_id - 1]

    def special_objs(self, maze_id: int) -> list:
        return self.special_objs_list[maze_id - 1]

    def has_fow(self, maze_id: int) -> bool:
        cfg = self.level_configs.get(maze_id)
        return bool(cfg and cfg.get("fow"))

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------

    def load_sub_map(self, maze_id: int, map_index: int, game) -> None:
        """Load a sub-map and update internal lists."""
        config = self.level_configs[maze_id]
        layout = self._build_layout(maze_id, map_index)

        current_maze = Maze(layout, config["tps"], self._player, game, map_index=map_index)

        self.level_map_list[maze_id - 1]    = layout
        self.wall_list[maze_id - 1]         = current_maze.walls
        self.special_objs_list[maze_id - 1] = current_maze.special_objs
        self.vision_radius = VISION_RADIUS

        return layout  # returned so Game can recalculate dimensions

    def load_level(self, maze_id: int, game) -> None:
        """Load the complete level (sub-map 0) and mark the level as loaded."""
        config = self.level_configs[maze_id]
        layout = self._build_layout(maze_id, 0)

        current_maze = Maze(layout, config["tps"], self._player, game, map_index=0)
        spawn = current_maze.spawn_point

        self.level_map_list[maze_id - 1]    = layout
        self.wall_list[maze_id - 1]         = current_maze.walls
        self.special_objs_list[maze_id - 1] = current_maze.special_objs
        config["loaded"] = True

        self._player.move_spawn(spawn[0], spawn[1])
        self._player.respawn()
        self.vision_radius = VISION_RADIUS

        return layout

    # ------------------------------------------------------------------
    # Reset
    # ------------------------------------------------------------------

    def reset_objects(self, maze_id: int) -> None:
        """Reset keys and doors of the level (player death)."""
        for obj in self.special_objs_list[maze_id - 1]:
            if isinstance(obj, (Key, Door)):
                obj.reset()

    def reset_vision(self) -> None:
        self.vision_radius = VISION_RADIUS

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _build_layout(self, maze_id: int, map_index: int) -> list:
        """Generates or reads the grid according to the level."""
        # Level 3: procedural generation
        if maze_id == 3:
            return self._generate_level3(map_index)

        config = self.level_configs[maze_id]
        return load_map(config["file"][map_index])

    def _generate_level3(self, map_index: int) -> list:
        if map_index == 0:
            layout = generate_custom_maze(31, 21, ('P', 0, 1), ('S', 30, 19))
        elif map_index == 1:
            layout = generate_custom_maze(31, 21, (' ', 0, 1), ('S', 30, 1))
            row_list = list(layout[19])
            row_list[30] = 'S'
            layout[19] = "".join(row_list)
        else:  # map_index == 2
            layout = generate_custom_maze(31, 21, (' ', 0, 1), ('V', 30, 19))
        self._player.move_spawn(TILE_SIZE / 4, TILE_SIZE)
        return layout
