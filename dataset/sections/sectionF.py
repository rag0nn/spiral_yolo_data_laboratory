from PyQt6.QtWidgets import QLabel, QPushButton
from .section import Section

class _ImagePathButton(QPushButton):
    def __init__(self,data,index,click_func):
        self.data = data
        self.index = index
        self.click_func = click_func
        super().__init__(self.data.image_path.split("/")[-1])
        self.clicked.connect(self.click)
    
    def click(self):
        self.click_func(self.index)

    def color_mark(self):
        self.setStyleSheet('background-color: green; color: white;')
    
    def color_mark_remove(self):
        self.setStyleSheet('background-color: white; color: black;')

class SectionF(Section):
    def __init__(self):
        self.buttons = []
        super().__init__(children=[QLabel("Section F")],scroll=True)

    def load_im_path_buttons(self,datas,func_change_data):
        self.func_change_data = func_change_data
        self.buttons = []
        for i,data in enumerate(datas):
            btn = _ImagePathButton(data,i,func_change_data)
            self.buttons.append(btn)
        super().update(new_children=self.buttons)

    def remove_button(self,index):
        self.buttons.pop(index)
        super().remove(index)            

