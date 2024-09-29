from PyQt6.QtWidgets import QApplication, QMainWindow,QWidget,QVBoxLayout, QHBoxLayout
from PyQt6.QtGui import QGuiApplication, QPixmap,QImage
from spiral_dataset import SpiralDataset
from spiral_events.monitor_helper import SpiralMonitorHelper
from core_organization import create_dataset, analysis, merge_datasets
import sys
import os 
from sections.sectionA import SectionA
from sections.sectionB import SectionB
from sections.sectionC import SectionC
from sections.sectionD import SectionD
from sections.sectionE import SectionE
from sections.sectionF import SectionF 
from PyQt6.QtCore import Qt
import cv2
from language import Language

FILE_PATH = file_path = os.path.dirname(os.path.abspath(__file__))
  
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.language = Language()
        self.initUi()

    def initUi(self):
        dataset_names = self._get_ds_names()
        self.chosen_ds_name = ""
        self.chosen_ds = None
        self.chosen_data = None
        self.chosen_data_index = None
        self.old_chosen_data_index = None
        self.paint_objects_ = False

        
        ####
        # Pencere başlığı
        self.setWindowTitle("Spiral Dataset Laboratuary")

        root_widget = QWidget()
        self.setCentralWidget(root_widget)

        root_layout = QHBoxLayout()
        
        # Sütun layout'larını oluştur
        column1_layout = QVBoxLayout()
        column2_layout = QVBoxLayout()
        column3_layout = QVBoxLayout()


        self.sectC=SectionC()
        self.sectA=SectionA(dataset_names,self.change_dataset)
        self.sectB=SectionB(self.language,create_dataset,analysis,merge_datasets)
        self.sectD=SectionD(self.language)
        self.sectE=SectionE(self.language,self.remove_data,self.data_index_forward,self.data_index_backward,self.change_paint_objects,self.switch_language)
        self.sectF=SectionF()
        #Sütun 1
        column1_layout.addWidget(self.sectA)
        column1_layout.addWidget(self.sectB)

        # Sütun 2
        column2_row1_layout,column2_row2_layout = QHBoxLayout(),QHBoxLayout()
        column2_row1_layout.addWidget(self.sectC)
        column2_row2_layout.addWidget(self.sectD)
        column2_row2_layout.addWidget(self.sectE)
        column2_layout.addLayout(column2_row1_layout)
        column2_layout.addLayout(column2_row2_layout)
        column2_layout.setStretch(0,3)
        column2_layout.setStretch(1,1)

        # Sütun 3
        column3_layout.addWidget(self.sectF)

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

    def _get_ds_names(self): 
        ds_list = os.listdir(FILE_PATH + "/datasets")
        return ds_list
    
    def _numpy_to_qpixmap(self,numpy_array):
        numpy_array = cv2.cvtColor(numpy_array,cv2.COLOR_BGR2RGB)
        # NumPy array'i uint8 tipinde olmalı
        height, width, channel = numpy_array.shape
        bytes_per_line = channel * width
        q_image = QImage(numpy_array.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
        
        # QImage'yi QPixmap'e çevir
        q_pixmap = QPixmap.fromImage(q_image)
        return q_pixmap

    def paint_objects(self,image,data):
        if self.paint_objects_:
            objects = data.get_as_absoluate_coordinates(image.shape)
            try:
                image = SpiralMonitorHelper.paint_objects(image,objects)
            except:
                pass
            return image
        else:
            return image
    
    def change_dataset(self,text):
        self.chosen_ds_name = text
        self.chosen_ds = SpiralDataset(FILE_PATH+"/datasets/" + self.chosen_ds_name)
        datas = self.chosen_ds.get_datas()
        self.chosen_data_index = 0
        self.sectF.load_im_path_buttons([data for data in datas],self.change_data)
        self.sectD.show_analysis(self.chosen_ds.analyze())
        self.sectD.dataset = self.chosen_ds
        self.chosen_data_index = 0
        self.change_data(0)
        self.sectD.title.setText("DATASET: " + text)
        
    def change_data(self,index):
        index = index % len(self.sectF.buttons)
        data = self.sectF.buttons[index].data
        if data is not None:
            self.chosen_data = data
            self.old_chosen_data_index = self.chosen_data_index
            self.chosen_data_index = index 

            image = cv2.imread(self.chosen_data.image_path)
            im_text = str(image.shape)
            image = self.paint_objects(image,data)
            image = self._numpy_to_qpixmap(image)
            image = image.scaled(int(QGuiApplication.primaryScreen().geometry().width()*0.7),int(QGuiApplication.primaryScreen().geometry().height()*0.6),Qt.AspectRatioMode.KeepAspectRatio)
            self.sectC.image.setPixmap(image)
            self.sectE.load_data_info(data)
            self.sectE.data = data
            
            self.sectE.title.setText( im_text + " DATA: " + data.data_name )
            self.sectF.buttons[self.chosen_data_index].color_mark()
            self.sectF.buttons[self.old_chosen_data_index].color_mark_remove()
        else:
            pass

    def remove_data(self):
        self.sectF.remove_button(self.chosen_data_index)
        self.change_data(self.chosen_data_index+1) 

    def data_index_forward(self):
        self.change_data(self.chosen_data_index+1)

    def data_index_backward(self):
        self.change_data(self.chosen_data_index-1)
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_A:
            self.data_index_backward()
        elif event.key() == Qt.Key.Key_D:
            self.data_index_forward()
        elif event.key() == Qt.Key.Key_R:
            self.sectE.remove()

    def change_paint_objects(self):
        self.paint_objects_ = not self.paint_objects_
        self.change_data(self.chosen_data_index)
    
    def switch_language(self):
        if self.language.language == 'tr':
            self.language.switch('en')
        elif self.language.language == 'en':
            self.language.switch('tr')
        self.initUi()


app = QApplication(sys.argv)

window = MainWindow()
window.setGeometry(QGuiApplication.primaryScreen().geometry())
window.show()

sys.exit(app.exec())
