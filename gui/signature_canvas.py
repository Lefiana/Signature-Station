from PySide6.QtCore import Qt, QLineF
from PySide6.QtGui import (
    QPainter,
    QColor,
    QPixmap,
    QPen,
)
from PySide6.QtWidgets import QWidget

# Ensure your config file has these defined
from config import (
    CANVAS_WIDTH,
    CANVAS_HEIGHT,
)

# --- Calligraphy Brush Settings ---
# BRUSH_WIDTH acts as the "flat edge" of the nib. 
# Increase to 8, 10, or 12 for a more pronounced thick/thin contrast.
BRUSH_WIDTH = 8
BRUSH_ANGLE = -30

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
        """Calculates the distance and fills the gap with flat line stamps."""
        line = QLineF(p1, p2)
        dist = line.length()
        
        # Stamps along the line. 
        # Increase the step multiplier (e.g., int(dist * 2)) if you draw incredibly fast and still see gaps.
        steps = max(1, int(dist))
        for i in range(steps + 1):
            t = i / steps
            # Linear interpolation between p1 and p2
            point = p1 + (p2 - p1) * t
            self._stamp_at(point)

    def _stamp_at(self, point):
        """Draws a flat line segment (true calligraphy nib)."""
        painter = QPainter(self.canvas)
        
        # Comment this line out if you want the sharper, pixelated MS Paint look:
        painter.setRenderHint(QPainter.Antialiasing)
        
        # The 1.5px pen dictates the absolute thinnest part of the stroke.
        pen = QPen(QColor("black"), 1.5, Qt.SolidLine, Qt.RoundCap)
        painter.setPen(pen)

        painter.save()
        painter.translate(point)
        painter.rotate(BRUSH_ANGLE)
        
        # Stamp a flat line acting as the "edge" of the calligraphy nib
        painter.drawLine(QLineF(-BRUSH_WIDTH / 2, 0, BRUSH_WIDTH / 2, 0))
        
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