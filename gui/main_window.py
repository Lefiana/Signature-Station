from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QMessageBox,
)
from PySide6.QtGui import (
    QKeySequence,
    QAction,
    QFont,
)

from gui.signature_canvas import SignatureCanvas
from gui.preview_dialog import PreviewDialog
from processing.signature_processor import SignatureProcessor
from processing.image_conversion import qimage_to_pil
from services.validation_service import ValidationService
from config import OUTPUT_FOLDER, EXPORT_DPI

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Signature Capture Station")

        # Layout Setup
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()
        central.setLayout(layout)

        # Header Details
        layout.addWidget(QLabel("Employee Name:"))
        self.name_input = QLineEdit()
        layout.addWidget(self.name_input)
        
        # Subtle Instructional Label
        self.instruction_label = QLabel("Please sign anywhere in the white area below.")
        self.instruction_label.setAlignment(Qt.AlignCenter)
        self.instruction_label.setStyleSheet("color: #666666; margin-top: 10px; margin-bottom: 5px;")
        font = QFont()
        font.setPointSize(11)
        font.setItalic(True)
        self.instruction_label.setFont(font)
        layout.addWidget(self.instruction_label)

        # The large expanding signature canvas
        self.canvas = SignatureCanvas()
        layout.addWidget(self.canvas)

        # Canvas Signals
        self.canvas.interaction_started.connect(self.handle_canvas_interaction)

        # Buttons Definition
        buttons = QHBoxLayout()
        self.undo_btn = QPushButton("Undo")
        self.clear_btn = QPushButton("Clear")
        self.save_white_btn = QPushButton("Save (White)")
        self.save_trans_btn = QPushButton("Save (Trans)")
        self.preview_btn = QPushButton("Preview")

        buttons.addWidget(self.undo_btn)
        buttons.addWidget(self.clear_btn)
        buttons.addWidget(self.save_white_btn)
        buttons.addWidget(self.save_trans_btn)
        buttons.addWidget(self.preview_btn)
        layout.addLayout(buttons)

        # Connections
        self.undo_btn.clicked.connect(self.canvas.undo)
        self.clear_btn.clicked.connect(self.reset_session)
        
        self.save_white_btn.clicked.connect(lambda: self.save_signature(transparent=False))
        self.save_trans_btn.clicked.connect(lambda: self.save_signature(transparent=True))
        self.preview_btn.clicked.connect(self.preview_signature)

        # Keyboard Shortcuts
        undo_action = QAction(self)
        undo_action.setShortcut(QKeySequence("Ctrl+Z"))
        undo_action.triggered.connect(self.canvas.undo)
        self.addAction(undo_action)

        save_action = QAction(self)
        save_action.setShortcut(QKeySequence("Ctrl+S"))
        save_action.triggered.connect(lambda: self.save_signature(transparent=True))
        self.addAction(save_action)

        clear_action = QAction(self)
        clear_action.setShortcut(QKeySequence("Ctrl+N"))
        clear_action.triggered.connect(self.reset_session)
        self.addAction(clear_action)

        # Start maximized so the expanding layout fills the monitor
        self.showMaximized()

    def showEvent(self, event):
        super().showEvent(event)
        self.canvas.focus_canvas()
        self.canvas.center_cursor()

    def enterEvent(self, event):
        super().enterEvent(event)
        local_pos = self.canvas.mapFromGlobal(self.cursor().pos())
        if not self.canvas.rect().contains(local_pos) and not self.canvas.is_drawing():
            self.canvas.center_cursor()
            self.canvas.focus_canvas()

    def handle_canvas_interaction(self):
        """Hides or shows the instruction label based on whether strokes exist."""
        if self.canvas.strokes or self.canvas.is_drawing():
            self.instruction_label.hide()
        else:
            self.instruction_label.show()

    def reset_session(self):
        self.canvas.clear_canvas()
        self.instruction_label.show()
        self.canvas.focus_canvas()
        self.canvas.center_cursor()

    def save_signature(self, transparent):
        valid, message = ValidationService.validate(self.name_input.text(), self.canvas.strokes)

        if not valid:
            QMessageBox.warning(self, "Validation", message)
            return

        suffix = ".sigg_trans" if transparent else ".sigg_white"
        filename = self.name_input.text().strip().lower().replace(" ", "_") + f"{suffix}.png"
        path = OUTPUT_FOLDER / filename
        
        image = qimage_to_pil(self.canvas.get_pixmap().toImage())
        processed = SignatureProcessor.process(image, transparent=transparent)

        try:
            processed.save(path, dpi=(EXPORT_DPI, EXPORT_DPI))
            QMessageBox.information(self, "Saved", f"Successfully saved to:\n{path}")
            
            self.name_input.clear()
            self.reset_session()

        except PermissionError:
            QMessageBox.critical(self, "Save Error", "Permission denied.")
        except OSError as e:
            QMessageBox.critical(self, "Network Error", f"Could not reach destination.\n{str(e)}")

    def preview_signature(self):
        image = qimage_to_pil(self.canvas.get_pixmap().toImage())
        processed = SignatureProcessor.process(image, transparent=False)
        
        dialog = PreviewDialog(processed, self)
        dialog.exec()