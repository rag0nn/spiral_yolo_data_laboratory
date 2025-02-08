from tools.utils import path_sequence, get_screen_resolution
from spiral_dataset import SpiralDataset
from spiral_data import SpiralData
from monitor_helper import SpiralMonitorHelper
from tools.utils import show_pie
import os
import yaml
import pandas as pd 
import cv2
import numpy as np
import shutil
from tqdm import tqdm
import matplotlib.pyplot as plt

file_path = os.path.dirname(os.path.abspath(__file__))


def test_dataset(dataset:SpiralDataset):
    """
    Veri setini manuel olarak test etmek için kullanılır
    input:
        SpiralDataset: Test edilecek veri seti
    kullanım:
        Verileri dolaşma:
            a: bir önceki veri
            d: bir sonraki veri
            q: kapat
            p: veriyi işaretle
        Eğer işaretlenen veri varsa:
            a: bir önceki veri
            d: bir sonraki veri
            q: kapat
            p: veriyi sil
            b: işaretli tüm verileri sil ve kapat       
    """
    dataset.check_non_scale_labels()
    screen_w,screen_h = get_screen_resolution()

    monitor_shapes = {
        0:(int(screen_h),int(screen_w*0.8)),
        1:(int(screen_h*0.25),int(screen_w*0.2)),
        2:(int(screen_h*0.25),int(screen_w*0.2)),
        3:(int(screen_h*0.5),int(screen_w*0.2))
    }

    monitor_datas = {
        #i:[isim,index,monitor,monitor konumu]
        0:["Ana",0,np.zeros(monitor_shapes[0]),(0,0)],
        1:["Onceki",-1,np.zeros(monitor_shapes[1]),(0,monitor_shapes[0][1])],
        2:["Sonraki",1,np.zeros(monitor_shapes[2]),(monitor_shapes[1][0],monitor_shapes[0][1])],
        3:["Panel",0,np.zeros(monitor_shapes[3]),(monitor_shapes[1][0]+monitor_shapes[2][0],monitor_shapes[0][1])],
    }

    defective_datas = []

    while True:
        # ana verinin panel için tutulacak olan kopyası
        main_data = None
        # monitörleri göster ve girdi bekle
        for key,[name,index,monitor,monitor_location] in monitor_datas.items():
            data = SpiralData(dataset.image_paths[index],dataset.txt_paths[index])
        
            if name != "Panel":
                im = cv2.imread(data.image_path)

                if name == "Ana":
                    main_data = data
                    objects = data.get_as_absoluate_coordinates(im.shape)
                    try:
                        im = SpiralMonitorHelper.paint_objects(im,objects)
                    except:
                        pass
                im = cv2.resize(im,monitor.shape[::-1])
                monitor = im
            else:
                monitor = np.zeros_like(monitor)
                c = main_data.txt_path.split("/")
 
                cv2.putText(monitor,f"index: {index}/{len(dataset.image_paths)}",(10,20),cv2.FONT_HERSHEY_PLAIN,1,(120,255,120))  
                cv2.putText(monitor,f"{c[-1]}",(10,50),cv2.FONT_HERSHEY_PLAIN,1,(255,255,255))
                cv2.putText(monitor,f"etiket sayilari: {main_data.label_counts}",(10,80),cv2.FONT_HERSHEY_PLAIN,1,(255,255,255))
                cv2.putText(monitor,f"toplam etiket: {main_data.total_label_count}",(10,110),cv2.FONT_HERSHEY_PLAIN,1,(255,255,255))
            cv2.namedWindow(name)
            cv2.moveWindow(name,monitor_location[1],monitor_location[0])
            cv2.imshow(name,monitor)        
        
        key = cv2.waitKey(0)
        if key == ord("d") or key == ord("D"):
            for value in monitor_datas.values():value[1] = (value[1]+1)%len(dataset.image_paths)
        elif key == ord("a") or key == ord("A"):
            for value in monitor_datas.values():value[1] = (value[1]-1)%len(dataset.image_paths)
        elif key == ord("p") or key == ord("P"):
            for value in monitor_datas.values():value[1] = (value[1]+1)%len(dataset.image_paths)
            if data not in defective_datas:
                defective_datas.append(data)
        elif key == ord("q") or key == ord("Q"):
            break    

    cv2.destroyAllWindows()

    if len(defective_datas) > 0:
        for i,value in enumerate(list(monitor_datas.values())):
            value[1] = -1 + i
        while len(defective_datas) > 0:
            # ana verinin panel için tutulacak olan kopyası
            main_data = None
            # monitörleri göster ve girdi bekle
            for key,[name,index,monitor,monitor_location] in list(monitor_datas.items())[0:len(defective_datas)]:
                data = defective_datas[index]
            
                if name != "Panel":
                    im = cv2.imread(data.image_path)
        
                    if name == "Ana":
                        main_data = data
                        objects = data.get_as_absoluate_coordinates(im.shape)
                        try:
                            im = SpiralMonitorHelper.paint_objects(im,objects)
                        except:
                            pass
                    im = cv2.resize(im,monitor.shape[::-1])
                    monitor = im
                else:
                    monitor = np.zeros_like(monitor)
                    c = main_data.txt_path.split("/")
                    short_path = " ".join([c[3],c[6],c[7]])
                    cv2.putText(monitor,f"{short_path}",(10,20),cv2.FONT_HERSHEY_PLAIN,1,(255,255,255))
                    cv2.putText(monitor,f"etiket sayilari: {main_data.label_counts}",(10,50),cv2.FONT_HERSHEY_PLAIN,1,(255,255,255))
                    cv2.putText(monitor,f"toplam etiket: {main_data.total_label_count}",(10,80),cv2.FONT_HERSHEY_PLAIN,1,(255,255,255))
                    
                cv2.namedWindow(name)
                cv2.moveWindow(name,monitor_location[1],monitor_location[0])
                cv2.imshow(name,monitor)        
            
            key = cv2.waitKey(0)
            if key == ord("d") or key == ord("D"):
                for value in monitor_datas.values():value[1] = (value[1]+1)%len(defective_datas)
            elif key == ord("a") or key == ord("A"):
                for value in monitor_datas.values():value[1] = (value[1]-1)%len(defective_datas)
            elif key == ord("p") or key == ord("P"):
                main_data.remove_data()
                defective_datas.remove(main_data)
                if len(defective_datas) == 0:
                    break
                for value in monitor_datas.values():value[1] = (value[1]+1)%len(defective_datas) # silme işlemleri 
            elif key == ord("b") or key == ord("B"):
                for data in defective_datas:
                    data.remove_data()
                break
            elif key == ord("q") or key == ord("Q"):
                break    

        cv2.destroyAllWindows()
    
    print("Test işlemi tamamlandı")


