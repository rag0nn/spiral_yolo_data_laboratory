import os
from spiral_events.tools.utils import path_sequence, yaml
from spiral_dataset import SpiralDataset
from spiral_events.tools.utils import show_pie
import pandas as pd
import matplotlib.pyplot as plt
import shutil
from tqdm import tqdm
file_path = os.path.dirname(os.path.abspath(__file__))

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
    ds_row = {'isim':"-",'tasit':0, 'insan':0, 'uap':0, 'uai':0, 'bilinmiyor':0,'toplam etiket sayısı':0,'toplam frame sayısı':0}

    rows = []
    indexes = []
    for ds_name in ds_list:
        indexes.append(ds_name)
        ds = SpiralDataset(path_sequence(datasets_file_path,ds_name))
        label_counts, total_label_count, total_frame_count = ds.analyze()
        print("Q:",ds.analyze())
        row = ds_row.copy()
        
        row['isim'] = ds_name
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
    
    df.loc['TOPLAM'] = {'isim':'toplam','tasit':df['tasit'].sum(), 'insan':df['insan'].sum(), 'uap':df['uap'].sum(), 'uai':df['uai'].sum(), 'bilinmiyor':df['bilinmiyor'].sum(),'toplam etiket sayısı':df['toplam etiket sayısı'].sum(),'toplam frame sayısı':df['toplam frame sayısı'].sum()}

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