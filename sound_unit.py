from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QMediaPlaylist
from PyQt5.QtCore import QUrl
import os
import time


def restart_player(player: QMediaPlayer):
    player.stop()
    player.play()


class SoundUnit:
    def __init__(self):
        self.dir = os.getcwd()
        self._music_track = self.format_filename('music')
        self.music_player = QMediaPlayer()
        self.music = self.setup_playlist()
        self._shot_player = self.setup_music_player(
            self.format_filename('shot'))
        self._super_shot_player = self.setup_music_player(
            self.format_filename('super_shot'))
        self._ball_insertion_player = self.setup_music_player(
            self.format_filename('ball_insertion'))
        self._balls_destroyed_player = self.setup_music_player(
            self.format_filename('balls_destroyed'))

    def setup_playlist(self):
        music = QMediaPlaylist()
        music.addMedia(
            QMediaContent(QUrl.fromLocalFile(self._music_track)))
        music.setPlaybackMode(QMediaPlaylist.Loop)
        return music

    def format_filename(self, name: str):
        return f'{self.dir}/resources/{name}.ogg'

    @staticmethod
    def setup_music_player(filename: str):
        player = QMediaPlayer()
        player.setMedia(QMediaContent(QUrl.fromLocalFile(filename)))
        return player

    @staticmethod
    def stop_player(player: QMediaPlayer):
        if player.state() != QMediaPlayer.StoppedState:
            player.stop()

    def play_music(self):
        if self.music_player.state() == QMediaPlayer.PlayingState:
            raise ValueError("Playing already")
        self.music_player.setVolume(10)
        self.music_player.setPlaylist(self.music)
        self.music_player.play()

    def stop_music(self):
        if self.music_player.state() != QMediaPlayer.PlayingState:
            raise ValueError("Not playing")
        self.music_player.stop()

    def shot_sound(self):
        restart_player(self._shot_player)

    def super_shot_sound(self):
        restart_player(self._super_shot_player)

    def ball_insertion_sound(self):
        restart_player(self._ball_insertion_player)

    def balls_destroyed_sound(self):
        restart_player(self._balls_destroyed_player)
