import yaml
import os
import cv2
from typing import Callable
from datetime import datetime   
import pandas as pd
from ..dataset.spiral_object import SpiralObject
from IPython.display import clear_output
import shutil
import numpy as np

now = datetime.now()
date_string = now.strftime("%Y-%m-%d")


MAIN_PATH = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = MAIN_PATH + "/data"

class TestData:
    def __init__(self,path):
        """Bir test verisini ifade eder.
        input:
            path: Ana veri dosyası yolu
        """
        self.path = path
        self.name = self.path.split("/")[-1]
        self.type = self._read_info()
        self._paths()

    def _read_info(self):
        """Testin info.yaml içerisindeki türünü okur"""
        info = None
        with open(self.path+"/"+"info.yaml", 'r') as file:
            info= yaml.safe_load(file)
        type = info["type"]
        return type
    
    def _paths(self):
        """Testin altyollarını oluşturur"""
        pass

    def clear(self):
        """Test Verisinin tüm loglarını ve tüm tahminlerini temizler"""
        f = open(self.path + "/" + "logs.txt","w")
        f.close()

    def test(self):
        """Veriyi test eder"""
        pass

    def logs(self):
        """Testin loglarını okur"""
        with open(self.path + "/" + "logs.txt","r") as file:
            lines = file.readlines()
        for i,j in enumerate(lines):
            print(str(i)+" "+ j)
        
    def write_log(self,*text):
        """Testin loglarına log ekler"""
        full_text = " ".join(text)
        with open(self.path + "/" + "logs.txt","a") as file:
            file.write(full_text+ "\n")

    def get_object_predictions(self):
        """
        Bulunuyorsa eğer veriye ait önceden tahmin edilmiş obje tahminlerini döndürür.
        return:
            Dict{index:SpiralObject} frame sayısı ile indekslenmiş spiralobjectler
            eğer bulunmuyorsa None döndürülür.
        """
        preds = {}
        pred_names =  os.listdir(self.path + "/predictions/objects/")
        if len(pred_names) != 0:
            date_path = self.path + "/predictions/objects/" + pred_names[-1] 
            time_names =  os.listdir(date_path)
            if len(time_names) != 0:
                file_names = os.listdir(date_path + "/" + time_names[-1])
                for file_name in file_names:
                    file_path = date_path + "/"+ time_names[-1] + "/" + file_name
                    f = open(file_path,"r")
                    lines = f.readlines()

                    objects = []
                    for line in lines:
                        words = line.split(" ")
                        objects.append(SpiralObject(
                            label_index=int(words[0]),
                            confidence=float(words[5]),
                            x1=int(words[1]),
                            y1=int(words[2]),
                            x2=int(words[3]),
                            y2=int(words[4]),
                            ))
                    
                    preds[int(file_name.split(".")[0])] = objects
            print("Yüklendi: ",len(preds.values()))    
            self.write_log("kullanıldı: get_object_predictions")  
            return preds
        else:
            print("Bu veriye ait tahmin edilmiş objeler bulunamamaktadır")
            return None
        
    def get_translation_predictions(self):
        """
        Bulunuyorsa eğer veriye ait önceden tahmin edilmiş konum tahminlerini döndürür.
        return:
            eğer bulunuyorsa pd.DataFrame döndürülür.
            eğer bulunmuyorsa None döndürülür.       
        """
        pred_date_names = os.listdir(self.path + "/predictions/translations/")
        self.write_log("kullanıldı: get_translation_predictions")  

        if len(pred_date_names) != 0:
            pred_time_names = os.listdir(self.path + "/predictions/translations/" + pred_date_names[-1])
            if len(pred_time_names) != 0:
                pred_path = self.path + "/predictions/translations/" + pred_date_names[-1] + f"/{pred_time_names[-1]}"
                return pd.read_csv(pred_path)
            else:
                return None
        else:
            print("Bu veriye ait tahmin edilmiş konumlar bulunamamaktadır")
            return None

    def create(name,path,type):
        """Yeni veri oluşturmak için şablon oluşturur.
        input:
            name: Verinin ismi,
            path: verinin oluşturulacağı yerin yolun
            type: 'frames', 'video' veya 'images'
        """
        main_path = path + "/" + name
        if os.path.exists(main_path):
            assert "Bu isimde veri bulunuyor"
        os.mkdir(main_path)
        if type == 'video':
            os.mkdir(main_path + "/" + "predictions")
            os.mkdir(main_path + "/" + "predictions/objects")
            os.mkdir(main_path + "/" + "predictions/translations")
            os.mkdir(main_path + "/" + "predictions/videos")
            os.mkdir(main_path + "/" + "translations")
            os.mkdir(main_path + "/" + "video")
            with open(main_path + "/" + "logs.txt","w") as file:
                file.write("Oluşturuldu")
            with open(main_path + "/" +'info.yaml', 'w') as file:
                yaml.dump({'type':'video'}, file, default_flow_style=False)
        elif type == "frames":
            os.mkdir(main_path + "/" + "frames")
            os.mkdir(main_path + "/" + "translations")
            os.mkdir(main_path + "/" + "predictions")
            os.mkdir(main_path + "/" + "predictions/objects")
            os.mkdir(main_path + "/" + "predictions/translations")
            os.mkdir(main_path + "/" + "predictions/videos")
            with open(main_path + "/" + "logs.txt","w") as file:
                file.write("Oluşturuldu")
            with open(main_path + "/" +'info.yaml', 'w') as file:
                yaml.dump({'type':'frames'}, file, default_flow_style=False)
        elif type == "images":
            os.mkdir(main_path + "/" + "images")
            os.mkdir(main_path + "/" + "predictions")
            os.mkdir(main_path + "/" + "predictions/objects")
            os.mkdir(main_path + "/" + "predictions/images")
            with open(main_path + "/" + "logs.txt","w") as file:
                file.write("Oluşturuldu")
            with open(main_path + "/" + 'info.yaml', 'w') as file:
                yaml.dump({'type':'images'}, file, default_flow_style=False)
        else:
            assert "Yanlış girdi girildi, olması gereken girdiler: video,frames,images"
    

    

