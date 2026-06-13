from PySide6.QtCore import Qt, QPoint, QLineF
from PySide6.QtGui import (
    QPainter,
    QColor,
    QPixmap,
    QBrush,
)
from PySide6.QtWidgets import QWidget

# Ensure your config file has these defined
from config import (
    CANVAS_WIDTH,
    CANVAS_HEIGHT,
)

# --- Calligraphy Brush Settings ---
# Adjust these to match the "weight" of your desired signature
BRUSH_WIDTH = 6
BRUSH_HEIGHT = 2
BRUSH_ANGLE = -30  # Angle in degrees for the tilted ellipse (negative for left tilt)

class SignatureCanvas(QWidget):
    def __init__(self):
        super().__init__()

        self.setFixedSize(CANVAS_WIDTH, CANVAS_HEIGHT)

        self.strokes = []
        self.current_stroke = []
        self.last_point = None

        self.canvas = QPixmap(CANVAS_WIDTH, CANVAS_HEIGHT)
        self.canvas.fill(Qt.white)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.canvas)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.current_stroke = [event.pos()]
            self.last_point = event.pos()
            self._stamp_at(event.pos())

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            new_point = event.pos()
            self.current_stroke.append(new_point)
            
            # Fill the gap between the last point and the current point
            self._draw_segment(self.last_point, new_point)
            self.last_point = new_point

    def mouseReleaseEvent(self, event):
        if self.current_stroke:
            self.strokes.append(self.current_stroke.copy())
            self.current_stroke = []
            self.last_point = None

    def _draw_segment(self, p1, p2):
        """Calculates the distance and fills the gap with stamps."""
        line = QLineF(p1, p2)
        dist = line.length()
        
        # Stamps along the line
        steps = max(1, int(dist))
        for i in range(steps + 1):
            t = i / steps
            # Linear interpolation between p1 and p2
            point = p1 + (p2 - p1) * t
            self._stamp_at(point)

    def _stamp_at(self, point):
        """Draws the tilted ellipse at a specific coordinate."""
        painter = QPainter(self.canvas)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(QColor("black")))
        painter.setPen(Qt.NoPen)

        painter.save()
        painter.translate(point)
        painter.rotate(BRUSH_ANGLE)
        painter.drawEllipse(
            -BRUSH_WIDTH // 2, 
            -BRUSH_HEIGHT // 2, 
            BRUSH_WIDTH, 
            BRUSH_HEIGHT
        )
        painter.restore()
        painter.end()
        self.update()

    def redraw(self):
        """Rebuilds the canvas from the strokes list (used for undo/clear)."""
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

    def get_pixmap(self):
        return self.canvas