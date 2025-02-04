from tools.constants import label_dict
from spiral_object import SpiralObject

class SpiralDatasetObject:

    def __init__(self,label_index,cx,cy,cw,ch):
        """
        XYWHN formatındaki objelerdir
        input:
            label_index:int: veri etiketi: 0,1,2,3
            confidenfce:float: tahmin olasılığı
            cx: float: normalize obje merkez x
            cy: float: normalize obje merkez y
            cw: float: normalize obje genişlik
            ch: float: normalize obje yükseklik         
        """
        
        self.label_idx = int(label_index)
        self.cx = cx
        self.cy = cy
        self.cw = cw
        self.ch = ch

    def __str__(self):
        return f"Nesne: {label_dict[self.label_idx]} cx:{self.cx} cy:{self.cy} cw:{self.x2} ch:{self.y2}"
    

    def get_like_spiral_object(self):
        """
        SpiralObject: Verileri XYXYN formatında al
        """
        x1 = self.cx - self.cw*0.5
        y1 = self.cy - self.ch*0.5
        x2 = self.cx + self.cw*0.5
        y2 = self.cy + self.ch*0.5        

        return SpiralObject(
            label_index=self.label_idx,
            confidence=-1,
            x1=x1,
            y1=y1,
            x2=x2,
            y2=y2
            )