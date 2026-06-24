from PySide6.QtCore import Qt, QLineF, QPoint, Signal
from PySide6.QtGui import (
    QPainter,
    QColor,
    QPixmap,
    QPen,
    QCursor,
)
from PySide6.QtWidgets import QWidget, QSizePolicy

BRUSH_WIDTH = 8
BRUSH_ANGLE = -30

class SignatureCanvas(QWidget):
    # Emitted when the user starts the first stroke of a session
    interaction_started = Signal()

    def __init__(self):
        super().__init__()

        # Allow the widget to expand freely across the main window
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setFocusPolicy(Qt.StrongFocus)

        self.strokes = []
        self.current_stroke = []
        self.last_point = None
        
        self.drawing = False
        self.enable_physical_containment = False 

        # Initial pixmap size (will be overridden immediately by resizeEvent)
        self.canvas = QPixmap(800, 600)
        self.canvas.fill(Qt.white)

    def resizeEvent(self, event):
        """Rebuilds the canvas surface dynamically when the window is maximized or resized."""
        if event.size().isValid():
            new_pixmap = QPixmap(event.size())
            new_pixmap.fill(Qt.white)
            self.canvas = new_pixmap
            self.redraw()
        super().resizeEvent(event)

    def center_cursor(self):
        center_point = self.rect().center()
        global_pos = self.mapToGlobal(center_point)
        QCursor.setPos(global_pos)

    def focus_canvas(self):
        self.setFocus()

    def is_drawing(self) -> bool:
        return len(self.current_stroke) > 0

    def clamp_point(self, point: QPoint) -> QPoint:
        x = max(0, min(point.x(), self.width() - 1))
        y = max(0, min(point.y(), self.height() - 1))
        return QPoint(x, y)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.canvas)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.rect().contains(event.pos()):
                self.drawing = True
                
                # Hide the instructional text when the user begins signing
                if not self.strokes:
                    self.interaction_started.emit()

                self.current_stroke = [event.pos()]
                self.last_point = event.pos()
                self._stamp_at(event.pos())

    def mouseMoveEvent(self, event):
        if self.drawing and (event.buttons() & Qt.LeftButton):
            clamped_pos = self.clamp_point(event.pos())
            
            if self.enable_physical_containment and clamped_pos != event.pos():
                global_pos = self.mapToGlobal(clamped_pos)
                QCursor.setPos(global_pos)

            self.current_stroke.append(clamped_pos)
            self._draw_segment(self.last_point, clamped_pos)
            self.last_point = clamped_pos

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.drawing:
            self.drawing = False
            if self.current_stroke:
                self.strokes.append(self.current_stroke.copy())
                self.current_stroke = []
                self.last_point = None

    def _draw_segment(self, p1, p2):
        line = QLineF(p1, p2)
        dist = line.length()
        steps = max(1, int(dist))
        for i in range(steps + 1):
            t = i / steps
            point = p1 + (p2 - p1) * t
            self._stamp_at(point)

    def _stamp_at(self, point):
        painter = QPainter(self.canvas)
        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen(QColor("black"), 1.5, Qt.SolidLine, Qt.RoundCap)
        painter.setPen(pen)
        painter.save()
        painter.translate(point)
        painter.rotate(BRUSH_ANGLE)
        painter.drawLine(QLineF(-BRUSH_WIDTH / 2, 0, BRUSH_WIDTH / 2, 0))
        painter.restore()
        painter.end()
        self.update()

    def redraw(self):
        self.canvas.fill(Qt.white)
        for stroke in self.strokes:
            for i in range(len(stroke) - 1):
                self._draw_segment(stroke[i], stroke[i+1])
        self.update()

    def clear_canvas(self):
        self.strokes.clear()
        self.current_stroke.clear()
        self.canvas.fill(Qt.white)
        self.update()

    def undo(self):
        if self.strokes:
            self.strokes.pop()
            self.redraw()
            if not self.strokes:
                self.interaction_started.emit()  # Can re-show label if empty

    def get_pixmap(self):
        return self.canvas