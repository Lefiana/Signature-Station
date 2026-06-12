from pathlib import Path
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
)
from PIL import Image

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

        # Input and Canvas
        layout.addWidget(QLabel("Employee Name"))
        self.name_input = QLineEdit()
        layout.addWidget(self.name_input)
        
        self.canvas = SignatureCanvas()
        layout.addWidget(self.canvas)

        # Buttons Definition
        buttons = QHBoxLayout()
        self.undo_btn = QPushButton("Undo")
        self.clear_btn = QPushButton("Clear")
        self.save_btn = QPushButton("Save")
        self.preview_btn = QPushButton("Preview")

        buttons.addWidget(self.undo_btn)
        buttons.addWidget(self.clear_btn)
        buttons.addWidget(self.save_btn)
        buttons.addWidget(self.preview_btn)
        layout.addLayout(buttons)

        # Connections
        self.undo_btn.clicked.connect(self.canvas.undo)
        self.clear_btn.clicked.connect(self.canvas.clear_canvas)
        self.save_btn.clicked.connect(self.save_signature)
        self.preview_btn.clicked.connect(self.preview_signature)

        # Keyboard Shortcuts
        undo_action = QAction(self)
        undo_action.setShortcut(QKeySequence("Ctrl+Z"))
        undo_action.triggered.connect(self.canvas.undo)
        self.addAction(undo_action)

        save_action = QAction(self)
        save_action.setShortcut(QKeySequence("Ctrl+S"))
        save_action.triggered.connect(self.save_signature)
        self.addAction(save_action)

        clear_action = QAction(self)
        clear_action.setShortcut(QKeySequence("Ctrl+N"))
        clear_action.triggered.connect(self.canvas.clear_canvas)
        self.addAction(clear_action)

    def save_signature(self):
        # Validation
        valid, message = ValidationService.validate(
            self.name_input.text(),
            self.canvas.strokes
        )

        if not valid:
            QMessageBox.warning(self, "Validation", message)
            return

        filename = self.name_input.text().strip().lower().replace(" ", "_") + ".png"
        path = OUTPUT_FOLDER / filename

        # Optimized Conversion
        image = qimage_to_pil(self.canvas.get_pixmap().toImage())

        processed = SignatureProcessor.process(image)
        processed.save(path, dpi=(EXPORT_DPI, EXPORT_DPI))

        QMessageBox.information(self, "Saved", f"Saved:\n{path}")

    def preview_signature(self):
        image = qimage_to_pil(self.canvas.get_pixmap().toImage())
        processed = SignatureProcessor.process(image)
        
        dialog = PreviewDialog(processed, self)
        dialog.exec()