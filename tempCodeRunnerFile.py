from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,QSlider, QPushButton
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtCore import Qt
import sys
import os 
class Section(QWidget):
    def __init__(self,children):
        super().__init__()
        self.setStyleSheet(f"""
                border: 2px solid black;  /* Tek çerçeve */
                padding: 1px;                    /* İç boşluk */
                background-color: white;
            """)
        layout = QVBoxLayout()
        for chl in children:layout.addWidget(chl)

        self.setLayout(layout)

def get_ds_names():
    file_path = os.path.dirname(os.path.abspath(__file__))
    ds_list = os.listdir(file_path + "/dataset/datasets")
    return ds_list

class SectionA(Section):
    def __init__(self):
        ds_names = get_ds_names()
        widgets = [QLabel("Section A")]
        
        for ds_name in ds_names:
            btn = QPushButton(ds_name)
            widgets.append(btn)
        
        super().__init__(children=widgets)
        self.setMaximumHeight(int(QGuiApplication.primaryScreen().geometry().height()*0.4))

class SectionB(Section):
    def __init__(self):
        super().__init__(children=[QLabel("Section B")])
        self.setMaximumHeight(int(QGuiApplication.primaryScreen().geometry().height()*0.6))


class SectionC(Section):
    def __init__(self):
        super().__init__(children=[QLabel("Section C")])
        self.setMaximumHeight(int(QGuiApplication.primaryScreen().geometry().height()*0.6))


class SectionD(Section):
    def __init__(self):
        super().__init__(children=[QLabel("Section D")])
        self.setMaximumHeight(int(QGuiApplication.primaryScreen().geometry().height()*0.4))


class SectionE(Section):
    def __init__(self):
        super().__init__(children=[QLabel("Section E")])
        self.setMaximumHeight(int(QGuiApplication.primaryScreen().geometry().height()*0.4))


class SectionF(Section):
    def __init__(self):
        super().__init__(children=[QLabel("Section F")])


# MAIN    
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Pencere başlığı
        self.setWindowTitle("Spiral Dataset Laboratuary")

        root_widget = QWidget()
        self.setCentralWidget(root_widget)

        root_layout = QHBoxLayout()
        
        # Sütun layout'larını oluştur
        column1_layout = QVBoxLayout()
        column2_layout = QVBoxLayout()
        column3_layout = QVBoxLayout()

        #Sütun 1
        column1_layout.addWidget(SectionA())
        column1_layout.addWidget(SectionB())

        # Sütun 2
        column2_row1_layout,column2_row2_layout = QHBoxLayout(),QHBoxLayout()
        column2_row1_layout.addWidget(SectionC())
        column2_row2_layout.addWidget(SectionD())
        column2_row2_layout.addWidget(SectionE())
        column2_layout.addLayout(column2_row1_layout)
        column2_layout.addLayout(column2_row2_layout)
        column2_layout.setStretch(0,3)
        column2_layout.setStretch(1,1)

        # Sütun 3
        column3_layout.addWidget(SectionF())

        # Sütunları ana layout'a ekle
        root_layout.addLayout(column1_layout)
        root_layout.addLayout(column2_layout)
        root_layout.addLayout(column3_layout)

        root_layout.setStretch(0,1)
        root_layout.setStretch(1,5)
        root_layout.setStretch(2,1)
        root_layout.setContentsMargins(0, 0, 0, 0)  # Ana layout'un kenar boşluklarını sıfırla
        root_layout.setSpacing(0)  # 
        root_widget.setLayout(root_layout)

app = QApplication(sys.argv)

window = MainWindow()
window.setGeometry(QGuiApplication.primaryScreen().geometry())
window.show()

sys.exit(app.exec())
