from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel,
    QTextEdit, QLineEdit, QHBoxLayout, QSizePolicy,
    QScrollArea, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMessageBox

from ..dataset import Dataset

class ReviewWinWidget(QWidget):
    def __init__(self, 
                 main_attributes, 
                 parent=None):
        super().__init__(parent)
        self.main_attributes = main_attributes


        main_layout = QHBoxLayout(self)
        
        # LEFT PANEL
        left_panel = QVBoxLayout()
        left_panel.addWidget(QLabel("Operations"))
        for op in self.main_attributes.get_selected_operation():
            btn = QPushButton(op.value[0])
            def make_handler(handler):
                def wrapped():
                    result= handler()
                    QMessageBox.information(self, "Result:", result)
                return wrapped
            btn.clicked.connect(make_handler(op.value[1]))
            left_panel.addWidget(btn)
        left_panel.addStretch(1)

        # RIGHT PANEL
        right_panel = QVBoxLayout()
        right_panel.addWidget(QLabel("Review Datasets"))
        dataset_list_widget = QWidget()
        dataset_list_layout = QVBoxLayout(dataset_list_widget)
        dataset_list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        dataset_list = self.main_attributes.get_dataset_paths()
        for ds in dataset_list:
            row = QHBoxLayout()
            # Dataset ismi butonu
            ds_btn = QPushButton(str(ds.stem))
            ds_btn.clicked.connect(lambda _, name=ds: self.review_dataset(name))
            row.addWidget(ds_btn)
            container = QWidget()
            container.setLayout(row)
            dataset_list_layout.addWidget(container)

        dataset_list_layout.addStretch(1)
        # Scroll area ile sar
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(dataset_list_widget)
        right_panel.addWidget(scroll)

        # Panelleri ana layout'a ekle
        main_layout.addLayout(left_panel, 1)
        main_layout.addLayout(right_panel, 2)
        self.setLayout(main_layout)

    def review_dataset(self, dataset_path):
        ds = Dataset(dataset_path)
        ds.review_dataset()