class _TestVid(TestData):
    def __init__(self, path):
        super().__init__(path)
        
    def _paths(self):
        # video yolu
        video_names = os.listdir(self.path + "/" + "video")
        if len(video_names) == 0:
            assert "Video verisi bulunamamaktadır"
            self.video_path = None
        else:
            self.video_path = self.path + "/video/" + video_names[-1]

        # gerçek konum yolu
        translations_names = os.listdir(self.path + "/translations/")
        if len(translations_names) == 0:
            print("Bu veriye ait konum verisi bulunmamaktadır")
            self.translations_path = None
        else:
            self.translations_path = self.path + "/translations/" +translations_names[-1]

        # tahmin objeler yolu
        predictied_objects_names = os.listdir(self.path + "/predictions/objects/")
        if len(predictied_objects_names) == 0:
            self.predictions_objects_path = None
            print("Bu veriye ait tahmin obje verisi bulunmamaktadır")
        else:
            self.predictions_objects_path = self.path + "/predictions/objects/" + predictied_objects_names[-1]

        # tahmin konumlar yolu
        predictied_translation_names = os.listdir(self.path + "/predictions/translations/")
        if len(predictied_translation_names) == 0:
            print("Bu veriye ait tahmin konum verisi bulunmamaktadır")
            self.predictions_translations_path = None
        else:
            self.predictions_translations_path = self.path + "/predictions/translations/" + predictied_translation_names[-1]

    def clear(self):
        """Test verisinin tüm tahminlerini ve loglarını temizler"""
        super().clear()
        for i in os.listdir(self.path + "/predictions/translations/"):
            shutil.rmtree(self.path + "/predictions/translations/" + i)
        for i in os.listdir(self.path + "/predictions/objects"):
            shutil.rmtree(self.path + "/predictions/objects/" + i)
        for i in os.listdir(self.path + "/predictions/videos"):
            shutil.rmtree(self.path + "/predictions/videos/" + i)
        print("tahmin ve log verileri temizleme işlemi tamamlandı")
        self.write_log("Loglar ve tahmin çıktı verileri temizlendi")

    def duplicate_like_frames(self):
        new_data_name  = self.name + "_duplicated_like_frame"
        TestData.create(new_data_name,DATA_PATH,"frames")
        self.write_log(new_data_name + " adlı bir frames kopya şablonu oluşturuldu")
        frame_counter = 0
        cap = cv2.VideoCapture(self.video_path)
        while True:
            ret,frame = cap.read()
            if ret:
                try:
                    cv2.imwrite(DATA_PATH + "/" + new_data_name + "/" + "frames" + "/" +f"frame_{frame_counter}.jpg",frame)
                    print(f"{frame_counter}.Yazıldı",end="\r")
                except:
                    print(f"{frame_counter}. frame yazılamadı")
                frame_counter += 1
            else:
                break
        self.write_log("frames kopyalama işlemi sona erdi")
        if self.translations_path is not None:
            shutil.copy(
                self.translations_path,
                DATA_PATH + "/" + new_data_name + "/translations/translations.csv"
                )
        self.write_log("Translations kopyalama işlemi sona erdi")
        


    def test(self,
             test_name:str = "test",
             test_func:Callable[[list,float,float,int,int],list]=None,
             frame_interval=1,
             frame_skip=0,
             with_translations=True,
             save_predicted_vid=False,
             save_predicted_objects=False,
             save_predicted_translations=False,
             predicted_vid_save_FPS =30,
             frame_display_shape=(1200,800)):
        """
        Veriyi test etmeye yarar \n
        input:
            test_name: Test özel olarak isimlendirmek için kulalnılır
            frame_interval: Frame atlama sayısı
            frame_skip: En baştan kaç frame'in atlanacağı
            with_translations: Eğer veri konum verisine sahipse onlarla birlikte test
            save_predicted_vid: True-> Tahmin edilmiş videyo kaydet
            save_predicted_objects: True-> Tahmin edilmiş objeleri kaydet
            save_predicteed_translations: True-> Tahmin edilmiş konumları kaydet
            predicted_vid_save_FPS: kaydedilecek tahmin videosunun kaç FPS olacağı
            frame_display_shape: frame gösterim boyutu
            test_func:
                function(frame,translation_x,translation_y,frame_counter,shown_frame_counter) -> frame, objects, (tranlation_x,translation_y)
                test edilecek fonksiyon, Fonksiyon girdi ve çıktıları belirtildiği gibi omka zorundadır.
        """
    
        now = datetime.now()
        date_string = now.strftime("%Y-%m-%d")
        time_string = now.strftime("%H-%M-%S")
        self.write_log(f"\n# test başlatıldı {date_string} {time_string} :{test_name} interval:{frame_interval} skip:{frame_skip} with_translations:{with_translations} save_predicted_[vid,objects,translations]:{save_predicted_vid},{save_predicted_objects},{save_predicted_translations} frame_display_shape:{frame_display_shape} save_fps:{predicted_vid_save_FPS}")  
        
        
        # eğer gerçek konum bilgileriyle çalışılacaksa
        if with_translations == True and self.translations_path is not None:
            real_translations = pd.read_csv(self.translations_path)
            real_translations_x = real_translations["translation_x"]
            real_translations_y = real_translations["translation_y"]
            self.write_log("translations başarıyla aktarıldı")  


        predicted_translations_x = []
        predicted_translations_y = []



        # Kaydediciyi başlatma
        if save_predicted_vid: 

            # Eğer test günlü bir dosya oluşturulmamışsa oluştur
            if os.path.exists(self.path + "/predictions/videos/" + date_string) == False:
                os.mkdir(self.path + "/predictions/videos/" + date_string)
                print("Yeni dosya oluşturuldu: ",self.path + "/predictions/videos/" + date_string)
                self.write_log("Yeni dosya oluşturuldu: ",self.path + "/predictions/videos/" + date_string)

            save_vid_name = time_string + "_"+ test_name + ".avi"
            self.write_log("test edilen video: "+str(save_vid_name))
            print(self.path + "/predictions/videos/" + date_string + "/" + save_vid_name)
            vid_save = cv2.VideoWriter(
                self.path + "/predictions/videos/" + date_string + "/" + save_vid_name ,  
                cv2.VideoWriter_fourcc(*'XVID'), 
                predicted_vid_save_FPS, 
                frame_display_shape) 
            
        # Baştan Frame atlama        
        cap = cv2.VideoCapture(self.video_path)
        for i in range(frame_skip):
            cap.read()

        frame_counter = 0
        shown_frame_counter = 0
        while True:
            objects = None
            ret,orig_frame = cap.read()
            if ret:
                if frame_counter % frame_interval == 0:
                    # eğer gerçek konumlar ile çalışılacaksa
                    if with_translations == True and self.translations_path is not None:
                        real_translation_x =  real_translations_x[frame_counter]
                        real_translation_y =  real_translations_y[frame_counter]
                    else:
                        real_translation_x = 0
                        real_translation_y = 0

                    # işlemeler
                    frame = orig_frame.copy()
                    if test_func is not None:
                        frame,objects,transltns = test_func(frame,real_translation_x,real_translation_y,frame_counter,shown_frame_counter)
                        predicted_translations_x.append(transltns[0])
                        predicted_translations_y.append(transltns[1])
                    frame = cv2.resize(frame,frame_display_shape)

                    # göster
                    window_name = "Test " + self.name
                    cv2.namedWindow(window_name)
                    cv2.moveWindow(window_name,20,20)
                    cv2.imshow(window_name,frame)
                    
                    key = cv2.waitKey(30)
                    if key == ord("q") or key == ord("Q"):
                        cv2.destroyAllWindows()
                        break
                    
                    # kaydet
                    if save_predicted_vid:
                        vid_save.write(frame.astype('uint8'))
                    
                    if save_predicted_objects:
                        if os.path.exists(self.path + "/predictions/objects" + "/" + date_string) == False:
                            os.mkdir(self.path + "/predictions/objects" + "/" + date_string)
                            print("Dosya oluşturuldu: ",self.path + "/predictions/objects" + "/" + date_string)
                            self.write_log("Dosya oluşturuldu: ",self.path + "/predictions/objects" + "/" + date_string)
                        if os.path.exists(self.path + "/predictions/objects" + "/" + date_string + "/" + time_string) == False:
                            os.mkdir(self.path + "/predictions/objects" + "/" + date_string + "/" + time_string)
                            print("Dosya oluşturuldu: ",self.path + "/predictions/objects" + "/" + date_string + "/" + time_string)
                            self.write_log("Dosya oluşturuldu: ",self.path + "/predictions/objects" + "/" + date_string + "/" + time_string)
                        with open(self.path + "/predictions/objects/" + date_string + "/" + time_string + f"/{frame_counter}.txt","w") as f:
                            for obj in objects:
                                row = f"{obj.label_idx} {obj.x1} {obj.y1} {obj.x2} {obj.y2} {obj.conf} {obj.landing_status}\n"
                                f.writelines(row)

                    shown_frame_counter +=1
                frame_counter+=1
            else:
                print("Video Okuma işlemi sonlandı")
                break

        cv2.destroyAllWindows()
        cap.release()
        if save_predicted_vid:
            vid_save.release()

        if save_predicted_translations:
            if os.path.exists(self.path + "/predictions/translations/" + date_string) == False:
                os.mkdir(self.path + "/predictions/translations/" + "/" + date_string)
                print("Dosya oluşturuldu: ",self.path + "/predictions/translations/" + "/" + date_string)
                self.write_log("Dosya oluşturuldu: ",self.path + "/predictions/translations/" + "/" + date_string)
            df = pd.DataFrame({
                'translation_x': predicted_translations_x,
                'translation_y': predicted_translations_y
            })

            # CSV dosyasını oluşturma
            df.to_csv(self.path + "/predictions/translations/" + date_string + "/" +f'translations_{time_string}.csv', index=False)
            self.write_log(f"translations_{time_string}.csv' başarıyla oluşturuldu")
        self.write_log("# Test sonlandı")