def analysis():
    """
    datasets altındaki tüm veri setlerini analiz et ve bir sonuç olarak döndür
    return: 
        pd.DataFrame: Sonuçların çerçevesi
    """
    label_dict = {
        0:"tasit",
        1:"insan",
        2:"uap",
        3:"uai"
        }
    datasets_file_path = path_sequence(file_path,"datasets")
    ds_list = os.listdir(datasets_file_path)
    ds_row = {'tasit':0, 'insan':0, 'uap':0, 'uai':0, 'bilinmiyor':0,'toplam etiket sayısı':0,'toplam frame sayısı':0}

    rows = []
    indexes = []
    for ds_name in ds_list:
        indexes.append(ds_name)
        ds = SpiralDataset(path_sequence(datasets_file_path,ds_name))
        label_counts, total_label_count, total_frame_count = ds.analyze()
        print("Q:",ds.analyze())
        row = ds_row.copy()

        for lbl in list(label_counts.keys()):
            if lbl in list(label_dict.keys()):
                row[label_dict[lbl]] += label_counts[lbl]
            else:
                row['bilinmiyor'] += label_counts[lbl]
        row['toplam frame sayısı'] = total_frame_count
        row['toplam etiket sayısı'] = total_label_count
        rows.append(row)
    
    df = pd.DataFrame(
        columns=list(ds_row.keys()),
        data=rows,
        index=indexes
    )
    
    df.loc['TOPLAM'] = {'tasit':df['tasit'].sum(), 'insan':df['insan'].sum(), 'uap':df['uap'].sum(), 'uai':df['uai'].sum(), 'bilinmiyor':df['bilinmiyor'].sum(),'toplam etiket sayısı':df['toplam etiket sayısı'].sum(),'toplam frame sayısı':df['toplam frame sayısı'].sum()}

    main_fig = plt.figure(figsize=(5,20))
    plt.title("Etiket Sayıları")
    show_pie(
        values=df['toplam etiket sayısı'][:-1],
        labels=indexes
    )
    main_fig.add_subplot(2,1,1)
    plt.title("Frame Sayıları")
    show_pie(
        values=df['toplam frame sayısı'][:-1],
        labels=indexes
    ) 
    
    return df
    
