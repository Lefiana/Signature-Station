from io import BytesIO

from PySide6.QtGui import (
    QPixmap,
)

from PySide6.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QDialog,
)

from PIL.ImageQt import ImageQt


class PreviewDialog(QDialog):

    def __init__(
        self,
        pil_image,
        parent=None
    ):
        super().__init__(parent)

        self.setWindowTitle(
            "Preview"
        )

        self.resize(
            500,
            250
        )

        layout = QVBoxLayout()

        qt_image = ImageQt(
            pil_image
        )

        pixmap = QPixmap.fromImage(
            qt_image
        )

        label = QLabel()

        label.setPixmap(
            pixmap.scaled(
                450,
                180
            )
        )

        layout.addWidget(
            label
        )

        self.setLayout(
            layout
        )