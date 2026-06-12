from io import BytesIO

from PIL import Image

from PySide6.QtCore import (
    QByteArray,
    QBuffer,
    QIODevice,
)


def qimage_to_pil(qimage):

    byte_array = QByteArray()

    buffer = QBuffer(byte_array)

    buffer.open(
        QIODevice.WriteOnly
    )

    qimage.save(
        buffer,
        "PNG"
    )

    buffer.close()

    return Image.open(
        BytesIO(
            byte_array.data()
        )
    ).convert("RGBA")