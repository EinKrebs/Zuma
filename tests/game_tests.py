import os
import unittest
import unittest.mock

from domain.game import Game
from domain.level import Level
from sound_unit import SoundUnit


class GameTests(unittest.TestCase):
    @staticmethod
    def two_dim_lists_equal(first, second, param):
        cond = len(first) == len(second)
        if cond:
            for i in range(len(first)):
                cond1 = (len(param(first[i]))
                         == len(param(second[i])))
                if cond1:
                    for j in range(len(param(first[i]))):
                        cond1 = (cond1
                                 and param(first[i])[j]
                                 == param(second[i])[j])
                cond = cond and cond1
        return cond

    @staticmethod
    def level_equals(first: Level, second: Level):
        cond = GameTests.two_dim_lists_equal(first.sequences,
                                             second.sequences,
                                             lambda x: x.balls)
        cond = cond and GameTests.two_dim_lists_equal(
            first.next_sequences,
            second.next_sequences,
            lambda x: x
        )
        if not cond:
            return cond
        if ((first.current_sequence_next is None
             and second.current_sequence_next is not None)
                or (first.current_sequence_next is not None
                    and second.current_sequence_next is None)):
            return False
        if first.current_sequence_next is None:
            return True
        if (len(first.current_sequence_next)
                != len(second.current_sequence_next)):
            return False
        for i in range(len(first.current_sequence_next)):
            if (first.current_sequence_next[i]
                    != second.current_sequence_next[i]):
                return False
        return True

    def test_general(self):
        mock = unittest.mock.create_autospec(SoundUnit)
        game = Game.from_directory(['test_levels'], [], sound_unit=mock)
        level = Level.from_file('test_levels/test_level1.txt')
        self.assertTrue(self.level_equals(level, game.current_level))
        game.update()
        level.go_next_state()
        self.assertTrue(self.level_equals(level, game.current_level))
        game.current_level.finished = True
        game.update()
        self.assertTrue(self.level_equals(level, game.current_level))
        game.current_level.hp = 0
        game.current_level.finished = False
        game.update()
        self.assertTrue(self.level_equals(level, game.current_level))
        game.next_level()
        level = Level.from_file('test_levels/test_level2.txt')
        self.assertTrue(self.level_equals(level, game.current_level))
        game.next_level()
        self.assertEqual(game.over, 1)
        self.assertIsNone(game.current_level)
