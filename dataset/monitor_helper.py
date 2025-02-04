from tools.constants import label_color_dict,label_dict,landing_status_dict,landing_status_color_dict
import cv2
import numpy as np
import matplotlib.pyplot as plt
import math
import os

def paint_weighted_color(image,x1,y1,x2,y2,color=[255,255,255],scale=0.7):
    roi = image[y1:y2,x1:x2]
    color_filter = np.resize(np.array(color,dtype=np.uint8),roi.shape)      
    colored = cv2.addWeighted(roi,scale,color_filter,0.3,0.0)

    image[y1:y2,x1:x2] = colored
    return image

class SpiralMonitorHelper:
    """
    Yarışma için doğrudan gerekli olmayan ama denetim için gerekli olan gösterime fonksiyonları
    """


    def paint_tracks(image,tracks,track_ids):
        """
        Yolo Tracking verilerini çizdirir.
        """
        for track_id in track_ids:
            track =tracks[track_id]
            points = np.hstack(track).astype(np.int32).reshape((-1, 1, 2))
            cv2.polylines(image, [points], isClosed=False, color=(230, 230, 230), thickness=3)
        return image

    def paint_objects(image,objects):
        """
        Bu fonksiyon objeleri ekrana çizer
        input:
            image: Üstüne çizilecek resim
            objects: Çizdirilecek SpiralObject türünden objeler
        return: 
            çzidirilmiş resim
        """
        
        if len(objects) > 0:
            print("Tespit edilen objeler\n")
            for obj in objects:
                print(obj)
                obj.conf = float("{:.3f}".format(obj.conf))
                image=paint_weighted_color(image,obj.x1,obj.y1,obj.x2,obj.y2,label_color_dict[obj.label_idx])
                cv2.rectangle(image,(obj.x1,obj.y1),(obj.x1+130,obj.y1-25),landing_status_color_dict[obj.landing_status],-1)
                cv2.rectangle(image,(obj.x1,obj.y1),(obj.x2,obj.y2),landing_status_color_dict[obj.landing_status],3)
                cv2.putText(image,f"{label_dict[obj.label_idx]} {obj.conf}",(obj.x1+5,obj.y1-5),cv2.FONT_HERSHEY_DUPLEX,0.8,(0,0,0))
        return image
    
    def paint_info(image,init_x=25,init_y=40,scale=0.7):
        """
        Bu fonksiyon sınıf renkleri gibi açıklayıcı metinleri ekrana yazdırır.
        input: 
            image: üstüne çizdirilecek resim
        return:
            image: çidirilmiş resim
        """
        paint_weighted_color(image,x1=0,y1=0,x2=340,y2=int(image.shape[0]/3))

        for j,info_text in enumerate(list(label_dict.values())[:-1]
                                    ):
            cv2.putText(image,info_text,(init_x+20,40*j+init_y),cv2.FONT_HERSHEY_DUPLEX,scale,(0,0,0))
            cv2.circle(image,(init_x-10,j*40+init_y-10),int(scale*10),label_color_dict[j],-1)
        
        for j,info_text in enumerate(list(landing_status_dict.values())):
            cv2.putText(image,info_text,(init_x+20,40*j+init_y+200),cv2.FONT_HERSHEY_DUPLEX,scale,(0,0,0))
            cv2.circle(image,(init_x-10,j*40+200+init_y-10),int(scale*10),list(landing_status_color_dict.values())[j],-1)    
            
        return image
    
    def paint_flows(image:list[int],flow_mask_image:list[int])->list[int]:
        """
        Optik akışların görselleştirilmiş hallerini resmet
        input:
            image: çizdirlecek resim
            flow_mask_image: flow_detector'ün içerdiği flow_mask resmi
        return:
            image: çizdirilmiş resim
        """
        return cv2.add(image,flow_mask_image)


        
    def paint_optical_flow_outputs(image,
                                   image_name,
                                   location_x,location_y,
                                   healt_status,
                                   coefficent_x,coefficent_y,
                                   transition_x_pix,transition_y_pix,
                                   direction_adjust_x="",direction_adjust_y="",
                                   show_decimals=2):
        """
        Optik akışlardan elde edilen bilgileri çizdir
        input:
            image: çizdirlecek resim
            transition_x: x'teki katedilen mesafe
            transition_y: y'deki katedilen mesafe
            location_x: x'deki mevcut konum
            location_y: y'deki mevcut konum
            healt_status: veri akış sağlık durumu
            coefficent_x: x ekseninde pikselden metreye geçiş katsayısı
            coefficent_y: y ekseninde pikselden metreye geçiş katsayısı
            transition_x_pix: x ekseninde piksel cinsinden katedilen mesafe
            transition_y_pix: y ekseninde piksel cinsinden katedilen mesafe
            directions_adjust_x: x ekseninde düzeltme katsayısı
            directions_adjust_y: y ekseninde düzeltme katsayısı
        return:
            image: çizdirilmiş resim        
        """
        
        paint_weighted_color(image,x1=0,y1=int(image.shape[0]/3),x2=340,y2=int(image.shape[0]/3*2))
        cv2.putText(image,f"frame : {image_name}",(10,int(image.shape[0]/3+20)),cv2.FONT_HERSHEY_DUPLEX,0.7,(0,0,0))  
        cv2.putText(image,f"mesafe (pix) x: {round(transition_x_pix,show_decimals)}",(10,int(image.shape[0]/3+50)),cv2.FONT_HERSHEY_DUPLEX,0.7,(0,0,0))
        cv2.putText(image,f"mesafe (pix) y: {round(transition_y_pix,show_decimals)}",(10,int(image.shape[0]/3+80)),cv2.FONT_HERSHEY_DUPLEX,0.7,(0,0,0))
        cv2.putText(image,f"pix2m coef_x: {round(coefficent_x,show_decimals)}",(10,int(image.shape[0]/3+110)),cv2.FONT_HERSHEY_DUPLEX,0.7,(0,0,0))
        cv2.putText(image,f"pix2m coef_y: {round(coefficent_y,show_decimals)}",(10,int(image.shape[0]/3+140)),cv2.FONT_HERSHEY_DUPLEX,0.7,(0,0,0))
        cv2.putText(image,f"health_status: {healt_status}",(10,int(image.shape[0]/3+170)),cv2.FONT_HERSHEY_DUPLEX,0.7,(0,0,0))
        cv2.putText(image,f"lokasyon (metre) X: {round(location_x,show_decimals)}",(10,int(image.shape[0]/3+200)),cv2.FONT_HERSHEY_DUPLEX,0.7,(0,0,0))
        cv2.putText(image,f"lokasyon (metre) Y: {round(location_y,show_decimals)}",(10,int(image.shape[0]/3+230)),cv2.FONT_HERSHEY_DUPLEX,0.7,(0,0,0))
        cv2.putText(image,f"düzeltme katsayi X: {direction_adjust_x}",(10,int(image.shape[0]/3+260)),cv2.FONT_HERSHEY_DUPLEX,0.7,(0,0,0))
        cv2.putText(image,f"düzeltme katsayi Y: {direction_adjust_y}",(10,int(image.shape[0]/3+290)),cv2.FONT_HERSHEY_DUPLEX,0.7,(0,0,0))

        return image    
    
    def paint_field_monitors(image,landing_field_monitors):
        paint_weighted_color(image,x1=0,y1=int(image.shape[0]/3*2),x2=340,y2=int(image.shape[0]))
        height = image.shape[0]
        for v_idx,field_monitor in enumerate(landing_field_monitors):
            for h_idx ,sub_monitor in enumerate(field_monitor):
                if len(sub_monitor.shape) == 2:
                    sub_monitor = cv2.cvtColor(sub_monitor,cv2.COLOR_GRAY2BGR)
                image[height-(v_idx + 1)*100:height-v_idx*100,20+h_idx*100:20+(h_idx+1)*100] = cv2.resize(sub_monitor,(100,100))

        return image
                

    def paint_logo(image):
        this_path = os.path.dirname(os.path.abspath(__file__))
        logo = cv2.imread(f"{this_path}/tools/logo.jpg")
        if logo.shape[0] >= image.shape[0]*2:
            print("Resim küçük oldugu için logo çizilemedi")
        else:
            w,h = logo.shape[1],logo.shape[0]
            image[0:logo.shape[0],340-w:340] = cv2.addWeighted(image[0:logo.shape[0],340-w:340],0.5,logo,0.5,0.0)
        return image
    


