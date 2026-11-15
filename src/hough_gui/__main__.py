"""`python3 -m hough_gui` 入口。"""

import os
import sys

from PyQt5.QtGui import QFont, QFontDatabase
from PyQt5.QtWidgets import QApplication

from hough_gui.ui.main_window import MainWindow

# WSL2 的 WSLg 不注册 Windows 字体；系统未装中文字体时按顺序尝试这些字体。
HOST_FONT_CANDIDATES = (
    "/mnt/c/Windows/Fonts/msyh.ttc",
    "/mnt/c/Windows/Fonts/NotoSansSC-VF.ttf",
    "/mnt/c/Windows/Fonts/simsun.ttc",
    "/mnt/c/Windows/Fonts/Deng.ttf",
)


def _ensure_cjk_font(app: QApplication) -> None:
    """系统中没有可显示简体中文的字体时，加载宿主 Windows 字体，避免界面中文变方框。"""
    database = QFontDatabase()
    if any(
        QFontDatabase.SimplifiedChinese in database.writingSystems(family)
        for family in database.families()
    ):
        return
    for path in HOST_FONT_CANDIDATES:
        if not os.path.exists(path):
            continue
        font_id = database.addApplicationFont(path)
        if font_id == -1:
            continue
        families = database.applicationFontFamilies(font_id)
        if not families:
            continue
        font = app.font()
        font.setFamily(families[0])
        app.setFont(font)
        return


def main() -> int:
    app = QApplication(sys.argv)
    _ensure_cjk_font(app)
    window = MainWindow()
    window.show()
    return app.exec_()


if __name__ == "__main__":
    raise SystemExit(main())