class _TestFrames(TestData):
    def __init__(self, path):
        super().__init__(path)
    
    def _paths(self):
        # görseller yolu
        frames_names = os.listdir(self.path + "/" + "frames")
        if len(frames_names) == 0:
            assert "Görseller verisi bulunamamaktadır"
            self.frames_path = None
        else:
            self.frames_path = self.path + "/frames/"

        # gerçek konum yolu
        translations_names = os.listdir(self.path + "/translations/")
        if len(translations_names) == 0:
            print("Bu veriye ait konum verisi bulunmamaktadır")
            self.translations_path = None
        else:
            self.translations_path = self.path + "/translations/" +translations_names[-1]

        # tahmin objeler yolu
        predictied_objects_names = os.listdir(self.path + "/predictions/objects/")
        if len(predictied_objects_names) == 0:
            self.predictions_objects_path = None
            print("Bu veriye ait tahmin obje verisi bulunmamaktadır")
        else:
            self.predictions_objects_path = self.path + "/predictions/objects/" + predictied_objects_names[-1]

        # tahmin konumlar yolu
        predictied_translation_names = os.listdir(self.path + "/predictions/translations/")
        if len(predictied_translation_names) == 0:
            print("Bu veriye ait tahmin konum verisi bulunmamaktadır")
            self.predictions_translations_path = None
        else:
            self.predictions_translations_path = self.path + "/predictions/translations/" + predictied_translation_names[-1]

    def clear(self):
        """Test verisinin tüm tahminlerini ve loglarını temizler"""
        super().clear()
        for i in os.listdir(self.path + "/predictions/translations/"):
            shutil.rmtree(self.path + "/predictions/translations/" + i)
        for i in os.listdir(self.path + "/predictions/objects"):
            shutil.rmtree(self.path + "/predictions/objects/" + i)
        for i in os.listdir(self.path + "/predictions/frames"):
            shutil.rmtree(self.path + "/predictions/frames/" + i)
        print("tahmin ve log verileri temizleme işlemi tamamlandı")
        self.write_log("Loglar ve tahmin çıktı verileri temizlendi")

    def duplicate_like_video(self,FPS=30):
        new_data_name  = self.name + "_duplicated_like_video" 
        TestData.create(new_data_name,DATA_PATH,"video")
        self.write_log(new_data_name + " adlı bir video kopya şablonu oluşturuldu")
        frame_names = os.listdir(self.frames_path)
        frame_shape = cv2.imread(self.frames_path + "/" + frame_names[0]).shape[:2]
        vid_save = cv2.VideoWriter(
            DATA_PATH + "/" + new_data_name + "/" + "video" + "/" + "video.avi",  
            cv2.VideoWriter_fourcc(*'XVID'), 
            FPS,
            frame_shape[::-1]
            ) 
    
        for frame_counter,frame_name in enumerate(frame_names):
            frame = cv2.imread(self.frames_path + "/" + frame_name)
            vid_save.write(frame.astype('uint8'))
            print(f"{frame_counter}. frame eklendi",end="\r")

        vid_save.release()
        self.write_log("Video kopyaleme işlemi sona erdi")
        if self.translations_path is not None:
            shutil.copy(
                self.translations_path,
                DATA_PATH + "/" + new_data_name + "/translations/translations.csv"
                )
        self.write_log("translations kopyalam işlemi sona erdi")

    def test(self,
             test_func:Callable[[list,float,float,int,int],list]=None,
             frame_interval=1,
             frame_skip=0,
             with_translations=True,
             save_predicted_frames=False,
             save_predicted_objects=False,
             save_predicted_translations=False,
             frame_display_shape=(1200,800)):
        """
        Veriyi test etmeye yarar \n
        input:
            frame_interval: Frame atlama sayısı
            frame_skip: En baştan kaç frame'in atlanacağı
            with_translations: Eğer veri konum verisine sahipse onlarla birlikte test
            save_predicted_frames: True-> Tahmin edilmiş görselleri kaydet
            save_predicted_objects: True-> Tahmin edilmiş objeleri kaydet
            save_predicteed_translations: True-> Tahmin edilmiş konumları kaydet
            frame_display_shape: frame gösterim boyutu
            test_func:
                function(frame,translation_x,translation_y,frame_counter,shown_frame_counter) -> frame, objects, (tranlation_x,translation_y)
                test edilecek fonksiyon, Fonksiyon girdi ve çıktıları belirtildiği gibi omka zorundadır.
        """
        now = datetime.now()
        date_string = now.strftime("%Y-%m-%d")
        time_string = now.strftime("%H-%M-%S")
        self.write_log(f"\n# Test başlatıldı {date_string} {time_string} : frame_interval:{frame_interval} frame_skip:{frame_skip} with_translations:{with_translations} save_predicted_[frames,objects,translations]:{save_predicted_frames},{save_predicted_objects},{save_predicted_translations} frame_display_shape:{frame_display_shape}")

        
        # eğer gerçek konum bilgileriyle çalışılacaksa
        if with_translations == True and self.translations_path is not None:
            real_translations = pd.read_csv(self.translations_path)
            real_translations_x = real_translations["translation_x"]
            real_translations_y = real_translations["translation_y"]

        predicted_translations_x = []
        predicted_translations_y = []

        # Kaydediciyi başlatma
        if save_predicted_frames: 

            # Eğer test günlü bir dosya oluşturulmamışsa oluştur
            if os.path.exists(self.path + "/predictions/frames/" + date_string) == False:
                os.mkdir(self.path + "/predictions/frames/" + date_string)
                print("Yeni dosya oluşturuldu: ",self.path + "/predictions/frames/" + date_string)
                self.write_log("Yeni dosya oluşturuldu: ",self.path + "/predictions/frames/" + date_string)
            if os.path.exists(self.path + "/predictions/frames/" + date_string + "/" + time_string) == False:
                os.mkdir(self.path + "/predictions/frames/" + date_string + "/" + time_string)
                print("Yeni dosya oluşturuldu: ",self.path + "/predictions/frames/" + date_string + "/" + time_string)
                self.write_log("Yeni dosya oluşturuldu: ",self.path + "/predictions/frames/" + date_string + "/" + time_string)
            
        # Baştan Frame atlama
        frame_names = os.listdir(self.frames_path) 
        del frame_names[0:frame_skip]       

        frame_counter = 0
        shown_frame_counter = 0
        while True:
            objects = None
            orig_frame = cv2.imread(self.frames_path + "/" + frame_names[frame_counter])
            if orig_frame is not None:
                if frame_counter % frame_interval == 0:
                    # eğer gerçek konumlar ile çalışılacaksa
                    if with_translations == True and self.translations_path is not None:
                        real_translation_x =  real_translations_x[frame_counter]
                        real_translation_y =  real_translations_y[frame_counter]
                    else:
                        real_translation_x = 0
                        real_translation_y = 0

                    # işlemeler
                    frame = orig_frame.copy()
                    if test_func is not None:
                        frame,objects,transltns = test_func(frame,real_translation_x,real_translation_y,frame_counter,shown_frame_counter)
                        predicted_translations_x.append(transltns[0])
                        predicted_translations_y.append(transltns[1])
                    frame = cv2.resize(frame,frame_display_shape)

                    # göster
                    window_name = "Test " + self.name
                    cv2.namedWindow(window_name)
                    cv2.moveWindow(window_name,20,20)
                    cv2.imshow(window_name,frame)
                    
                    key = cv2.waitKey(30)
                    if key == ord("q") or key == ord("Q"):
                        cv2.destroyAllWindows()
                        break
                    
                    # kaydet
                    if save_predicted_frames:
                        cv2.imwrite(self.path + "/predictions/frames/" + date_string  + "/" + time_string + "/"  f"frame_{frame_counter}.jpg",frame)
                    
                    if save_predicted_objects:
                        if os.path.exists(self.path + "/predictions/objects" + "/" + date_string) == False:
                            os.mkdir(self.path + "/predictions/objects" + "/" + date_string)
                            print("Dosya oluşturuldu: ",self.path + "/predictions/objects" + "/" + date_string)
                            self.write_log("Dosya oluşturuldu: ",self.path + "/predictions/objects" + "/" + date_string)
                        if os.path.exists(self.path + "/predictions/objects" + "/" + date_string + "/" + time_string) == False:
                            os.mkdir(self.path + "/predictions/objects" + "/" + date_string + "/" + time_string)
                            print("Dosya oluşturuldu: ",self.path + "/predictions/objects" + "/" + date_string + "/" + time_string)
                            self.write_log("Dosya oluşturuldu: ",self.path + "/predictions/objects" + "/" + date_string + "/" + time_string)
                        with open(self.path + "/predictions/objects/" + date_string + "/" + time_string + f"/{frame_counter}.txt","w") as f:
                            for obj in objects:
                                row = f"{obj.label_idx} {obj.x1} {obj.y1} {obj.x2} {obj.y2} {obj.conf} {obj.landing_status}\n"
                                f.writelines(row)

                    shown_frame_counter +=1
                frame_counter+=1
            else:
                print("Video Okuma işlemi sonlandı")
                break

        cv2.destroyAllWindows()



        if save_predicted_translations:
            if os.path.exists(self.path + "/predictions/translations/" + date_string) == False:
                os.mkdir(self.path + "/predictions/translations/" + "/" + date_string)
                print("Dosya oluşturuldu: ",self.path + "/predictions/translations/" + "/" + date_string)
                self.write_log("Dosya oluşturuldu: ",self.path + "/predictions/translations/" + "/" + date_string)

            df = pd.DataFrame({
                'translation_x': predicted_translations_x,
                'translation_y': predicted_translations_y
            })

            # CSV dosyasını oluşturma
            df.to_csv(self.path + "/predictions/translations/" + date_string + "/" +f'translations_{time_string}.csv', index=False)
            self.write_log(f'translations_{time_string}.csv dosyayı başarıyla oluşturuldu')
        self.write_log("# Test sonlandı")


