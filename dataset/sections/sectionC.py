from PyQt6.QtGui import QGuiApplication
from PyQt6.QtWidgets import QLabel
from .section import Section

class SectionC(Section):
    def __init__(self):
        self.image = QLabel("image")
        super().__init__(children=[self.image])
        self.setMaximumHeight(int(QGuiApplication.primaryScreen().geometry().height()*0.6))