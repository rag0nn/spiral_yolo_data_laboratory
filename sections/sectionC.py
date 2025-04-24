from PyQt6.QtCore import Qt
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget
from .section import Section

class SectionC(Section):
    def __init__(self):
        root_Widget = QWidget()
        ly = QVBoxLayout()
        root_Widget.setLayout(ly)
        self.image = QLabel("image")
        ly.addWidget(self.image,alignment=Qt.AlignmentFlag.AlignCenter)
        super().__init__(children=[root_Widget])
        self.setMaximumHeight(int(QGuiApplication.primaryScreen().geometry().height()*0.6))