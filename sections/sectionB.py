from PyQt6.QtGui import QGuiApplication
from PyQt6.QtWidgets import QLabel, QPushButton, QPlainTextEdit, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
from .section import Section
import os
file_path = os.path.dirname(os.path.abspath(__file__))




class _Button(QPushButton):
    def __init__(self,text,click_func):
        self.text = text
        self.click_func = click_func
        super().__init__(self.text)
        self.clicked.connect(self.click)
    
    def click(self):
        self.click_func()   
        
class SectionB(Section):
    def __init__(self,language,func_create_dataset,func_analysis,func_merge):
        self.func_create_dataset = func_create_dataset
        self.func_analysis = func_analysis
        self.func_merge = func_merge
        self.language = language

        children = []
        self.title = QLabel(self.language.sectionB["title"])
        self.btn_create_ds = _Button(self.language.sectionB["btn_create_ds"],self.create_dataset)
        self.btn_merge_ds = _Button(self.language.sectionB["btn_merge_ds"],self.merge_datasets)
        self.btn_analyis = _Button(self.language.sectionB["btn_analysis"],self.show_analysis)
        self.output = QPlainTextEdit()

        for widget in [self.title,self.btn_create_ds,self.btn_merge_ds,self.btn_analyis,self.output]:
            children.append(widget)
        

        super().__init__(children=children)
        self.setMaximumHeight(int(QGuiApplication.primaryScreen().geometry().height()*0.6))
    
    def create_dataset(self):
        def save():
            name = text.toPlainText()
            self.func_create_dataset(name)
            self.output.setPlainText(self.language.sectionB["cd_2"]+name)
            self.window.close()
        
        self.window = QWidget()
        lyt = QVBoxLayout()
        text = QPlainTextEdit()
        btn = _Button(self.language.sectionB["cd_1"],save)
        lyt.addWidget(text)
        lyt.addWidget(btn)
        self.window.setLayout(lyt)
        self.window.show()

    def show_analysis(self):
        
        def load_data_to_table(df):
            table_widget = QTableWidget()
            table_widget.setRowCount(len(df))
            table_widget.setColumnCount(len(df.columns))

            table_widget.setHorizontalHeaderLabels(df.columns)

            for i in range(len(df)):
                for j in range(len(df.columns)):
                    table_widget.setItem(i, j, QTableWidgetItem(str(df.iat[i, j])))
            return table_widget
        output_df = self.func_analysis()

        self.table = load_data_to_table(output_df)
        self.table.show()
        
        self.output.setPlainText(str(output_df))

    def merge_datasets(self):
        def save():
            name = text.toPlainText()
            self.func_merge(name)
            self.output.setPlainText(self.language.sectionB["md_2"]+name)
            self.window.close()
        
        self.window = QWidget()
        lyt = QVBoxLayout()
        text = QPlainTextEdit()
        btn = _Button(self.language.sectionB["md_1"],save)
        lyt.addWidget(text)
        lyt.addWidget(btn)
        self.window.setLayout(lyt)
        self.window.show()


        
        