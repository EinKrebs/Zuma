import sys
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QApplication, QLabel
from PyQt5.QtGui import QPainter, QPaintEvent, QFont, QPen, QColor, QPixmap,\
    QTransform
from PyQt5.QtCore import Qt, QTimer
import math

from Game import Game
from Ellipse import Ellipse
import MathExtentions as mathExt


class ViewControl(QWidget):
    def __init__(self):
        super().__init__()

        self.text = 'Hello world!'
        self.width = 800
        self.height = 600
        self.setGeometry(100, 100, self.width, self.height)
        self.ellipse = Ellipse(400, 600, 0, math.pi)
        self.game = Game(self.ellipse, [1, 1, 0, 0, 0, 1], 20, 1, 150, (0, 90))
        self.setWindowTitle('Zuma')
        # self.image = QtGui.QImage("Frog.jpg")
        self.image = QLabel(self)
        self.image.setAlignment(Qt.AlignCenter)
        self.pixmap = None

        self.timer = self.startTimer(10)

        self.show()

    def timerEvent(self, e):
        self.update()
        QApplication.processEvents()
        self.game.go_next_state()

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

        if self.game.finished:
            self.draw_level_completed(qp)
        elif self.game.hp > 0:
            self.draw_text(event, qp)
            self.draw_game(event, qp)
            self.draw_frog()
            self.debug_draw(qp)
        else:
            self.draw_game_over(qp)

        qp.end()

    def draw_text(self, event, qp):
        qp.setFont(QFont('Segoe UI', 16))
        qp.drawText(
            QtCore.QRect(0, 0, 100, 60),
            Qt.AlignCenter,
            f'HP: {self.game.hp}\nScore:{self.game.score}')

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
        self.pixmap = QPixmap('Frog.jpg')
        self.image.resize(self.pixmap.width() * math.sqrt(2),
                          self.pixmap.height() * math.sqrt(2))
        self.image.move(self.width // 2 - self.game.turret[
            0] - self.image.width() // 2,
                        self.height - self.game.turret[
                            1] - self.image.height() // 2)
        t = QTransform().rotate((self.game.turret_angle - math.pi / 2
                                 ) / math.pi * 180)

        self.image.setPixmap(self.pixmap.transformed(t))

    def draw_balls(self, event, qp):
        for ball in self.game.balls:
            self.draw_ball(qp,
                           ball.point,
                           self.game.radius,
                           QColor(*ball.color))
        for shot in self.game.shots:
            self.draw_ball(qp,
                           (shot.x, shot.y),
                           self.game.radius,
                           QColor(*shot.color))

    def draw_game_over(self, qp: QPainter):
        qp.setFont(QFont('Segoe UI', 30))
        qp.drawText(
            QtCore.QRect(0, 0, self.width, self.height),
            Qt.AlignCenter,
            'GAME OVER'
        )

    def draw_level_completed(self, qp: QPainter):
        qp.setFont(QFont('Segoe UI', 30))
        qp.drawText(
            QtCore.QRect(0, 0, self.width, self.height),
            Qt.AlignCenter,
            'Congratulation,\n you won in {:.2f} sec'.format(
                self.game.complete_time)
        )

    def debug_draw(self, qp: QPainter):
        start = mathExt.translate_point(
            self.game.turret,
            self.width,
            self.height)
        end = mathExt.translate_point(
            self.ellipse.get_coordinates(
                self.game.turret_angle,
                self.game.turret),
            self.width,
            self.height
        )
        frog_line = QtCore.QLineF(
            QtCore.QPointF(start[0], start[1]),
            QtCore.QPointF(end[0], end[1])
        )
        qp.drawLine(frog_line)

    def draw_ball(self, qp, point, radius, color):
        qp.setBrush(color)
        pen = QPen(QColor(0, 0, 0), 1, Qt.SolidLine)
        qp.setPen(pen)
        qp.drawEllipse(self.width // 2 - point[0] - radius,
                       self.height - point[1] - radius,
                       2 * radius,
                       2 * radius)

    def closeEvent(self, a0: QtGui.QCloseEvent):
        self.killTimer(self.timer)
        QtWidgets.qApp.quit()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    widget = ViewControl()
    widget.show()

    sys.exit(app.exec())
