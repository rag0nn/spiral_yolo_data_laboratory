from IPython.display import clear_output
import os
from datetime import datetime
import matplotlib.pyplot as plt
import cv2
import numpy as np
import math


file_path = os.path.dirname(os.path.abspath(__file__))

def add_log(log:str):
    """
    Loglama işlemi
    """

    f = open(path_sequence(file_path,'..','output','logs.txt'),"a")
    f.writelines(str(datetime.now().date())+' '+str(datetime.now().time())+'  '+str(log)+'\n')
    f.close()

def chose_dataset():
    """
    Var olan veri setlerinden birini seç
    return:
        veri setinin yolu
    """

    ds_list = os.listdir(path_sequence(file_path,"datasets"))
    for i,ds in enumerate(ds_list):
        print(i," ",ds)
    chosen = int(input(">> :"))
    if chosen > len(ds_list) or chosen < 0:
        clear_output()
        print("> Yanlış girdi girildi!")
        return chose_dataset()
    clear_output()
    print("> Seçilen: ",chosen," ", ds_list[chosen])
    return path_sequence(file_path,"datasets",ds_list[chosen])

def path_sequence(root,*directories):
    """
    Yolları '/' işareti ile birbirine bağlar, string ifadesidir.
    """
    seq = root
    for directory in directories:
            seq += f"/{directory}"
    return seq

def format_line(line):
    """
    TXT dosyasından elde edilen yolo formatındaki taglari ayırmaya yarar.
    """
    words = line.split(" ")
    return int(words[0]),float(words[1]),float(words[2]),float(words[3]),float(words[4])
    
def show_images_figure(images,titles,num_rows,num_columns,figsize=(10,5),imsize=(700,500)):
    """
    resimleri ve başlıkları plt kullanarak bastırır
    """
    main_fig = plt.figure(figsize=figsize)

    for i in range(num_rows*num_columns):
            main_fig.add_subplot(num_rows,num_columns,i+1)
            plt.imshow(cv2.resize(cv2.cvtColor(images[i],cv2.COLOR_BGR2RGB),imsize))
            plt.axis('off')
            plt.title(titles[i])


def show_pie(values,labels,title=None,explode=None,startangle=0,colors=None,percentages='%1.2f%%',fontsize=7):
    """
    Pasta grafiği göster
    values=[değerler]
    labels=[etiketler]
    explode=[0.1,0.2,...] dilimin merkezden uzaklığı
    startangle=başlangıç açısı
    color=[renkler] hex veya plt renkleri r vs.
    percentages=yüzdelik dilimler, None göstermez,
    """

    plt.pie(values,labels=labels,explode=explode,startangle=startangle,colors=colors, autopct=percentages)     
    if title != None:
        plt.legend(title=title,loc='upper right',fontsize=fontsize)

def get_screen_resolution():
          """
          return: width,height
          """
          import tkinter
          root = tkinter.Tk()
          width = root.winfo_screenwidth()
          height = root.winfo_screenheight()
          return width,height

def get_new_shape_const_ratio(frame_width,frame_height,newsize_value):
    """
    büyük olan kenara göre resmi oranı bozmayarak görseli yeniden boyutlandırır.
    !newsize_value uzun kenardan düşük olmalıdır!
    [input] frame_width: resim genişlik, frame_height: resiim yükseklik, newsize_value: istenen uzun kenarı değeri
    [return] yeni boyut
    """
    frame_shape = (frame_width,frame_height)
    
    max_value = np.max(frame_shape)
    max_value_idx = np.argmax(frame_shape)
    
    if max_value > newsize_value:
        if max_value_idx == 0:
            new_height = int(newsize_value * frame_height / frame_width)
            new_width = newsize_value
        elif max_value_idx == 1:
            new_width = int(newsize_value * frame_width / frame_height)
            new_height = newsize_value
        frame_shape = (new_width,new_height)
        
    return frame_shape

def add_padding(image, padding_size):
    """
    Resme kenarlık ekler.
    input:
        image: eklenecek resim, 
        padding_size: kenar kalınlığı
    return: 
        image:
            kenarlık eklenmiş resim  
    """
    height, width = image.shape[:2]
    padded_image = np.zeros((height + 2 * padding_size, width + 2 * padding_size, 3), dtype=np.uint8)
    padded_image[padding_size:padding_size+height, padding_size:padding_size+width] = image
    return padded_image

def custom_BGR_to_gray(image, weights=[0.05, 0.05, 0.9]):
    """
    Verilen resmi istenen ağırlaklarda gri tonlamaya çevirir.
    input:
        image: resim
        weights: b,g,r ağırlıkları
    return:
        image: gri tonlamalı resim
    """
    b, g, r = cv2.split(image)
    gray = weights[0] * b + weights[1] * g + weights[2] * r
    return gray.astype('uint8')

def euclidean_distance(point1, point2):
    """
        İki nokta arasındaki Euclidean mesafesini hesaplar.
        input: 
            point1:ilk nokta (x,y)
            point2:ikinci nokta (x,y)
        return:
            mesafe
    """
    x1, y1 = point1
    x2, y2 = point2
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def convert_contours_to_seq(contours):
    contours_ = []
    for contour in contours:
        cnt = np.reshape(contour,(-1,2))
        for point in cnt:
            contours_.append(point)
    return np.array(contours_)

''' # Kütüphaneini yüklenmesi gerek!
def voc2yolo(xml_files_path):
     from pylabel import importer
     dataset = importer.ImportVOC(path=xml_files_path)
     dataset.export.ExportToYoloV5()
'''