def create_dataset(name,path=None,detect_yaml=None):
    """
    YOLO formatında veri seti şablonu oluşturur
    input:
        path: Veri setinin hangi folder'da olacağı, eğer boş bırakılırsa datasets altında oluşturulur
        detect_yaml: Veri setinin YOLO yaml dosyasının içeriği, eğer boş bırakılırsa varsayılan etiketler ve adresler döndürülür (Bu veriler sonradan değiştirilibelir)
    """

    if path == None:
        path = path_sequence(file_path,"datasets")
    if detect_yaml == None:
        detect_yaml = {
            'train': 'images/train',
            'val': 'images/val',
            'test': 'images/test',
            'names': {0:'tasit',1:"insan",2:"UAP",3:"UAI"}
        }

    ds_path = path_sequence(path,name)
    if os.path.exists(ds_path) == False:
        os.mkdir(path=ds_path)
        detect_path = path_sequence(ds_path,"detect")
        os.mkdir(path=detect_path)
        
        images_path = path_sequence(detect_path,"images")
        os.mkdir(path=images_path)
        labels_path = path_sequence(detect_path,"labels")
        os.mkdir(path=labels_path)
    
        for cat in ["train","test","val"]:      
            im_cat_path = path_sequence(images_path,cat)
            label_cat_path = path_sequence(labels_path,cat)
            os.mkdir(im_cat_path)
            os.mkdir(label_cat_path)
            print("Oluşturuldu",im_cat_path," -- ",label_cat_path)
            
        with open(path_sequence(ds_path,"detect","detect.yaml"),"w") as f:
            yaml.dump(detect_yaml,f, default_flow_style=False)

def merge_datasets(name):
    """
    Datasets altındaki veri setlerini birleştirir ve merge altına veri seti olarak kaydeder.
    input:
        name: veri setinin ismi
    """
    ds_paths = path_sequence(file_path,"datasets")
    path = path_sequence(file_path,"merge")
    name_count =len(os.listdir(path))+1
    name = f"{name_count}_{name}"
    create_dataset(path=path,name=name)
    ds_path = path_sequence(path,name)
    for sub_ds_name in tqdm(os.listdir(ds_paths)):
        print("Kopyalanıyor: ",sub_ds_name)
        sub_ds_path = path_sequence(ds_paths,sub_ds_name)
        sub_ds = SpiralDataset(sub_ds_path)
        
        for im_path,txt_path in zip(sub_ds.image_paths,sub_ds.txt_paths):
            cat = im_path.split("/")[-2]
            im_name = im_path.split("/")[-1]
            txt_name = txt_path.split("/")[-1]
            shutil.copyfile(im_path,path_sequence(ds_path,"detect","images",cat,f"{sub_ds.name}_{im_name}"))
            shutil.copyfile(txt_path,path_sequence(ds_path,"detect","labels",cat,f"{sub_ds.name}_{txt_name}"))
    print("Veri setleri birleştirildi")
