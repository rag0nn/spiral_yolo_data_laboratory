from tools.constants import label_dict

class SpiralObject:
    """
    Obje: xyxyn
    input:
        label_idx:int:  Etiket indeksi: 0,1,2,3
        x1:int : normalize sol_üst_x
        y1:int : normalize sol_üst_y 
        x2:int : normalize sol_alt_x 
        y1:int : normalize sol_alt_y
        confidence:float: objenin tahmin olasılığı
        landing_status:int: İnişe uygunluk: 0,1,3
            -1: iniş alanı değil
            0: iniş alanı ama uygun değil
            1: iniş alanı ve uygun       
    """
    def __init__(self,label_index,confidence,x1,y1,x2,y2):
        self.label_idx = int(label_index)
        self.conf = float(confidence)
        self.x1 = float(x1)
        self.y1 = float(y1)
        self.x2 = float(x2)
        self.y2 = float(y2)

        if self.label_idx == 0:
            self.landing_status = -1
        elif self.label_idx == 1:
            self.landing_status = -1
        elif self.label_idx == 2:
            self.landing_status = 1
        elif self.label_idx == 3:
            self.landing_status = 1

    def convert_to_absolute_coordinates(self,image_width,image_height):
        """
        Nesnenin normalize edilmiş(0-1 arasında) olan koordinatları direkt piksel koordinatlarına çevirir.
        xyxyn -> xyxy
        input:
            image_width: resmin genişliği
            image_height: resmin yüksekliği
        """
        self.x1 = int(self.x1 * image_width)
        self.x2 = int(self.x2 * image_width)
        self.y1 = int(self.y1 * image_height)
        self.y2 = int(self.y2 * image_height)


    def __str__(self):
        return f"Nesne: {label_dict[self.label_idx]} iniş durumu: {self.landing_status} x1:{self.x1} y1:{self.y1} x2:{self.x2} y2:{self.y2}  conf:{self.conf}"

    def get_label_index_like_tag(self):
        """
        Sınıfı(cls) Tasit,Insan,UAP,UAI şeklinde döndürür
        """
        classes = {
            0:"Tasit",
            1:"Insan",
            2:"UAP", 
            3:"UAI" 
        }

        return classes[self.label_idx]


    def get_landing_status_like_tag(self):
        """
        İniş durumu (landing_status)'u  Inilebilir,Inilemez,Inis Alani Degil şeklinde döndürür.
        """
        landing_statuses = {
            1:"Inilebilir",
            0:"Inilemez",
            -1:"Inis Alani Degil"
        }

        return landing_statuses[self.landing_status]
    
    def convert_coordinates_to_int(self):
        """
        float değerlikli olan koordinat değerlerini integera çevirir
        """
        self.x1 = int(self.x1)
        self.y1 = int(self.y1)
        self.x2 = int(self.x2)
        self.y2 = int(self.y2)
        

     