class _TestImages(TestData):
    def __init__(self, path):
        super().__init__(path)
    
    def _paths(self):
        self.images_path = self.path + "/images"
        if os.path.exists(self.images_path) == False:
            assert "Verinin içerisinde images adlı bir dosya bulunmuyor."
        
        self.prediction_images_path = self.path + "/predictions/images"
        self.prediction_objects_path = self.path + "/predictions/objects"
    
    def clear(self):
        """Test verisinin tüm tahminlerini ve loglarını temizler"""
        super().clear()
        for i in os.listdir(self.path + "/predictions/objects"):
            shutil.rmtree(self.path + "/predictions/objects/" + i)
        for i in os.listdir(self.path + "/predictions/images"):
            shutil.rmtree(self.path + "/predictions/images/" + i)
        print("tahmin ve log verileri temizleme işlemi tamamlandı")
        self.write_log("Loglar ve tahmin çıktı verileri temizlendi")

    def get_translation_predictions(self):
        print("images türündeki veriler translations verisi bulunduramaz")

    def get_object_predictions(self):
        print("Images türündeki veriler objects verileri içeri aktaramaz")

    def test(self,test_func:Callable[[list,str],list,]=None,save_predicted_images=False,save_predicted_objects=False):
        """
        Veriyi test etmeye yarar \n
        q veya Q: bitir, a veya A: bir önceki resim, d veya D: bir sonraki resim \n
        input:
            test_func: function(frame, image_name)-> frame,objects : işlem fonksiyonu
            save_predicted_images: İşlem görmüş resimleri kaydet
            save_predicted_objects: işlemden alınmış objeleri kaydet
        """
        now = datetime.now()
        date_string = now.strftime("%Y-%m-%d")
        time_string = now.strftime("%H-%M-%S")
        self.write_log(f"\n# Test baştıldı {date_string} {time_string}: save_predicted_images:{save_predicted_images} save_predicted_objects:{save_predicted_objects}")
        
        # index ile resim seç
        image_names = os.listdir(self.images_path)
        for i ,  j in enumerate(image_names):
            print(i," ",j)
        k = int(input("İndeks seçin: "))
        assert k>= 0,"İndeks değeri pozitif olmalı"
        assert k < len(image_names),"indeks aşımı yapıldı"
        clear_output()


        # Eğer test günlü bir dosya oluşturulmamışsa oluştur
        if save_predicted_images:
            if os.path.exists(self.path + "/predictions/images/" + date_string) == False:
                os.mkdir(self.path + "/predictions/images/" + date_string)
                print("Yeni dosya oluşturuldu: ",self.path + "/predictions/images/" + date_string)
                self.write_log("Yeni dosya oluşturuldu: ",self.path + "/predictions/images/" + date_string)
            if os.path.exists(self.path + "/predictions/images/" + date_string + "/" + time_string) == False:
                os.mkdir(self.path + "/predictions/images/" + date_string+ "/" + time_string)
                print("Yeni dosya oluşturuldu: ",self.path + "/predictions/images/" + date_string+ "/" + time_string)
                self.write_log("Yeni dosya oluşturuldu: ",self.path + "/predictions/images/" + date_string+ "/" + time_string)
        if save_predicted_objects:
            if os.path.exists(self.path + "/predictions/objects" + "/" + date_string) == False:
                os.mkdir(self.path + "/predictions/objects" + "/" + date_string)
                print("Yeni dosya oluşturuldu:",self.path + "/predictions/objects" + "/" + date_string)
                self.write_log("Yeni dosya oluşturuldu:",self.path + "/predictions/objects" + "/" + date_string)
            if os.path.exists(self.path + "/predictions/objects" + "/" + date_string + "/" + time_string) == False:
                os.mkdir(self.path + "/predictions/objects" + "/" + date_string + "/" + time_string)
                print("Yeni dosya oluşturuldu: ",self.path + "/predictions/objects" + "/" + date_string + "/" + time_string)
                self.write_log("Yeni dosya oluşturuldu: ",self.path + "/predictions/objects" + "/" + date_string + "/" + time_string)
        window_name = "Test " + self.name
        cv2.namedWindow(window_name)
        while True:
            objects =None
            self.write_log("Test resmi: ",image_names[k])
            frame = cv2.imread(self.images_path + "/" + image_names[k])
            if test_func is not None:
                frame,objects = test_func(frame,image_names[k])
            
            if save_predicted_images:
                cv2.imwrite(self.path + "/predictions/images/" + date_string+ "/" + time_string + "/" + image_names[k],frame)

            if save_predicted_objects:
                with open(self.path + "/predictions/objects" + "/" + date_string + "/" + time_string + "/" + f"/{image_names[k]}.txt","w") as f:
                    for obj in objects:
                        row = f"{obj.label_idx} {obj.x1} {obj.y1} {obj.x2} {obj.y2} {obj.conf} {obj.landing_status}\n"
                        f.writelines(row)  

            cv2.putText(frame,"a:onceki d:sonraki q:bitir",(50,20),cv2.FONT_HERSHEY_DUPLEX,0.9,(0,0,0))
            cv2.putText(frame,image_names[k],(50,60),cv2.FONT_HERSHEY_DUPLEX,0.8,(0,0,0))

            cv2.moveWindow(window_name,20,20)
            cv2.imshow(window_name,frame)
            key = cv2.waitKey(0)
            if key == ord("q") or key ==ord("Q"):
                print("Test sonlandırıldı")
                cv2.destroyAllWindows()
                break
            elif key == ord("A") or key == ord("a"):
                k -= 1
                k = k % len(image_names)
                continue
            elif key == ord("D") or key == ord("d"):
                k += 1
                k = k % len(image_names)
                continue

        self.write_log("# Test sonlandırıldı")
    


