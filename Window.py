import sys
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QApplication, QLabel
from PyQt5.QtGui import QPainter, QPaintEvent, QFont, QPen, QColor, QPixmap,\
    QTransform
from PyQt5.QtCore import Qt, QTimer
import math

from Ellipse import Ellipse
from Level import Level
from Game import Game
import MathExtentions as mathExt


class ViewControl(QWidget):
    def __init__(self, file='level_description.txt'):
        super().__init__()

        self.text = 'Hello world!'
        self.width = 800
        self.height = 600
        self.setGeometry(100, 100, self.width, self.height)
        self.setWindowTitle('Zuma')
        # self.image = QtGui.QImage("Frog.jpg")
        self.image = QLabel(self)
        self.image.setAlignment(Qt.AlignCenter)
        self.pixmap = None
        self.running = True

        self.next_btn = None
        self.initialise_button()

        with open(file) as f:
            self.game = Game.from_string_array(f.readlines())

        self.timer = self.startTimer(10)

        self.show()

    @property
    def ellipse(self) -> Ellipse:
        return self.game.current_level.ellipse

    @property
    def current_level(self) -> Level:
        return self.game.current_level

    def initialise_button(self):
        self.next_btn = QtWidgets.QPushButton('Next Level', self)

        def next_pressed():
            self.game.next_level()
            self.next_btn.hide()

        self.next_btn.clicked.connect(next_pressed)
        self.next_btn.hide()

    def timerEvent(self, e):
        self.update()
        QApplication.processEvents()
        self.game.update()

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        current_level = self.current_level
        if not current_level:
            return
        if event.key() == 0x41:  # A
            current_level.left = True
            current_level.right = False
        elif event.key() == 0x44:  # D
            current_level.right = True
            current_level.left = False
        elif event.key() == 0x20:  # Space
            current_level.shoot()

    def keyReleaseEvent(self, event: QtGui.QKeyEvent):
        current_level = self.current_level
        if not current_level:
            return
        if event.key() == 0x41:  # A
            current_level.left = False
        elif event.key() == 0x44:  # D
            current_level.right = False

    def wheelEvent(self, event: QtGui.QWheelEvent):
        current_level = self.current_level
        if not current_level:
            return
        current_level.turn_turret(
            current_level.turret_speed * event.angleDelta().y() / 50)

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        current_level = self.current_level
        if not current_level:
            return
        if event.button() == Qt.LeftButton:
            current_level.shoot()

    def paintEvent(self, event: QPaintEvent):
        qp = QPainter()
        qp.begin(self)

        if self.game.over == 1:
            self.draw_game_won(qp)
        elif not self.game.running:
            self.draw_level_completed(qp)
        elif self.game.over == -1:
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
            f'HP: {self.current_level.hp}\nScore:{self.current_level.score}')

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
        self.image.move(self.width // 2 - self.current_level.turret[
            0] - self.image.width() // 2,
                        self.height - self.current_level.turret[
                            1] - self.image.height() // 2)
        t = QTransform().rotate((self.current_level.turret_angle - math.pi / 2
                                 ) / math.pi * 180)

        self.image.setPixmap(self.pixmap.transformed(t))

    def draw_balls(self, event, qp):
        for ball in self.current_level.balls:
            self.draw_ball(qp,
                           ball.point,
                           self.current_level.radius,
                           QColor(*ball.color))
        for shot in self.current_level.shots:
            self.draw_ball(qp,
                           (shot.x, shot.y),
                           self.current_level.radius,
                           QColor(*shot.color))

    def draw_game_over(self, qp: QPainter):
        qp.setFont(QFont('Segoe UI', 30))
        qp.drawText(
            QtCore.QRect(0, 0, self.width, self.height),
            Qt.AlignCenter,
            'GAME OVER'
        )

    def draw_level_completed(self, qp: QPainter):
        self.next_btn.show()
        qp.setFont(QFont('Segoe UI', 30))
        qp.drawText(
            QtCore.QRect(0, 0, self.width, self.height),
            Qt.AlignCenter,
            'Congratulations,\n you won in {:.2f} sec'.format(
                self.current_level.complete_time)
        )

    def draw_game_won(self, qp: QPainter):
        qp.setFont(QFont('Segoe UI', 30))
        qp.drawText(
            QtCore.QRect(0, 0, self.width, self.height),
            Qt.AlignCenter,
            'Congratulations,\n you won the game!'
        )

    def debug_draw(self, qp: QPainter):
        start = mathExt.translate_point(
            self.current_level.turret,
            self.width,
            self.height)
        end = mathExt.translate_point(
            self.ellipse.get_coordinates(
                self.current_level.turret_angle,
                self.current_level.turret),
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

    if len(sys.argv) > 1:
        widget = ViewControl(sys.argv[1])
    else:
        widget = ViewControl()
    widget.show()

    sys.exit(app.exec())
