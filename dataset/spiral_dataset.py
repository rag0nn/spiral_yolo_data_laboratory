from tools.utils import path_sequence
import os
from spiral_data import SpiralData
from utils import add_log
from tqdm import tqdm
import numpy as np

class SpiralDataset:
    def __init__(self,path):
        self.path = path
        self.name =self.path.split("/")[-1]
        self.image_paths = []
        self.txt_paths = []


        self.load_data_paths()
        self.check_data_balance()

    def __str__(self):
        return f"{self.name}"
    
    def load_data_paths(self):
        self.image_paths.clear()
        self.txt_paths.clear()
        for cat in ["train","val","test"]:
            im_names = os.listdir(  path_sequence(self.path,"detect","images",cat))
            for im_name in im_names:
                self.image_paths.append(path_sequence(self.path,"detect","images",cat,im_name))
            txt_names = os.listdir(path_sequence(self.path,"detect","labels",cat))
            for txt_name in txt_names:
                self.txt_paths.append(path_sequence(self.path,"detect","labels",cat,txt_name))
    
    def get_datas(self):
        """
        return:
            List(SpiralData): image ve txt pathlarden SpiralData oluşturur ve geri döndürür
        """
        datas = []
        for i,j in zip(self.image_paths,self.txt_paths):
            datas.append(SpiralData(i,j))
        return datas
    
    def check_data_balance(self):
        """
        Veri setinin eşlenik olması gereken txt - image dosyalarının durumunu kontrol eder.
        """
        im_names = []
        txt_names = []
        problems = []
        for im_path,txt_path in zip(self.image_paths,self.txt_paths):
            im_name = im_path.split("/")[-1].split(".")[-2]
            im_names.append(im_name)
            txt_name = txt_path.split("/")[-1].split(".")[-2]
            txt_names.append(txt_name)
        for im_name in tqdm(im_names):
            if im_name not in txt_names:
                problems.append(f"image {im_name}")
                print(f"{im_name} bir txt dosyasıyla eşleşmedi")
        for txt_name in tqdm(txt_names):
            if txt_name not in im_names:
                problems.append(f"txt {txt_name}")
                print(f"{txt_name} bir image dosyasıyla eşleşmedi")
        if len(problems) == 0:
            print("Tüm txt-image çiftleri eşleşiyor.")
            add_log(f'{self.name} veri eşleşimi kontrolü: problemsiz')
        else:
            add_log(f"{self.name} veri eşleşimi kontrolü: eşleşmeyen veriler var")

        return problems
    
    def check_non_scale_labels(self):
        """
        Veri setinin etiketleri içerisinde 0 ile 1 arasında etiketin olup olmadığını kontrol eder
        """
        for im_path,txt_path in zip(self.image_paths,self.txt_paths):
            data = SpiralData(im_path,txt_path)
            for index,[lbl,x,y,w,h] in enumerate(data.labels):
                for i in [x,y,w,h]:
                    if i <0 or i>1:
                        print(f"0-1 Arasında scale olmamış veri bulundu: {i} at {index}  -- ",self,data.txt_path)

        

    def analyze(self):
        """
        Veri setinin istatiksel bilgilerini döndürür.
        return:
            dict: içerdiği toplam etiket sayıları, int: toplam etiket sayısı: int:toplam frame sayısı
        """
        total_label_count = 0
        total_frame_count = len(self.image_paths)

        label_counts = {0:0,1:0,2:0,3:0}
        parts_labels_counts = {"train":{0:0,1:0,2:0,3:0},"test":{0:0,1:0,2:0,3:0},"val":{0:0,1:0,2:0,3:0}}
        for im_path,txt_path in zip(self.image_paths,self.txt_paths):
            part = im_path.split("/")[-2]
            data = SpiralData( image_path=im_path,txt_path=txt_path)
            total_label_count += data.total_label_count
            for lbl in list(data.label_counts.keys()):
                if lbl in list(label_counts.keys()):
                    label_counts[lbl] += data.label_counts[lbl]
                else:
                    label_counts[lbl] = data.label_counts[lbl]
                parts_labels_counts[part][lbl] += data.label_counts[lbl]
                
        sorted_total_label_counts = {k: label_counts[k] for k in sorted(label_counts)}
        add_log(f'{self.name} analiz')
        print(parts_labels_counts)
        
        return sorted_total_label_counts,total_label_count,total_frame_count
    
    def convert_labels(self,targets:dict):
        """
        Veri setinin etiketlerini dönüştürür
        input:
            targets: Mevcut etiketlerin hangi etiketlere karşılık geleceğini belirler   
        örnek kullanım:
            convert_labels({0:1,1:2,2:0})
            => 0 etiketleri 1'e, 1 etiketleri 2'ye 2'leri 3'e dönüştürür.
        """
        for im_path,txt_path in tqdm(zip(self.image_paths,self.txt_paths)):
            data = SpiralData( image_path=im_path,txt_path=txt_path)       
            data.convert_labels(targets=targets)
        add_log(f'{self.name} etiket dönüşümü: {list(targets.keys())} -> {list(targets.values())}')

    def augment(self,min_angle,max_angle):
        import random
        from spiral_data_organization import create_dataset

        aug_name =f"{self.name}_aug_r_{min_angle}_{max_angle}"
        create_dataset(aug_name)
        
        datas = self.get_datas()
        for data in tqdm(datas):
            angle = random.randint(min_angle,max_angle)
            
            im_name_parts = data.image_path.split("/")
            im_name_parts[-5] = aug_name
            new_im_path = "/".join(im_name_parts)

            txt_name_parts = data.txt_path.split("/")
            txt_name_parts[-5] = aug_name
            new_txt_path = "/".join(txt_name_parts)


            data.augment_zoom_and_rotate_data(new_im_path,new_txt_path, angle, coord=None)


    def resize_frames(self,newsize_value:int):
        """
        Framelerin boyutunu en boy oranını bozmadan dönüştürür.
        input:
            new_size_value: uzun kenarın değerinin kaç olması isteniyorsa
        """
        for im_path,txt_path in tqdm(zip(self.image_paths,self.txt_paths)):  
            data = SpiralData( image_path=im_path,txt_path=txt_path) 
            data.resize_image(newsize_value=newsize_value)
            
        add_log(f'{self.name} frame yeniden boyutlandırma: {newsize_value}')

    def slice(self,slice_width,slice_height,cover_objectless_datas=False):
        from  spiral_data_organization import create_dataset
        new_name =f"{self.name}_sliced"
        create_dataset(new_name)
        
        datas = self.get_datas()

        for data in tqdm(datas):
            data:SpiralData
            
            im_name_parts = data.image_path.split("/")
            im_name_parts[-5] = new_name
            new_im_path = "/".join(im_name_parts[:-1])

            txt_name_parts = data.txt_path.split("/")
            txt_name_parts[-5] = new_name
            new_txt_path = "/".join(txt_name_parts[:-1])

            data.slice(
                slice_width,slice_height,
                new_im_path,new_txt_path,
                cover_objectless_data=cover_objectless_datas,info=False)
        add_log(f'{self.name} veri dilimleme: slice w,h{slice_width,slice_height}')

    def apply_train_test_split(self,train=0.6,val=0.25):
        """
        Etiket sayısına göre veri setini train test val olarak ayırır.

        Nasıl İşliyor:
            dataset label countları al
            train test katsayıları ile her parçaya kaç adet label count düşecek onu hesapla
            datasetteki verileri dolaşmaya başla
            her veri için:
                verinin doyurma katsayısılarını hesapla
                train test val 'ın açlık katsayılarını hesapla
                doyurma kaysayılarından max olan label'ı seç ve o labela en aç olan parçayı seç
                veriyi o parçaya ekle
        """
        # veri setinin içerdiği etiket sayıları
        dataset_label_counts = list(self.analyze()[0].values())
        # katsayılara göre train test split ayrışım sayıları
        train_splits,test_splits,val_splits = [],[],[]
        for value in dataset_label_counts:
            train_splits.append(int(value * train))
        for value in dataset_label_counts:
            val_splits.append(int(value * val))
        for i in range(4):
            test_splits.append(dataset_label_counts[i]-(train_splits[i] + val_splits[i]))
        print("Mevcut toplam dağılım",dataset_label_counts)
        print("İstenen train",train_splits)
        print("İstenen  test",test_splits)
        print("İstenen   val",val_splits)

        # verinin besin değerleri ve besini döndürür
        def find_feeding(spiral_data):

            data_dict = {0:0,1:0,2:0,3:0}
                
            for key,value in spiral_data.label_counts.items():
                data_dict[key] = value
            data_values = np.array(list(data_dict.values()))
            total = data_values.sum()
            feeding = data_values / total
            #print(feeding)
            return feeding,data_dict
        # kategorinin ne kadar açlığı olduğunu döndürür
        def find_starvation(current_values,target_values):
            starvations = []
            for i in range(4):
                if target_values[i] == 0: target_values[i] += 0.000001
                starvations.append(current_values[i] / target_values[i])
            return starvations

        train_paths,test_paths,val_paths = [],[],[]
        train_counts,test_counts,val_counts = [0,0,0,0],[0,0,0,0],[0,0,0,0]
        for im_path,txt_path in zip(self.image_paths,self.txt_paths):
            cof,food = find_feeding(SpiralData(im_path,txt_path))
            primary_food_index = cof.argmax()
            #print(primary_food_index)

            train_starvation = find_starvation(train_counts,train_splits)
            test_starvation = find_starvation(test_counts,test_splits)
            val_starvation = find_starvation(val_counts,val_splits)
            chosen_part_index = np.array([train_starvation[primary_food_index],val_starvation[primary_food_index],test_starvation[primary_food_index]]).argmin()
            
            if chosen_part_index == 0:
                train_paths.append(SpiralData(im_path,txt_path))
                for i in range(len(train_counts)):
                    train_counts[i] +=food[i]
            elif chosen_part_index == 1:
                val_paths.append(SpiralData(im_path,txt_path))
                for i in range(len(val_counts)):
                    val_counts[i] +=food[i]
            elif chosen_part_index == 2:
                test_paths.append(SpiralData(im_path,txt_path))
                for i in range(len(test_counts)):
                    test_counts[i] +=food[i]
        print("\nTrain Beklenen: ",train_splits,"Ulaşılan ",train_counts)
        print("Test Beklenen: ",test_splits,"Ulaşılan ",test_counts)
        print("Val Beklenen: ",val_splits,"Ulaşılan ",val_counts)

        print("Train Veri dosyası sayısı: ",len(train_paths))
        print("Test Veri dosyası sayısı: ",len(test_paths))
        print("Val Veri dosyası sayısı: ",len(val_paths))
        # dağıtımı uygulayalım
        def apply(datas,part):
            for data in datas:
                os.replace(data.image_path,f"{self.path}/detect/images/{part}/{data.data_name}.jpg")
                os.replace(data.txt_path,f"{self.path}/detect/labels/{part}/{data.data_name}.txt")
            print("Dağıtma işlemi başarılı ", self.path)
        apply(train_paths,"train")
        apply(test_paths,"test")
        apply(val_paths,"val")

        add_log(f"{self.name} train test val split: başarılı")

        self.load_data_paths()


