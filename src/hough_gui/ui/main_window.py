"""主窗口：参数面板、叠加预览、后台检测与导出。"""

import os
import time

import cv2
from PyQt5.QtCore import Qt, QThread, QTimer, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (
    QAction,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QSizePolicy,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from hough_gui.core.detector import detect_circles
from hough_gui.core.imageio import load_image, render_overlay, save_annotated
from hough_gui.core.params import HoughParams

DEBOUNCE_MS = 150
IMAGE_FILTER = "图片 (*.png *.jpg *.jpeg *.bmp *.tif *.tiff)"


class DetectThread(QThread):
    """在后台线程执行一次检测，并通过信号把代次、圆列表与耗时送回主线程。"""

    finished_result = pyqtSignal(int, list, float)

    def __init__(self, generation: int, image, params: HoughParams, parent=None):
        super().__init__(parent)
        self._generation = generation
        self._image = image
        self._params = params

    def run(self) -> None:
        start = time.perf_counter()
        circles = detect_circles(self._image, self._params)
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        self.finished_result.emit(self._generation, circles, elapsed_ms)


def _int_spin(minimum: int, maximum: int) -> QSpinBox:
    spin = QSpinBox()
    spin.setRange(minimum, maximum)
    return spin


def _double_spin(minimum: float, maximum: float, step: float, decimals: int) -> QDoubleSpinBox:
    spin = QDoubleSpinBox()
    spin.setRange(minimum, maximum)
    spin.setSingleStep(step)
    spin.setDecimals(decimals)
    return spin


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # WSLg 的标题栏由 Weston 绘制，不支持中文字形，中文标题会显示为方框，故标题用英文。
        self.setWindowTitle("Hough Circle Detection")
        self.resize(1100, 720)

        self._image = None
        self._overlay = None
        self._source_path = ""
        self._generation = 0
        self._thread = None
        self._pending = False

        self._debounce = QTimer(self)
        self._debounce.setSingleShot(True)
        self._debounce.setInterval(DEBOUNCE_MS)
        self._debounce.timeout.connect(self._start_detection)

        self._build_ui()
        self._apply_defaults()

    # ---- 界面构建 ----

    def _build_ui(self) -> None:
        open_action = QAction("打开图片", self)
        open_action.triggered.connect(self._open_image)
        self._export_action = QAction("导出标注图", self)
        self._export_action.setEnabled(False)
        self._export_action.triggered.connect(self._export_annotated)

        toolbar = self.addToolBar("操作")
        toolbar.setMovable(False)
        toolbar.setToolButtonStyle(Qt.ToolButtonTextOnly)
        toolbar.addAction(open_action)
        toolbar.addAction(self._export_action)

        self._dp = _double_spin(1.0, 3.0, 0.1, 1)
        self._min_dist = _int_spin(1, 2000)
        self._param1 = _int_spin(1, 500)
        self._param2 = _int_spin(1, 200)
        self._min_radius = _int_spin(0, 2000)
        self._max_radius = _int_spin(0, 2000)
        self._param_widgets = [
            self._dp,
            self._min_dist,
            self._param1,
            self._param2,
            self._min_radius,
            self._max_radius,
        ]
        for widget in self._param_widgets:
            widget.valueChanged.connect(self._on_param_changed)

        form = QFormLayout()
        form.addRow("dp", self._dp)
        form.addRow("minDist", self._min_dist)
        form.addRow("param1", self._param1)
        form.addRow("param2", self._param2)
        form.addRow("minRadius", self._min_radius)
        form.addRow("maxRadius", self._max_radius)

        self._error_label = QLabel("")
        self._error_label.setStyleSheet("color: #c0392b;")
        self._error_label.setWordWrap(True)

        panel = QWidget()
        panel_layout = QVBoxLayout(panel)
        panel_layout.addLayout(form)
        panel_layout.addWidget(self._error_label)
        panel_layout.addStretch(1)
        panel.setMaximumWidth(300)

        self._preview = QLabel()
        self._preview.setAlignment(Qt.AlignCenter)
        self._preview.setMinimumSize(320, 240)
        self._preview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        central = QWidget()
        layout = QHBoxLayout(central)
        layout.addWidget(panel, 0)
        layout.addWidget(self._preview, 1)
        self.setCentralWidget(central)

        self._file_label = QLabel("图片: -")
        self._result_label = QLabel("圆: -")
        self.statusBar().addWidget(self._file_label)
        self.statusBar().addPermanentWidget(self._result_label)

    def _apply_defaults(self) -> None:
        defaults = HoughParams()
        self._dp.setValue(defaults.dp)
        self._min_dist.setValue(defaults.min_dist)
        self._param1.setValue(defaults.param1)
        self._param2.setValue(defaults.param2)
        self._min_radius.setValue(defaults.min_radius)
        self._max_radius.setValue(defaults.max_radius)

    # ---- 参数与检测 ----

    def _collect_params(self) -> HoughParams:
        return HoughParams(
            dp=self._dp.value(),
            min_dist=self._min_dist.value(),
            param1=self._param1.value(),
            param2=self._param2.value(),
            min_radius=self._min_radius.value(),
            max_radius=self._max_radius.value(),
        )

    def _on_param_changed(self, *_args) -> None:
        errors = self._collect_params().validate()
        self._error_label.setText("\n".join(errors))
        if errors or self._image is None:
            self._debounce.stop()
            return
        self._debounce.start()

    def _start_detection(self) -> None:
        if self._image is None:
            return
        params = self._collect_params()
        errors = params.validate()
        self._error_label.setText("\n".join(errors))
        if errors:
            return
        if self._thread is not None and self._thread.isRunning():
            self._pending = True
            return
        self._generation += 1
        thread = DetectThread(self._generation, self._image.copy(), params, self)
        thread.finished_result.connect(self._on_detection_finished)
        thread.finished.connect(self._on_thread_stopped)
        self._thread = thread
        thread.start()

    def _on_detection_finished(self, generation: int, circles: list, elapsed_ms: float) -> None:
        if generation != self._generation:
            return
        self._overlay = render_overlay(self._image, circles)
        self._result_label.setText(f"圆: {len(circles)} | 耗时: {elapsed_ms:.1f} ms")
        self._update_preview()

    def _on_thread_stopped(self) -> None:
        thread = self._thread
        self._thread = None
        if thread is not None:
            thread.deleteLater()
        if self._pending:
            self._pending = False
            self._start_detection()

    # ---- 预览 ----

    def _update_preview(self) -> None:
        if self._overlay is None:
            return
        rgb = cv2.cvtColor(self._overlay, cv2.COLOR_BGR2RGB)
        height, width = rgb.shape[:2]
        image = QImage(rgb.data, width, height, 3 * width, QImage.Format_RGB888).copy()
        pixmap = QPixmap.fromImage(image)
        self._preview.setPixmap(
            pixmap.scaled(self._preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._update_preview()

    # ---- 动作 ----

    def _open_image(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "打开图片", self._source_path, IMAGE_FILTER)
        if not path:
            return
        try:
            image = load_image(path)
        except ValueError as exc:
            QMessageBox.critical(self, "打开失败", str(exc))
            return

        self._image = image
        self._source_path = path
        self._overlay = None
        self._generation += 1
        height, width = image.shape[:2]
        self._file_label.setText(f"图片: {os.path.basename(path)} ({width}×{height})")
        self._result_label.setText("圆: -")
        self._preview.clear()
        self._export_action.setEnabled(True)
        self._start_detection()

    def _export_annotated(self) -> None:
        image = self._overlay if self._overlay is not None else self._image
        if image is None:
            return
        stem = os.path.splitext(self._source_path)[0] if self._source_path else ""
        default = f"{stem}_circles.png" if stem else "circles.png"
        path, _ = QFileDialog.getSaveFileName(self, "导出标注图", default, "PNG 图片 (*.png)")
        if not path:
            return
        if not path.lower().endswith(".png"):
            path += ".png"
        try:
            save_annotated(path, image)
        except Exception as exc:  # noqa: BLE001 - 展示给用户即可
            QMessageBox.critical(self, "导出失败", str(exc))
            return
        self.statusBar().showMessage(f"已导出: {path}", 5000)

    def closeEvent(self, event) -> None:
        thread = self._thread
        if thread is not None and thread.isRunning():
            thread.wait()
        super().closeEvent(event)
