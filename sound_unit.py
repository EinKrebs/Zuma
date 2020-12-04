from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QMediaPlaylist
from PyQt5.QtCore import QUrl
import os
import time


class SoundUnit:
    def __init__(self):
        self.dir = os.getcwd()
        self.music_track = self.format_filename('music')
        self.shot = self.format_filename('shot')
        self.super_shot = self.format_filename('super_shot')
        self.ball_insertion = self.format_filename('ball_insertion')
        self.balls_destroyed = self.format_filename('balls_destroyed')
        self.music_player = QMediaPlayer()
        self.music = self.setup_playlist()
        self.action_player = QMediaPlayer()

    def setup_playlist(self):
        music = QMediaPlaylist()
        music.addMedia(
            QMediaContent(QUrl.fromLocalFile(self.music_track)))
        music.setPlaybackMode(QMediaPlaylist.Loop)
        return music

    def format_filename(self, name: str):
        return f'{self.dir}/resources/{name}.ogg'

    @staticmethod
    def set_music_player(player: QMediaPlayer, filename: str):
        player.setMedia(QMediaContent(QUrl.fromLocalFile(filename)))

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

    def action_sound(self, action: str):
        self.action_player.stop()
        self.set_music_player(self.action_player, action)
        self.action_player.play()
