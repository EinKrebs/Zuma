import sys
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import *  # TODO: remove all import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import math

from Game import Game
from Ellipse import Ellipse


class ViewControl(QWidget):
    def __init__(self):
        super().__init__()

        self.text = 'Hello world!'
        self.setGeometry(100, 100, 800, 600)
        self.ellipse = Ellipse(400, 600, 0, math.pi)
        self.game = Game(self.ellipse, [0, 0, 1], 20, 0.1, 4, (0, 90))
        self.setWindowTitle('Zuma')
        # self.image = QtGui.QImage("Frog.jpg")
        self.image = QLabel(self)
        self.image.setAlignment(Qt.AlignCenter)
        self.pixmap = None

        self.show()

        QTimer.singleShot(1, self.go)

    def go(self):
        while True:
            self.update()
            QApplication.processEvents()
            # TODO: move model to another thread, or use QTimer
            # QThread.msleep(10)
            self.game.go_next_state()
            self.draw_frog()

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        if event.key() == 0x41:  # A
            self.game.left = True
            self.game.right = False
        elif event.key() == 0x44:  # D
            self.game.right = True
            self.game.left = False
        elif event.key() == 0x20:  # Space
            self.game.shoot()

    def keyReleaseEvent(self, event: QtGui.QKeyEvent):
        if event.key() == 0x41:  # A
            self.game.left = False
        elif event.key() == 0x44:  # D
            self.game.right = False

    def wheelEvent(self, event: QtGui.QWheelEvent):
        self.game.turn_turret(
            self.game.turret_speed * event.angleDelta().y() / 50)

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.game.shoot()

    def paintEvent(self, event: QPaintEvent):
        qp = QPainter()
        qp.begin(self)

        # self.draw_text(event, qp)
        self.draw_game(event, qp)

        qp.end()

    def draw_text(self, event, qp):
        qp.setFont(QFont('Segoe UI', 16))
        qp.drawText(event.rect(), Qt.AlignCenter, str(self.game.turret_angle))

    def draw_game(self, event, qp):
        self.draw_ellipse(event, qp)
        self.draw_balls(event, qp)

    def draw_ellipse(self, event, qp):
        pen = QPen(QColor(0, 0, 0), 4, Qt.SolidLine)
        qp.setPen(pen)
        size = self.size()
        qp.drawEllipse(size.width() // 2 - self.ellipse.width,
                       size.height() - self.ellipse.height,
                       2 * self.ellipse.width, 2 * self.ellipse.height)

    def draw_frog(self):
        self.pixmap = QPixmap()
        self.pixmap.load("Frog.jpg", flags=Qt.AutoColor)
        self.image.resize(self.pixmap.width() * math.sqrt(2),
                          self.pixmap.height() * math.sqrt(2))
        self.image.move(self.width() // 2 - self.game.turret[
            0] - self.image.width() // 2,
                        self.height() - self.game.turret[
                            1] - self.image.height() // 2)
        t = QTransform().rotate((self.game.turret_angle - math.pi / 2
                                 ) / math.pi * 180)

        self.image.setPixmap(self.pixmap.transformed(t, ))

    def draw_balls(self, event, qp):
        for ball in self.game.balls:
            self.draw_ball(qp, ball.point, self.game.radius, ball.color)
        for shot in self.game.shot_balls:
            self.draw_ball(qp, (shot.x, shot.y), self.game.radius, shot.color)

    def draw_ball(self, qp, point, radius, color):
        qp.setBrush(color)
        pen = QPen(QColor(0, 0, 0), 1, Qt.SolidLine)
        qp.setPen(pen)
        qp.drawEllipse(self.width() // 2 - point[0] - radius,
                       self.height() - point[1] - radius,
                       2 * radius,
                       2 * radius)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    widget = ViewControl()
    widget.show()

    sys.exit(app.exec_())
