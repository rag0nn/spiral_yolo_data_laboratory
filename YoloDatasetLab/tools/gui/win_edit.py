from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel,
    QTextEdit, QLineEdit, QHBoxLayout, QSizePolicy,
     QScrollArea, QFrame
)

class EditWinWidget(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        layout = QVBoxLayout()
        label = QLabel("Bu bir edit dummy widget'tır.")
        layout.addWidget(label)
        self.setLayout(layout)