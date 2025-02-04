from PyQt6.QtGui import QGuiApplication, QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import QCheckBox,QHBoxLayout, QLabel, QPlainTextEdit, QPushButton, QTableView, QVBoxLayout, QWidget
from .section import Section
class _Button(QPushButton):
    def __init__(self,text,click_func):
        self.text = text
        self.click_func = click_func
        super().__init__(text)
        self.clicked.connect(self.click)
    
    def click(self):
        self.click_func() 

class _ManupilationButon(QPushButton):
    def __init__(self,text,click_func):
        self.text = text
        self.click_func = click_func
        super().__init__(self.text)
        self.clicked.connect(self.click)
    
    def click(self):
        self.click_func()   

class _DirectionButton(QPushButton):
    def __init__(self,text,click_func):
        self.text = text
        
        self.click_func = click_func
        super().__init__(self.text)
        self.clicked.connect(self.click)
    
    def click(self):
        self.click_func()       
        
class SectionE(Section):
    def __init__(self,language,func_remove_data,func_forward,func_backward,func_paint_objects,func_switch_language,data = None):
        
        print("a")
        self.data = data
        self.language = language
        self.func_remove_data = func_remove_data
        self.func_forward = func_forward
        self.func_backward = func_backward
        self.func_paint_objects = func_paint_objects
        print("b")
        
        self.h_widget = QWidget()
        self.h_layout = QHBoxLayout()

        print("c")
        self.manupilation_widget = QWidget()
        self.manupilation_layout = QVBoxLayout()
        self.title = QLabel(self.language.sectionE["title"])
        self.info_table_widget = QTableView()
        self.output_area = QPlainTextEdit()
        self.btn_remove = _ManupilationButon(self.language.sectionE["btn_remove"],self.remove)
        self.btn_resize = _ManupilationButon(self.language.sectionE["btn_resize"],self.resize_frame)
        self.btn_convert_labels = _ManupilationButon(self.language.sectionE["btn_convert"],self.convert_labels)
        for widget in [self.title,self.info_table_widget,self.output_area,self.btn_remove,self.btn_resize,self.btn_convert_labels]:
            self.manupilation_layout.addWidget(widget)
        self.manupilation_widget.setLayout(self.manupilation_layout)

        print("d")
        self.direction_widget = QWidget()
        print("T1")
        self.btn_direction_left = _DirectionButton("<",self.func_backward)
        print("T2")
        self.btn_direction_right = _DirectionButton(">",self.func_forward)
        print("T2")
        
        self.paint_objects_checkbox = QCheckBox()
        print("T2")
        
        self.paint_objects_checkbox.setMaximumWidth(20)
        print("T3")
        
        self.paint_objects_checkbox.stateChanged.connect(self.func_paint_objects)
        print("T4")
        
        #self.paint_objects_checkbox.setChecked(True)
        print("T5")
        
        self.paint_objects_text = QLabel(self.language.sectionE["lbl_po"])
        print("T6")
        
        self.btn_language = _Button(self.language.sectionE["btn_switch"],func_switch_language)

        print("e")
        layout_direction_buttons = QHBoxLayout()
        layout_direction_buttons.addWidget(self.btn_direction_left)
        layout_direction_buttons.addWidget(self.btn_direction_right)

        print("f")

        layout_paint_objects = QHBoxLayout()
        layout_paint_objects.addWidget(self.paint_objects_text)
        layout_paint_objects.addWidget(self.paint_objects_checkbox)

        print("g")

        v_layout = QVBoxLayout()
        v_layout.addLayout(layout_paint_objects)
        v_layout.addLayout(layout_direction_buttons)
        v_layout.addWidget(self.btn_language)
        self.direction_widget.setLayout(v_layout)

        print("h")

        self.h_layout.addWidget(self.manupilation_widget)
        self.h_layout.addWidget(self.direction_widget)
        self.manupilation_widget.setMaximumWidth(int(QGuiApplication.primaryScreen().geometry().height()*0.5))
        self.h_widget.setLayout(self.h_layout)

        print("Section e initialized")
        super().__init__(children=[self.h_widget])
        self.setMaximumHeight(int(QGuiApplication.primaryScreen().geometry().height()*0.4))
        

    def load_data_info(self,data):
        num_row = 1
        num_column = len(data.label_counts.keys())

        self.model = QStandardItemModel(num_row, num_column)
        self.model.setHorizontalHeaderLabels(list(str(x) for x in data.label_counts.keys()))

        items = list(data.label_counts.values())
        # Modelde veri ekleme
        for i in range(num_column):
            item = QStandardItem(str(items[i]))
            self.model.setItem(0, i, item)

        # Yeni tablo modelini mevcut tabloya ayarla
        self.info_table_widget.setModel(self.model)

    def resize_frame(self):
        def save():
            if self.data is not None:
                input = text.toPlainText()
                self.data.resize_image(int(input))
                self.output_area.setPlainText(self.language.sectionE["rf_3"]+input)
                self.window.close()
            else:
                self.output_area.setPlainText(self.language.sectionE["rf_4"])
                self.window.close()
        
        self.window = QWidget()
        lyt = QVBoxLayout()
        label = QLabel(self.language.sectionE["rf_1"])
        text = QPlainTextEdit()
        btn = _Button(self.language.sectionE["rf_2"],save)
        lyt.addWidget(label)
        lyt.addWidget(text)
        lyt.addWidget(btn)
        self.window.setLayout(lyt)
        self.window.show()
        
    def convert_labels(self):
        def save():
            if self.data is not None:
                input = text.toPlainText()
                conjugates = input.split(",")

                dict_ = {}
                for c in conjugates:
                    now,target = c.split(":")
                    dict_[int(now)] = int(target)

                self.data.convert_labels(dict_)
                self.output_area.setPlainText(self.language.sectionE["cl_3"]+input)
                
                self.data.labels = []
                self.data.label_counts = {}
                self.data._load_labels_and_stats()
                self.load_data_info(self.data)
                self.window.close()
            else:
                self.output_area.setPlainText(self.language.sectionE["cl_4"])        
                self.window.close()
        self.window = QWidget()
        lyt = QVBoxLayout()
        label = QLabel(self.language.sectionE["cl_1"])
        text = QPlainTextEdit()
        btn = _Button(self.language.sectionE["cl_2"],save)
        lyt.addWidget(label)
        lyt.addWidget(text)
        lyt.addWidget(btn)
        self.window.setLayout(lyt)
        self.window.show()

    def remove(self):
        def save():
            if self.data is not None:
                self.data.remove_data()
                self.output_area.setPlainText(self.language.sectionE["re_3"]+self.data.image_path)
                self.func_remove_data()
                
                self.window.close()
            else:
                self.output_area.setPlainText(self.language.sectionE["re_4"])        
                self.window.close()
        
        self.window = QWidget()
        lyt = QVBoxLayout()
        label = QLabel(self.language.sectionE["re_1"])
        btn = _Button(self.language.sectionE["re_2"],save)
        lyt.addWidget(label)
        lyt.addWidget(btn)
        self.window.setLayout(lyt)
        self.window.show()
