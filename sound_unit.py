import os
import sys
import pyogg

from PyQt5.QtCore import QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QMediaPlaylist, \
    QMediaMetaData


def restart_player(player: QMediaPlayer):
    if player is None:
        return
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
        if not self.check_music_file(self._music_track):
            return None
        music.addMedia(
            QMediaContent(QUrl.fromLocalFile(self._music_track)))
        music.setPlaybackMode(QMediaPlaylist.Loop)
        return music

    def format_filename(self, name: str):
        return f'{self.dir}/resources/{name}.ogg'

    @staticmethod
    def setup_music_player(filename: str):
        if not SoundUnit.check_music_file(filename):
            return None
        player = QMediaPlayer()
        try:
            player.setMedia(QMediaContent(QUrl.fromLocalFile(filename)))
        except QMediaPlayer.Error as e:
            print(e, file=sys.stderr)
            return None
        return player

    @staticmethod
    def check_music_file(filename):
        try:
            pyogg.VorbisFile(filename)
            return True
        except pyogg.ogg.PyOggError:
            print(f'File {filename} doesn\'t exist or incorrect: only OGG '
                  f'Vorbis files are supported',
                  file=sys.stderr)
            return False

    @staticmethod
    def stop_player(player: QMediaPlayer):
        if player is None:
            return
        if player.state() != QMediaPlayer.StoppedState:
            player.stop()

    def play_music(self):
        if self.music_player is None or self.music is None:
            return
        if self.music_player.state() == QMediaPlayer.PlayingState:
            raise ValueError("Playing already")
        self.music_player.setVolume(10)
        self.music_player.setPlaylist(self.music)
        try:
            self.music_player.play()
        except QMediaPlayer.Error as e:
            self.music_player = None
            print(e, file=sys.stderr)
        except Exception as e:
            self.music_player = None
            print('AAAAAAAAAAAAAA')
            print(e, file=sys.stderr)

    def stop_music(self):
        if self.music_player is None:
            return
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