class referenceCoordinateSystem:
    ''' 
    Referans Koordinat Sistemi sınıfı

    Attributes:
        frameCount (int): İşlenecek toplam kare sayısı
        data_points1 (list): Birinci grafiğin koordinat bilgilerinin saklandığı list yapısı.
        data_points2 (list): İkinci grafiğin koordinat bilgilerinin saklandığı list yapısı.(opsiyonel)

    Kullanım:
        referenceCoordinateSystem sınıfı, ne kadar frame ile çalışılacaksa, initialize ederken frameCount değeri o kadar verilmelidir. Aksi takdirde
        ilk değerler dequeue edilerek kaybolacaktır. 
        plotTranslate fonksiyonu bir döngünün içine koyulmalıdır. Döngü boyunca x ve y değerleri her iterasyonda değişmelidir.
        Döngünün dışına döngü bittikten sonra plt.show() fonksiyonu yerleştirilmelidir.
    '''
    def __init__(self,frameCount, enableSecondPlot=False,lineColor1="blue", scatterColor1="blue", 
                 lineColor2="green", scatterColor2="green"):
        ''' 
        referenceCoordinateSystem sınıfının constructor'ı

        Parameters:
            frameCount (int): Toplam işlenecek frame sayısı.(Şartnamede bu sayı 2250 olarak belirlenmiştir)
            enableSecondPlot (boolean): Ekranda ikinci bir grafik göstermek için. Default olarak False. (Opsiyonel)
            lineColor1: Birinci grafiğin çizgilerinin rengi. Default olarak "blue". (Opsiyonel)
            scantterColor1: Birinci grafiğin nokta rengi. Default olarak "blue". (Opsiyonel)
            lineColor2: İkinci grafiğin çizgilerinin rengi. Default olarak "green". (Opsiyonel)
            scantterColor2: İkinci grafiğin nokta rengi. Default olarak "green". (Opsiyonel)
        '''
        self.frameCount = int(frameCount)


        self.data_points1 = []  # Birinci veri seti için koordinat bilgilerinin saklanacağı array
        self.data_points2 = []  # İkinci veri seti için koordinat bilgilerinin saklanacağı array


        fig, self.ax = plt.subplots()

        self.lineColor1 = lineColor1
        self.scatterColor1 = scatterColor1
        self.lineColor2 = lineColor2
        self.scatterColor2 = scatterColor2
        self.enableSecondPlot = enableSecondPlot

        self.line1, = self.ax.plot([], [], color=self.lineColor1, label='Line 1')
        self.scatter1 = self.ax.scatter([], [], color=self.scatterColor1, label='Scatter 1')

        if self.enableSecondPlot:
            self.line2, = self.ax.plot([], [], color=self.lineColor2, label='Line 2')
            self.scatter2 = self.ax.scatter([], [], color=self.scatterColor2, label='Scatter 2')

        self.ax.set_xlim(-100,100) #x ekseni 0-100'e kadar şeklinde limit verildi
        self.ax.set_ylim(-100,100) #y ekseni 0-100'e kadar limit verildi (Bu iki değer keyfe göre değiştirilebilir. Başlangıçtaki sınırları değiştirmeye yarar)
        self.ax.legend()

    def plotTranslate(self,x,y, plotIndex=1,lineColor = None, scatterColor = None):
        '''
            X ve Y koordinatlarını grafikte gösteren fonksiyon. Bir döngü içinde kullanılmalıdır ve yeni koordinat bilgileri her 
            döngüde fonksiyona verilmelidir. Döngü dışına ise hemen sonra plt.show() fonksiyonu konularak görsel bir grafik elde
            edilir.

            Parameters:
                x (float): Yeni x değeri
                y (float): Yeni y değeri 
        '''

        if lineColor is None:
            lineColor = self.lineColor1 if plotIndex == 1 else self.lineColor2
        if scatterColor is None:
            scatterColor = self.scatterColor1 if plotIndex == 1 else self.scatterColor2

        new_x = x #Yeni x değeri
        new_y = y #Yeni y değeri
        
        if plotIndex == 1:
            self.data_points1.append((new_x, new_y))
            x_values = [x for x, y in self.data_points1]
            y_values = [y for x, y in self.data_points1]
            self.scatter1.set_offsets(list(zip(x_values, y_values)))
            self.scatter1.set_color(scatterColor)
            self.line1.set_data(x_values, y_values)
            self.line1.set_color(lineColor)
        elif plotIndex == 2 and self.enableSecondPlot:
            self.data_points2.append((new_x, new_y))
            x_values = [x for x, y in self.data_points2]
            y_values = [y for x, y in self.data_points2]
            self.scatter2.set_offsets(list(zip(x_values, y_values)))
            self.scatter2.set_color(scatterColor)
            self.line2.set_data(x_values, y_values)
            self.line2.set_color(lineColor)

        
        plt.pause(1/30)  #Grafiği güncelleyebilmek için gereken fonksiyon


class errorCalculator:
    """
    Gerçek lokasyon verileri ile tahmin edilen verileri karşılaştırıp hata oranını bulur

    Attributes:
        meanError (float): Ortalama hata
        length (int): Verilerin uzunluğu
        summ (float): Hataların toplamı(sum yazamıyordum o yüzden summ yazdım)

    """

    def __init__(self):
        self.meanError = 0
        self.length = 0
        self.summ = 0
    
    def calculateError(self,real_x,real_y,predicted_x,predicted_y):
        """
        Hata hesaplama fonksiyonu. Döngü içinde çalıştırılmalıdır.

        Parameters:
            real_x (float): Gerçek x lokasyon verisi
            real_y (float): Gerçek y lokasyon verisi
            predicted_x (float): Tahmin edilen x lokasyon verisi
            predicted_y (float): Tahmin edilen y lokasyon verisi
        """
        self.summ += math.sqrt((real_x-predicted_x)**2 + (real_y-predicted_y)**2) #Şartnamedeki denklem kullandım
        self.length += 1
        self.meanError = self.summ/self.length
