from .settings import NB_LEVELS


class AudioManager:
    """Manages all audio logic: music, sound effects, and volume."""

    def __init__(self, assets, save_data):
        self._assets = assets
        self.music_play = save_data["music"]
        self.music_animation = False
        self.time_display = 2.0

        # Active music
        self._active: object = assets["menu_music"]

        # Build playlist indexed by level (1-based, index 0 = menu)
        self._playlist = [None] * (NB_LEVELS + 1)
        self._playlist[0] = assets["menu_music"]
        self._playlist[1] = assets["music_level1"]
        self._playlist[2] = assets["music_level2"]
        self._playlist[3] = assets["music_level3"]
        self._playlist[4] = assets["music_level4"]
        self._playlist[42] = assets["music_level42"]

        # Initialize volumes
        volume = 0.5 if self.music_play else 0.0
        for track in self._playlist:
            if track is not None:
                track.set_volume(volume)

        self._active.play(loops=-1)

    # ------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------

    def music_for_level(self, level_id: int):
        """Returns the track associated with the level (None if not defined)."""
        if 0 <= level_id < len(self._playlist):
            return self._playlist[level_id]
        return None

    def switch(self, track) -> None:
        """Switch track. Respects the music_play setting."""
        if self._active is not None:
            self._active.stop()
        self._active = track
        if self._active is not None:
            vol = 0.5 if self.music_play else 0.0
            self._active.set_volume(vol)
            self._active.play(loops=-1)

    def switch_to_menu(self) -> None:
        if self._active is not self._assets["menu_music"]:
            self.switch(self._assets["menu_music"])

    def switch_to_victory(self) -> None:
        self.switch(self._assets["music_victory"])

    def switch_to_level(self, level_id: int) -> None:
        track = self.music_for_level(level_id)
        if track is not None:
            self.switch(track)

    def toggle(self) -> bool:
        """Toggle mute/unmute. Returns the new state."""
        self.music_play = not self.music_play
        volume = 0.5 if self.music_play else 0.0
        if self._active is not None:
            self._active.set_volume(volume)
        self.time_display = 2.0
        self.music_animation = True
        return self.music_play

    def play_sfx(self, name: str) -> None:
        sfx = self._assets.get(name)
        if sfx:
            sfx.play()

    def update(self, dt: float) -> None:
        """To be called each frame to manage the music icon animation."""
        if self.music_animation:
            self.time_display -= dt
            if self.time_display <= 0:
                self.music_animation = False
                self.time_display = 2.0