def chose_test_data():
    root = os.path.dirname(os.path.abspath(__file__))
    data_names = os.listdir(root+"/"+"data")

    for i , j in enumerate(data_names):
        print(i," ",j)
    
    k = int(input("Seçin: "))
    assert isinstance(k,int) == True,"İndex int türünde olmalıdır"
    assert k < len(data_names), "İndex veri sayısını geçmemelidir"
    assert k >= 0, "İndex positif olmalıdır"

    data_type = TestData(root + "/data/" + data_names[k]).type
    data = None
    if data_type == "video":
        data = _TestVid(root + "/data/" + data_names[k])
    elif data_type == "images":
        data = _TestImages(root + "/data/" + data_names[k])
    elif data_type == "frames":
        data = _TestFrames(root + "/data/" + data_names[k])
    else:
        assert "Verinin türü info.yaml dosyasında yanlış belirtilmiştir"

    write_project_log("Test Verisi seçildi: ",data_names[k])
    return data

def chose_spiral_model():
    print(os.path.dirname(os.path.abspath(__file__)))
    model_names = os.listdir("/".join(os.path.dirname(os.path.abspath(__file__)).split('\\')[:-1]) + "/models")

    for i ,j in enumerate(model_names):
        print(i," ",j)
    k = int(input("İndex seçin: "))
    assert isinstance(k,int) == True, "index int türünde olmalıdır"
    assert k < len(model_names), "İndex veri sayısını geçmemelidir"
    assert k >= 0, "İndex positif olmalıdır"
    model_path = "/".join(os.path.dirname(os.path.abspath(__file__)).split("\\")[:-1]) + "/models" + "/" + model_names[k]
    write_project_log("Yolo ağırlığı seçildi: ",model_names[k])
    return model_path

