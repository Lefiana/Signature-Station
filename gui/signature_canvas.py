from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import (
    QPainter,
    QPen,
    QColor,
    QPixmap,
)
from PySide6.QtWidgets import QWidget

from config import (
    CANVAS_WIDTH,
    CANVAS_HEIGHT,
    PEN_WIDTH,
)


class SignatureCanvas(QWidget):

    def __init__(self):
        super().__init__()

        self.setFixedSize(
            CANVAS_WIDTH,
            CANVAS_HEIGHT,
        )

        self.strokes = []
        self.current_stroke = []

        self.canvas = QPixmap(
            CANVAS_WIDTH,
            CANVAS_HEIGHT,
        )

        self.canvas.fill(Qt.white)

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.drawPixmap(
            0,
            0,
            self.canvas,
        )

    def mousePressEvent(self, event):

        if event.button() == Qt.LeftButton:

            self.current_stroke = [event.pos()]

    def mouseMoveEvent(self, event):

        if event.buttons() & Qt.LeftButton:

            self.current_stroke.append(
                event.pos()
            )

            self.redraw()

    def mouseReleaseEvent(self, event):

        if self.current_stroke:

            self.strokes.append(
                self.current_stroke.copy()
            )

            self.current_stroke = []

            self.redraw()

    def redraw(self):

        self.canvas.fill(Qt.white)

        painter = QPainter(self.canvas)

        pen = QPen(
            QColor("black"),
            PEN_WIDTH,
            Qt.SolidLine,
            Qt.RoundCap,
            Qt.RoundJoin,
        )

        painter.setPen(pen)

        for stroke in self.strokes:

            for i in range(
                len(stroke) - 1
            ):
                painter.drawLine(
                    stroke[i],
                    stroke[i + 1]
                )

        if len(self.current_stroke) > 1:

            for i in range(
                len(self.current_stroke) - 1
            ):
                painter.drawLine(
                    self.current_stroke[i],
                    self.current_stroke[i + 1]
                )

        painter.end()

        self.update()

    def clear_canvas(self):

        self.strokes.clear()
        self.current_stroke.clear()

        self.redraw()

    def undo(self):

        if self.strokes:

            self.strokes.pop()

            self.redraw()

    def get_pixmap(self):

        return self.canvas