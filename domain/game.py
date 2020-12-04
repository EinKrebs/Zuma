from domain.level import Level
from sound_unit import SoundUnit
import os


class Game:
    def __init__(
        self,
        levels,
    ):
        self.levels = levels
        self.current_level_index = 0
        self.last_level_complete_time = None
        self.over = -1
        self.running = True
        self.score = 0

    @staticmethod
    def from_directory(directory, sound_unit):
        levels = [
            Level.from_file(os.path.join(directory, file), sound_unit)
            for file in os.listdir(directory)]
        return Game(levels)

    @property
    def current_level(self) -> Level:
        return (self.levels[self.current_level_index]
                if self.current_level_index < len(self.levels)
                else None)

    def update(self):
        if self.over != -1 or not self.running:
            return
        self.current_level.go_next_state()
        if self.current_level.hp <= 0:
            self.over = 0
            self.score += self.current_level.score
        if self.current_level.finished:
            self.running = False
            self.score += self.current_level.score

    def next_level(self):
        self.last_level_complete_time = self.current_level.complete_time
        self.current_level_index += 1
        if self.current_level_index >= len(self.levels):
            self.over = 1
        else:
            self.current_level.start()
        self.running = True

    def pause(self):
        if self.current_level:
            self.current_level.pause()

    def resume(self):
        if self.current_level:
            self.current_level.resume()