def create_new_data(name,type):
    """
    Yeni test verisi oluştur
    input:
        name: Yeni verinin ismi
        type: 'video', 'frames' veya 'images' olmalıdır.
    """
    assert type in ["video","frames","images"] , "Yanlış girdi girildi"
    TestData.create(name,DATA_PATH,type)
    write_project_log("Yeni veri oluşturuldu: ",name)

def batch_test_videos(
             test_name:str = "batch_test",
             test_func:Callable[[list,float,float,int,int],list]=None,
             frame_interval=1,
             frame_skip=0,
             with_translations=True,
             save_predicted_vid=False,
             save_predicted_objects=False,
             save_predicted_translations=False,
             predicted_vid_save_FPS =30,
             frame_display_shape=(1200,800)):
    """Video türündeki tüm verileri test  etmeye yarar."""
    datas = []
    write_project_log("Yığın video test işlemi başlatıldı")

    k = int(input("0: Tüm verilerde test 1:Verileri seçerek test  :"))     
    assert k == 0 or k == 1,"Yanlış girdi girildi"

    if k == 0:
        data_names =os.listdir(DATA_PATH)
        for name in data_names:
            data_type = TestData(DATA_PATH + "/" + name).type
            if data_type == 'video':
                datas.append(_TestVid(DATA_PATH + "/" + name))
    elif k == 1:
        data_names = os.listdir(DATA_PATH)
        for i,name in enumerate(data_names):
            data_type = TestData(DATA_PATH + "/" + name).type
            if data_type == 'video':
                print(i," ",name)
        inp = input("Tercih ettiğiniz test verilerinin indexlerini ',' koyarak yazın. Örn:1,3,6,7\n")
        inps = inp.split(",")
        for i in inps:
            i = int(i)
            datas.append(_TestVid(DATA_PATH + "/" + data_names[i]))

    for data in datas:
        data.test(
            test_name=test_name,
            test_func=test_func,
            frame_interval=frame_interval,
            frame_skip=frame_skip,
            with_translations=with_translations,
            save_predicted_translations=save_predicted_translations,
            save_predicted_objects=save_predicted_objects,
            save_predicted_vid=save_predicted_vid,
            predicted_vid_save_FPS=predicted_vid_save_FPS,
            frame_display_shape=frame_display_shape
            )
        write_project_log("Veri test edildi: ",data.name)

        
