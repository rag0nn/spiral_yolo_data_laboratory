import logging
from tools.dataset import Dataset
from tools.enums import Category
from tools.data import Data
from tools.reports import DataReports,CategoryReports,DatasetReports
from pathlib import Path
from tools.project import Project
from main import create_project

from main import main

logging.basicConfig(
    level=logging.DEBUG,
)

# project
# p = Project(Path(r"C:\Users\asus\Desktop\NEW_DATASET_LAB\projects\newo"))
# p.merge()

# dataset    
#ds = Dataset.create("temp1111",r"C:\Users\asus\Desktop\Yeni klasör",{})
#Dataset.create("T22_O2_5",r"C:\Users\asus\Desktop\YoloDatasetLab\projects\newo\datasets",{})
# print(ds)
# ds = Dataset(Path(r"C:\Users\asus\Desktop\YoloDatasetLab\projects\newo\datasets\T22_O2_5\output\sub_T22_O2_5_0.5_rand-True_2025-06-11_00-42-02"))
# ds = Dataset(Path(r"C:\Users\asus\Desktop\YoloDatasetLab\projects\newo\datasets\T22_O2_5"))
# ds.convert_annotations({})
# ds.export_unmatches()
# ds.get_report()
# ds.split_standart(0.5,0.3,0.2)
#ds.sub_dataset(0.2)
#ds.rename_datas_consecutive("test",keep_current_names=False)
# ds.resize_images((1200,900),False)
# ds.copy(r"C:\Users\asus\Desktop\Yeni klasör")
# print(ds.images_path_dict)
# print(ds.annotations_path_dict)

# # #ds.get_data(Category.TRAIN,random=True,f_index=0,l_index=-5)
# ds.get_report(image_stats=True,save=True)

#data
# a = AnnotationData(Path(r"C:\Users\asus\Desktop\NEW_DATASET_LAB\projects\temp1\datasets\TP22_O3_2_NOISED\detect\labels\train\frame_000004.txt"))
# print(a.objects)
# print(a.get_stats())
# i = ImageData(Path(r"C:\Users\asus\Desktop\NEW_DATASET_LAB\projects\temp1\datasets\TP22_O3_2_NOISED\detect\images\train\frame_000004.jpg"))

# d = Data(r"C:\Users\asus\Desktop\YoloDatasetLab\projects\newo\datasets\T22_O2_5",Category.TEST,"test_0000032")
# print(d.name)
# d.annotation_data.convert_objects({0:1,1:2,2:3,3:0})
# dd = DataReports(d)

# c1 = CategoryReports([dd,dd])
# c2 = CategoryReports([dd,dd,dd])
# c3 = CategoryReports([dd,dd,dd,dd])
# #print(c)
# qq = DatasetReports([Category.TEST,Category.TRAIN,Category.VALIDATION],[c1,c2,c3])
# print(qq)

#create_project("newo")