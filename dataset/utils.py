from IPython.display import clear_output
from tools.utils import path_sequence
import os
from datetime import datetime

file_path = os.path.dirname(os.path.abspath(__file__))

def add_log(log:str):
    """
    Loglama işlemi
    """

    f = open(path_sequence(file_path,'logs.txt'),"a")
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