def batch_test_frames(
             test_func:Callable[[list,float,float,int,int],list]=None,
             frame_interval=1,
             frame_skip=0,
             with_translations=True,
             save_predicted_frames=False,
             save_predicted_objects=False,
             save_predicted_translations=False,
             frame_display_shape=(1200,800)):
    """Frames türündeki tüm verileri test  etmeye yarar."""
    datas = []

    write_project_log("Yığın frames test işlemi başlatıldı")

    k = int(input("0: Tüm verilerde test 1:Verileri seçerek test: "))     
    assert k == 0 or k == 1,"Yanlış girdi girildi"

    if k == 0:
        data_names =os.listdir(DATA_PATH)
        for name in data_names:
            data_type = TestData(DATA_PATH + "/" + name).type
            if data_type == 'frames':
                datas.append(_TestFrames(DATA_PATH + "/" + name))
        write_project_log("Tüm verilerle test etme seçildi")
    elif k == 1:
        data_names = os.listdir(DATA_PATH)
        for i,name in enumerate(data_names):
            data_type = TestData(DATA_PATH + "/" + name).type
            if data_type == 'frames':
                print(i," ",name)
        inp = input("Tercih ettiğiniz test verilerinin indexlerini ',' koyarak yazın. Örn:1,3,6,7\n")
        inps = inp.split(",")
        for i in inps:
            i = int(i)
            datas.append(_TestFrames(DATA_PATH + "/" + data_names[i]))
        write_project_log("Şu verilerle test etme seçildi: ",inp)


    for data in datas:
        data.test(
            test_func=test_func,
            frame_interval=frame_interval,
            frame_skip=frame_skip,
            with_translations=with_translations,
            save_predicted_translations=save_predicted_translations,
            save_predicted_objects=save_predicted_objects,
            save_predicted_frames=save_predicted_frames,
            frame_display_shape=frame_display_shape
            )
        write_project_log("Veri test edildi: ",data.name)
    
        
