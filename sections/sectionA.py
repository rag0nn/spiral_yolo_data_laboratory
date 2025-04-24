from PyQt6.QtWidgets import QPushButton
from PyQt6.QtGui import QGuiApplication
from .section import Section

class _DatasetButton(QPushButton):
    def __init__(self,text,click_func):
        self.text = text
        self.click_func = click_func
        super().__init__(text)
        self.clicked.connect(self.click)
    
    def click(self):
        self.click_func(self.text)

class SectionA(Section):
    def __init__(self,dataset_names,change_ds_func):
        children = []

        for ds_name in dataset_names:
            btn = _DatasetButton(ds_name,change_ds_func)
            children.append(btn)
        

        super().__init__(children=children,scroll=True)
        self.setMaximumHeight(int(QGuiApplication.primaryScreen().geometry().height()*0.4))