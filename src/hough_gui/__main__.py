"""`python3 -m hough_gui` 入口。"""

import sys

from PyQt5.QtWidgets import QApplication

from hough_gui.ui.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec_()


if __name__ == "__main__":
    raise SystemExit(main())
