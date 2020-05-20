import sys
import PyQt5.QtWidgets

from Window import ViewControl
import Tests

if __name__ == '__main__':
    args = sys.argv
    if len(args) == 1 or (len(args) == 2 and args[1] != 'pytest'):
        app = PyQt5.QtWidgets.QApplication(sys.argv)
        if len(sys.argv) == 2:
            widget = ViewControl(sys.argv[1])
        else:
            widget = ViewControl()

        widget.show()

        sys.exit(app.exec_())

    elif len(args) == 2:
        Tests
    else:
        raise ValueError