def batch_test_images(test_func:Callable[[list,str],list,]=None,
                      save_predicted_images=False,
                      save_predicted_objects=False):
    """images türündeki tüm verileri test  etmeye yarar."""
    datas = []
    write_project_log("Yığın images test işlemi başlatıldı")

    k = int(input("0: Tüm verilerde test 1:Verileri seçerek test: "))     
    assert k == 0 or k == 1,"Yanlış girdi girildi"

    if k == 0:
        data_names =os.listdir(DATA_PATH)
        for name in data_names:
            data_type = TestData(DATA_PATH + "/" + name).type
            if data_type == 'images':
                datas.append(_TestImages(DATA_PATH + "/" + name))
        write_project_log("Tüm verilerle test etme seçildi")
        
    elif k == 1:
        data_names = os.listdir(DATA_PATH)
        for i,name in enumerate(data_names):
            data_type = TestData(DATA_PATH + "/" + name).type
            if data_type == 'images':
                print(i," ",name)
        inp = input("Tercih ettiğiniz test verilerinin indexlerini ',' koyarak yazın. Örn:1,3,6,7\n")
        inps = inp.split(",")
        for i in inps:
            i = int(i)
            datas.append(_TestImages(DATA_PATH + "/" + data_names[i]))
        write_project_log("Şu verilerle test etme seçildi: ",inp)
        
    for data in datas:
        data.test(
            test_func=test_func,
            save_predicted_objects=save_predicted_objects,
            save_predicted_images=save_predicted_images
            )
        write_project_log("Veri test edildi: ",data.name)
        


def write_project_log(*text):
    """project_logs.txt dosyasına log ekler"""
    full_text = date_string + " " + " ".join(text)
    os.path.dirname(os.path.abspath(__file__))
    with open(MAIN_PATH + "/" + "project_logs.txt","a") as file:
        file.write(full_text+ "\n")



def conjugate_videos(paths:list,save_dir,monitor_shape=(1920,1360,3)):
    """
    Verilen yollardaki videoları tek bir video haline getirerek kaydeder. İndex ile eşler.
    input:
        paths: list[str]
            Video yolları
        save_dir: str
            Kaydetme yolu
        momitor_shape: [int,int,int]
            kaydedilecek videonun (genişlik,yükseklik,kanal)
    """
    caps = [cv2.VideoCapture(path) for path in paths]
    slice_number = 2
    if len(paths) % 2 == 0:
        slice_number = len(paths)
    else:
        slice_number = len(paths)+1

    slice_height = int(monitor_shape[1] / 2)
    slice_width = int(monitor_shape[0] / (slice_number/2))
    monitor = np.zeros((monitor_shape[1],monitor_shape[0],monitor_shape[2]))
    print(monitor.shape)
    print("Dilim: h,w",slice_height,slice_width)
    print("Dilim sayısı: ",slice_number)

    vid_save = cv2.VideoWriter(
        save_dir + "/" + 'conjugated_video.avi' ,  
        cv2.VideoWriter_fourcc(*'XVID'), 
        30, 
        monitor_shape[:2]) 
    status = True
    frame_counter = 0
    while status:
        print("frame "+ str(frame_counter),end="\r")
        
        for i,cap in enumerate(caps):
            ret,frame = cap.read()
            
            if ret:
                frame = cv2.resize(frame,(slice_width,slice_height))
                cv2.putText(frame,paths[i].split("/")[-1],(10,30),cv2.FONT_HERSHEY_DUPLEX,0.8,(255,0,0))
                cv2.putText(frame,str(frame_counter),(10,80),cv2.FONT_HERSHEY_DUPLEX,0.8,(255,0,0))
                y = i % 2 
                x = i // 2
                monitor[y*slice_height:y*slice_height+slice_height,x*slice_width:x*slice_width+slice_width] = frame
            else:
                print("Yeni frame okunamadı")
                status = False
                break
        vid_save.write(monitor.astype('uint8'))
        frame_counter += 1
                
    cv2.destroyAllWindows()

    vid_save.release()