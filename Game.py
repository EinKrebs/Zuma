from Level import Level


class Game:
    def __init__(
        self,
        levels
    ):
        self.levels = levels
        self.current_level_index = 0
        self.last_level_complete_time = None
        self.over = -1
        self.running = True
        self.score = 0

    @staticmethod
    def from_string_array(array):
        length = len(array)
        levels = []
        if length % 2 != 0:
            raise ValueError
        for i in range(length // 2):
            levels.append(
                Level.from_string_array([
                    array[2 * i][:-1],
                    array[2 * i + 1][:-1]])
            )
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
        self.running = True
