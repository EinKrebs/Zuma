import sys
import PyQt5.QtWidgets

from window import ViewControl

if __name__ == '__main__':
    args = sys.argv
    app = PyQt5.QtWidgets.QApplication(sys.argv)
    if len(sys.argv) == 2:
        widget = ViewControl(sys.argv[1])
    else:
        widget = ViewControl()

    widget.show()

    sys.exit(app.exec_())
