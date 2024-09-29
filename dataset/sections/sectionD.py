from PyQt6.QtGui import QGuiApplication, QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import QHBoxLayout, QWidget,QCheckBox,QLabel, QPlainTextEdit, QPushButton, QTableView, QVBoxLayout
from .section import Section

class _Button(QPushButton):
    def __init__(self,text,click_func):
        self.text = text
        self.click_func = click_func
        super().__init__(text)
        self.clicked.connect(self.click)
    
    def click(self):
        self.click_func()   

class _DatasetOptionsButton(QPushButton):
    def __init__(self,text,click_func):
        self.text = text
        self.click_func = click_func
        super().__init__(text)
        self.clicked.connect(self.click)
    
    def click(self):
        self.click_func()

class SectionD(Section):
    def __init__(self,language,spiral_dataset = None):
        children = []
        self.language = language
        self.dataset = spiral_dataset
        self.title = QLabel(self.language.sectionD["title"])
        self.table_view = QTableView()
        self.output_area = QPlainTextEdit()
        self.btn_slice = _DatasetOptionsButton(self.language.sectionD["btn_slice"],self.slice_datas)
        self.btn_convert_labels = _DatasetOptionsButton(self.language.sectionD["btn_convert_labels"],self.convert_labels)
        self.btn_train_test_split = _DatasetOptionsButton(self.language.sectionD["btn_train_test_split"],self.train_test_split)
        self.btn_resizes_frame = _DatasetOptionsButton(self.language.sectionD["btn_resize_frames"],self.resize_frames)
        self.btn_augment = _DatasetOptionsButton(self.language.sectionD["btn_btn_augment"],self.augment)

        for widget in [self.title,self.table_view,self.output_area,self.btn_slice,self.btn_convert_labels,self.btn_train_test_split,self.btn_resizes_frame,self.btn_augment]:
            children.append(widget)

        super().__init__(children=children)
        self.setMaximumHeight(int(QGuiApplication.primaryScreen().geometry().height()*0.4))
        self.setMaximumWidth(int(QGuiApplication.primaryScreen().geometry().width()*0.3))


    def show_analysis(self,analysis):
        cat_dict,total_label,total_frame = analysis
        num_column = len(cat_dict.keys()) + 2
        num_row = 1
        print(num_column)

        self.model = QStandardItemModel(num_row, num_column)
        self.model.setHorizontalHeaderLabels(list(str(x) for x in cat_dict.keys())+ ["total_label","total_frame"])

        items = list(cat_dict.values()) + [total_label,total_frame]
        # Modelde veri ekleme
        for i in range(num_column):
            item = QStandardItem(str(items[i]))
            self.model.setItem(0, i, item)

        # Yeni tablo modelini mevcut tabloya ayarla
        self.table_view.setModel(self.model)

    def convert_labels(self):
        def save():
            if self.dataset is not None:
                input = text.toPlainText()
                conjugates = input.split(",")

                dict_ = {}
                for c in conjugates:
                    now,target = c.split(":")
                    dict_[int(now)] = int(target)

                self.dataset.convert_labels(dict_)
                self.output_area.setPlainText(self.language.sectionD["convert_labels_3"]+input)
                self.window.close()
            else:
                self.output_area.setPlainText(self.language.sectionD["convert_labels_4"])
                self.window.close()
        
        self.window = QWidget()
        lyt = QVBoxLayout()
        label = QLabel(self.language.sectionD["convert_labels_1"])
        text = QPlainTextEdit()
        btn = _Button(self.language.sectionD["convert_labels_2"],save)
        lyt.addWidget(label)
        lyt.addWidget(text)
        lyt.addWidget(btn)
        self.window.setLayout(lyt)
        self.window.show()

    def train_test_split(self):
        def save():
            if self.dataset is not None:
                input1 = float(text.toPlainText())
                input2 = float(text2.toPlainText())

                self.dataset.apply_train_test_split(input1,input2)#
                self.output_area.setPlainText(self.language.sectionD["tts_3"]+str(input1)+ " test "+ str(input2))
                self.window.close()
            else:
                self.output_area.setPlainText(self.language.sectionD["tts_4"])
                self.window.close()
        
        self.window = QWidget()
        lyt = QVBoxLayout()
        label = QLabel(self.language.sectionD["tts_1"])
        text = QPlainTextEdit()
        text2 = QPlainTextEdit()
        text.setMaximumHeight(40)
        text2.setMaximumHeight(40)
        btn = _Button(self.language.sectionD["tts_2"],save)
        lyt.addWidget(label)
        lyt.addWidget(text)
        lyt.addWidget(text2)
        lyt.addWidget(btn)
        self.window.setLayout(lyt)
        self.window.show()

    def resize_frames(self):
        def save():
            if self.dataset is not None:
                input = text.toPlainText()
                self.dataset.resize_frames(int(input))
                self.output_area.setPlainText(self.language.sectionD["rf_3"]+input)
                self.window.close()
            else:
                self.output_area.setPlainText(self.language.sectionD["rf_4"])
                self.window.close()
        
        self.window = QWidget()
        lyt = QVBoxLayout()
        label = QLabel(self.language.sectionD["rf_1"])
        text = QPlainTextEdit()
        btn = _Button(self.language.sectionD["rf_2"],save)
        lyt.addWidget(label)
        lyt.addWidget(text)
        lyt.addWidget(btn)
        self.window.setLayout(lyt)
        self.window.show()

    def augment(self):
        def save():
            if self.dataset is not None:
                input1 = float(text.toPlainText())
                input2 = float(text2.toPlainText())

                self.dataset.augment(int(input1),int(input2))
                self.output_area.setPlainText(self.language.sectionD["aug_3"]+str(input1))
                self.window.close()
            else:
                self.output_area.setPlainText(self.language.sectionD["aug_4"])
                self.window.close()
        
        self.window = QWidget()
        lyt = QVBoxLayout()
        label = QLabel(self.language.sectionD["aug_1"])
        text = QPlainTextEdit()
        text2 = QPlainTextEdit()
        text.setMaximumHeight(40)
        text2.setMaximumHeight(40)
        btn = _Button(self.language.sectionD["aug_2"],save)
        lyt.addWidget(label)
        lyt.addWidget(text)
        lyt.addWidget(text2)
        lyt.addWidget(btn)
        self.window.setLayout(lyt)
        self.window.show()

    def slice_datas(self):
        def save():
            if self.dataset is not None:
                input1 = int(text.toPlainText())
                input2 = int(text2.toPlainText())

                self.dataset.slice(input1,input2,chkbox.isChecked())
                self.output_area.setPlainText(self.language.sectionD["sli_3"])
                self.window.close()
            else:
                self.output_area.setPlainText(self.language.sectionD["sli_4"])
                self.window.close()
        
        self.window = QWidget()
        lyt = QVBoxLayout()
        label = QLabel(self.language.sectionD["sli_1"])
        text = QPlainTextEdit()
        text2 = QPlainTextEdit()
        text.setMaximumHeight(40)
        text2.setMaximumHeight(40)
        h_layout = QHBoxLayout()
        lbl = QLabel(self.language.sectionD["sli_5"])
        chkbox =  QCheckBox()
        chkbox.setChecked(False)
        h_layout.addWidget(lbl)
        h_layout.addWidget(chkbox)
        btn = _Button(self.language.sectionD["sli_2"],save)
        lyt.addWidget(label)
        lyt.addWidget(text)
        lyt.addWidget(text2)
        lyt.addLayout(h_layout)
        lyt.addWidget(btn)
        self.window.setLayout(lyt)
        self.window.show()


