import math
from threading import Thread

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPaintEvent, QFont, QPen, QColor, QPixmap, \
    QTransform
from PyQt5.QtWidgets import QWidget, QApplication, QLabel

import MathExtentions as mathExt
from Ellipse import Ellipse
from Game import Game
from Level import Level


class ViewControl(QWidget):
    def __init__(self, directory='levels'):
        super().__init__()

        self.text = 'Hello world!'
        self.width = 800
        self.height = 600
        self.setGeometry(100, 100, self.width, self.height)
        self.setWindowTitle('Zuma')
        self.image = QLabel(self)
        self.image.setAlignment(Qt.AlignCenter)
        self.pixmap = None
        self.running = True
        self.setFixedSize(self.width, self.height)

        self.p = None
        self.next_btn = None
        self.initialise_button()

        self.game = Game.from_directory(directory)

        self.timer = self.startTimer(10)

        self.penetrate = False

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
        if self.p:
            self.p.join()
        self.update()
        QApplication.processEvents()
        self.p = Thread(target=self.game.update)
        self.p.start()

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
            current_level.shoot(self.penetrate)
        elif event.key() == 0x01000020:  # Shift
            self.penetrate = True

    def keyReleaseEvent(self, event: QtGui.QKeyEvent):
        current_level = self.current_level
        if not current_level:
            return
        if event.key() == 0x41:  # A
            current_level.left = False
        elif event.key() == 0x44:  # D
            current_level.right = False
        elif event.key() == 0x01000020:  # Shift
            self.penetrate = False

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
            current_level.shoot(self.penetrate)

    def paintEvent(self, event: QPaintEvent):
        qp = QPainter()
        qp.begin(self)

        if self.game.over == 1:
            self.draw_game_won(qp)
        elif not self.game.running:
            self.draw_level_completed(qp)
        elif self.game.over == -1:
            self.draw_stats(qp)
            self.draw_game(qp)
            self.draw_frog(qp)
            self.debug_draw(qp)
        else:
            self.draw_game_over(qp)

        qp.end()

    def draw_stats(self, qp):
        qp.setFont(QFont('Segoe UI', 16))
        qp.drawText(
            QtCore.QRect(0, 0, 100, 100),
            Qt.AlignCenter,
            f'HP: {self.current_level.hp}\n'
            f'Score:{self.current_level.score}')

    def draw_game(self, qp):
        self.draw_ellipse(qp)
        self.draw_balls(qp)

    def draw_ellipse(self, qp):
        pen = QPen(QColor(0, 0, 0), 4, Qt.SolidLine)
        qp.setPen(pen)
        size = self.size()
        qp.drawEllipse(size.width() // 2 - self.ellipse.width,
                       size.height() - self.ellipse.height,
                       2 * self.ellipse.width, 2 * self.ellipse.height)

    def draw_frog(self, qp):
        self.pixmap = QPixmap('Frog.png')
        self.image.resize(self.pixmap.width() * math.sqrt(2),
                          self.pixmap.height() * math.sqrt(2))
        self.image.move(self.width // 2 - self.current_level.turret[
            0] - self.image.width() // 2,
                        self.height - self.current_level.turret[
                            1] - self.image.height() // 2)
        t = QTransform().rotate((self.current_level.turret_angle - math.pi / 2
                                 ) / math.pi * 180)

        self.image.setPixmap(self.pixmap.transformed(t))
        if len(self.current_level.current_colors) == 0:
            return
        transform = qp.transform()
        qp.translate(
            self.width // 2 - self.current_level.turret[
                0],
            self.height - self.current_level.turret[
                1])
        qp.rotate(self.current_level.turret_angle / math.pi * 180)
        qp.setBrush(
            QColor(*self.current_level.current_colors[
                self.current_level.turret_ball]))
        qp.drawEllipse(QtCore.QPoint(0, 0), 2, 2)
        qp.drawEllipse(QtCore.QPointF(38, 0), 19, 17)
        qp.setTransform(transform)

    def draw_balls(self, qp):
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
            'Congratulations,\n you won the game!\n'
            f'Your final score is {self.game.score}'
        )

    def debug_draw(self, qp: QPainter):
        pen = QPen(QColor(0, 0, 0), 4, Qt.SolidLine)
        qp.setPen(pen)
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
