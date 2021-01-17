import sys
import argparse
import PyQt5.QtWidgets

from window import ViewControl

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--directory', '-d', type=str, action='append',
                        help='add directories containing only level files')
    parser.add_argument('--file', '-f', type=str, action='append',
                        help='add files with level')
    args = parser.parse_args()
    if args.directory is None and args.file is None:
        directories = ['levels']
    else:
        directories = args.directory
    if directories is None:
        directories = []
    files = args.file if args.file is not None else []
    app = PyQt5.QtWidgets.QApplication(sys.argv)
    widget = ViewControl(directories, files)

    widget.show()

    sys.exit(app.exec_())
