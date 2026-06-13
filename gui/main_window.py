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
        self.clear_btn.clicked.connect(self.canvas.clear_canvas)
        
        # Connect save buttons with their respective transparent flags using lambda
        self.save_white_btn.clicked.connect(lambda: self.save_signature(transparent=False))
        self.save_trans_btn.clicked.connect(lambda: self.save_signature(transparent=True))
        
        self.preview_btn.clicked.connect(self.preview_signature)

        # Keyboard Shortcuts (Defaulting Ctrl+S to transparent save)
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
        clear_action.triggered.connect(self.canvas.clear_canvas)
        self.addAction(clear_action)

    def save_signature(self, transparent):
        # Validation
        valid, message = ValidationService.validate(
            self.name_input.text(),
            self.canvas.strokes
        )

        if not valid:
            QMessageBox.warning(self, "Validation", message)
            return

        # Add a suffix so you know which is which if both are saved
        suffix = "_trans" if transparent else "_white"
        filename = self.name_input.text().strip().lower().replace(" ", "_") + f"{suffix}.png"
        path = OUTPUT_FOLDER / filename
        
        image = qimage_to_pil(self.canvas.get_pixmap().toImage())
        processed = SignatureProcessor.process(image, transparent=transparent)

        # Wrap the save operation in a try/except block to catch network path issues safely
        try:
            processed.save(path, dpi=(EXPORT_DPI, EXPORT_DPI))
            QMessageBox.information(self, "Saved", f"Successfully saved to:\n{path}")
        except PermissionError:
            QMessageBox.critical(self, "Save Error", "Permission denied. You do not have write access to the target destination folder.")
        except OSError as e:
            QMessageBox.critical(self, "Network Error", f"Could not reach the destination path.\n\nError details: {str(e)}")

    def preview_signature(self):
        image = qimage_to_pil(self.canvas.get_pixmap().toImage())
        
        # Force the preview to use a white background
        processed = SignatureProcessor.process(image, transparent=False)
        
        dialog = PreviewDialog(processed, self)
        dialog.exec()