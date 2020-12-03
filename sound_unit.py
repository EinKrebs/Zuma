from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl


class SoundUnit:
    def __init__(self):
        self.music = '/home/krebs/PythonProjects/Zuma/resources/music.mp3'
        self.player = QMediaPlayer()

    def play_music(self):
        self.player.setMedia(QMediaContent(QUrl.fromLocalFile(self.music)))
        self.player.play()

    def stop_music(self):
        if self.player.state() != QMediaPlayer.PlayingState:
            raise ValueError("Not playing")
        self.player.stop()
