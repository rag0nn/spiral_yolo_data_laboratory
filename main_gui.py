from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QComboBox, QHBoxLayout, QApplication, QTextEdit
)

from tools.gui.constants import MainWinTexts
from tools.gui.styles import MainWinStyles
from tools.utils import get_conf
from tools.enums import Category
from operations_gui import MainAttributes
import sys
from PyQt6.QtWidgets import QLabel
from tools.gui.win_edit import EditWinWidget
from tools.gui.win_model import ModelWinWidget
from tools.gui.win_review import ReviewWinWidget
import logging

logging.basicConfig(
    level=logging.DEBUG
)          

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.main_attributes = MainAttributes()
        self.setWindowTitle(MainWinTexts.MainTitle.value)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setStyleSheet(MainWinStyles.style.value)
        
        # Global Content
        top_layout = QHBoxLayout()
        self.dropdown = QComboBox()
        self.dropdown.addItems(self.main_attributes.get_operation_names())
        self.dropdown.currentIndexChanged.connect(self.update_operation_widget)
        top_layout.addWidget(self.dropdown)

        # Project dropdown
        self.project_dropdown = QComboBox()
        self.project_dropdown.addItems([p.name for p in self.main_attributes.get_project_paths()])
        self.project_dropdown.setCurrentIndex(
            next((i for i, p in enumerate(self.main_attributes.get_project_paths())
                  if p == self.main_attributes.get_selected_prject().path), 0)
        )
        self.project_dropdown.currentIndexChanged.connect(self.on_project_changed)
        self.project_dropdown.setMaximumWidth(300)
        top_layout.addWidget(self.project_dropdown)

        # Dataset dropdown
        self.dataset_dropdown = QComboBox()
        self.dataset_dropdown.addItems([p.name for p in self.main_attributes.get_dataset_paths()])
        self.dataset_dropdown.setCurrentIndex(0)
        self.dataset_dropdown.currentIndexChanged.connect(self.on_dataset_changed)
        self.dataset_dropdown.setMaximumWidth(600)
        top_layout.addWidget(self.dataset_dropdown)

        self.dataset_dropdown.setMaximumWidth(600)
        top_layout.addWidget(self.dataset_dropdown)

        # Conjugations Bar
        self.conjugation_bars = {
            Category.TRAIN : QLabel(str(self.main_attributes.get_conjugation_results()[Category.TRAIN])),
            Category.TEST : QLabel(str(self.main_attributes.get_conjugation_results()[Category.TEST])),
            Category.VALIDATION : QLabel(str(self.main_attributes.get_conjugation_results()[Category.VALIDATION])),
        }
        for label in self.conjugation_bars.values():
            label.setStyleSheet(MainWinStyles.conjugation_bar_style.value)
            label.setFixedHeight(24)
            top_layout.addWidget(label)

        # Add spacing between conjugation bars and the next widget
        top_layout.addSpacing(25)

        # add top layout
        top_layout.addStretch()
        top_layout.addStretch()
        main_layout.addLayout(top_layout)
        main_layout.addLayout(top_layout)
        
        # Sub Content(Sub windows)
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_widget.setLayout(self.content_layout)
        main_layout.addWidget(self.content_widget)
        central_widget.setLayout(main_layout)
        self.create_gui_widgets()
        self.update_operation_widget(0)

    def create_gui_widgets(self):
        self.gui_widgets = [
            ReviewWinWidget(
                self.main_attributes,
                ),
            EditWinWidget(),
            ModelWinWidget()
        ]

    def update_operation_widget(self, index):
        for i in reversed(range(self.content_layout.count())):
            widget = self.content_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        widget = self.gui_widgets[index]
        self.content_layout.addWidget(widget)

    def on_project_changed(self, index):
        self.main_attributes.set_project(index)
        self.main_attributes.dataset_paths = self.main_attributes.list_dataset_paths()
        self.dataset_dropdown.blockSignals(True)
        self.dataset_dropdown.clear()
        self.dataset_dropdown.addItems([p.name for p in self.main_attributes.get_dataset_paths()])
        self.dataset_dropdown.setCurrentIndex(0)
        self.dataset_dropdown.blockSignals(False)
        self.main_attributes.set_dataset(0)
        for cat in Category:
            self.conjugation_bars[cat].setText(str(self.main_attributes.get_conjugation_results()[cat]))
        self.create_gui_widgets()
        self.update_operation_widget(self.dropdown.currentIndex())

    def on_dataset_changed(self, index):
        self.main_attributes.set_dataset(index)
        for cat in Category:
            self.conjugation_bars[cat].setText(str(self.main_attributes.get_conjugation_results()[cat]))
        self.create_gui_widgets()
        
        
def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.showMaximized()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
