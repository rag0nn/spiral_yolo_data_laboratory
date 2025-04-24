import cv2
import numpy as np
from tools.object import SpiralObject
import os
import warnings


class SpiralData:
    def __init__(self,image_path:str,txt_path:str):
        self.image_path = image_path
        self.txt_path = txt_path
        self.data_name = ''.join(self.txt_path.split("/")[-1].split('.')[:-1])
        self.label_counts = {}
        self.total_label_count = 0
        self.labels = []
        self._load_labels_and_stats()

    def __str__(self) -> str:        
        return f'veri: {self.data_name} im_path: {self.image_path}, txt_path: {self.txt_path}'
    
    def _format_line(self,line):
        words = line.split(" ")
        return int(words[0]),float(words[1]),float(words[2]),float(words[3]),float(words[4])
 
    def _load_labels_and_stats(self):

        f = open(self.txt_path,"r")
        lines = f.readlines()
        f.close()

        for line in lines:
            lbl_index,center_x,center_y,center_width,center_height = self._format_line(line)
            self.labels.append((lbl_index,center_x,center_y,center_width,center_height))
            self.total_label_count += 1
            if lbl_index in list(self.label_counts.keys()):
                self.label_counts[lbl_index] += 1
            else:
                self.label_counts[lbl_index] = 1
    
    def get_as_absoluate_coordinates(self,frame_shape):
        """
        Etiketleri SpiralObject cinsine dönüştürmeye ve girilen boyutlarla çarparak gerçek koordinatlara çevirmeye yarar.
        input:  
            frame_shape: frame_width,frame_height
        return:
			List(SpiralObject): Etiketlerin spiral object cinsinden ve tam koordinatlı biçimi
        """
        objects = []
        for lbl_index,center_x,center_y,center_width,center_height in self.labels:
            obj = SpiralObject(
                label_index=lbl_index,
                confidence=1,
                x1 = float(center_x - center_width/2),
                y1 = float(center_y - center_height/2), 
                x2 = float(center_x + center_width/2),
                y2 = float(center_y + center_height/2 )
                       )
            obj.convert_to_absolute_coordinates(image_width=frame_shape[1],image_height=frame_shape[0])
            objects.append(obj)
        return objects
    
    def convert_labels(self,targets:dict):
        """
        Verilerin içesisindeki etiketleri değiştirmeye yarar
        input:
	 		targets: Mevcut etiketlerin hangi etiketlere karşılık geleceğini belirler   
        """
        newlines = []
        for lbl,cx,cy,cw,ch in self.labels: 
            print(targets)
            new_lbl = targets[lbl]
            newlines.append(f"{new_lbl} {cx} {cy} {cw} {ch}\n")

        f = open(self.txt_path,"w")
        f.writelines(newlines)
        f.close()
        print(f"Dönüştürüldü: {self.data_name}")

    def resize_image(self,newsize_value):
        """
        Girilen boyuta göre veri görselinin en ve boy oranını koruyayarak küçültme işlemi yapar. Eğer veri her türlü girilen değerden küçükse bir değişiklik yapılmaz
        input:
			Yeniden boyutlandırılan görselin uzun kenarının ne kadar olacağı
        """
        im = cv2.imread(self.image_path)
        frame_height,frame_width = im.shape[0],im.shape[1]
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
        

            im = cv2.resize(im,frame_shape)
            cv2.imwrite(self.image_path,im)

    def remove_data(self):
        """
        Verinin image ve txt dosyalarını bellekten siler.
        """
        for path in [self.image_path,self.txt_path]:
            if os.path.exists(path):
                os.remove(path)
                print("kaldırıldı: ",path)
            else:
                print("belirtilen yolda dosya bulunamadı: ", path)



    def augment_zoom_and_rotate_data(self, im_save_path, txt_save_path, angle, zoom='adaptive', coord=None):
        """
        Yakınlaştırma ve döndürme kullanarak veriyi çoğalt
        input:
            im_save_path: Çoğaltılan resmin kaydedileceği konum
            txt_save_path: Çoğaltılen etiketlerinin kaydedileceği konum
            angle: döndürme açısı
            zoom: büyütme boyutu
            coord: Döndürme merkez koordinatı (x,y) 
        """
        def get_rotated_box_coords(cx, cy, w, h, rot_mat):
            # Kutunun köşe noktalarını hesaplayalım
            box_coords = np.array([
                [cx - w / 2, cy - h / 2],
                [cx + w / 2, cy - h / 2],
                [cx - w / 2, cy + h / 2],
                [cx + w / 2, cy + h / 2]
            ])

            # Dönüşüm matrisini kutunun köşelerine uygulayalım
            ones = np.ones(shape=(len(box_coords), 1))
            coords_ones = np.hstack([box_coords, ones])
            rotated_coords = rot_mat.dot(coords_ones.T).T

            return rotated_coords
        
        image = cv2.imread(self.image_path)

        if zoom == 'adaptive':
            max_zoom = image.shape[1] / image.shape[0]
            zoom = (max_zoom - 1) * (angle % 90) / 90 + 1.8

        # Görüntünün genişliği ve yüksekliğini alalım
        img_h, img_w = image.shape[:2]

        rot_cy, rot_cx = [i / 2 for i in image.shape[:-1]] if coord is None else coord[::-1]

        rot_mat = cv2.getRotationMatrix2D((rot_cx, rot_cy), angle, zoom)

        rotated_image = cv2.warpAffine(image, rot_mat, (img_w, img_h), flags=cv2.INTER_LINEAR)

        rotated_objects = []

        for lbl, cx, cy, cw, ch in self.labels:
            # Koordinatları ve boyutları piksel cinsinden hesaplayalım
            cx = cx * img_w
            cy = cy * img_h
            box_w = cw * img_w
            box_h = ch * img_h

            # Kutunun dönüşten sonraki köşe noktalarını hesaplayalım
            rotated_coords = get_rotated_box_coords(cx, cy, box_w, box_h, rot_mat)

            # Dönüşen kutunun yeni sınırlarını hesaplayalım
            x_coords = rotated_coords[:, 0]
            y_coords = rotated_coords[:, 1]
            new_cx = (x_coords.max() + x_coords.min()) / 2
            new_cy = (y_coords.max() + y_coords.min()) / 2
            new_box_w = x_coords.max() - x_coords.min()
            new_box_h = y_coords.max() - y_coords.min()

            # Yeni YOLO etiketlerini normalize edelim
            new_cx /= img_w
            new_cy /= img_h
            new_cw = new_box_w / img_w
            new_ch = new_box_h / img_h

            new_nx1 = new_cx - (new_cw / 2)
            new_nx2 = new_cx + (new_cw / 2)
            new_ny1 = new_cy - (new_ch / 2)
            new_ny2 = new_cy + (new_ch / 2)

            condition = 1
            if new_cw > 0.01 and new_ch > 0.01 and new_cx > 0 and new_cx < 1 and new_cy > 0 and new_cy < 1:
                for p in [new_nx1, new_nx2, new_ny1, new_ny2]:
                    if p > 1 or p < 0:
                        condition = 0
                        break
            else:
                condition = 0

            if condition == 1:
                rotated_objects.append(f"{lbl} {new_cx} {new_cy} {new_cw} {new_ch}\n")

        if len(rotated_objects) > 0:
            cv2.imwrite(im_save_path, rotated_image)
            with open(txt_save_path, "w") as f:
                f.writelines(rotated_objects)
            print("Veri çoğaltma işlemi gerçekleştirildi")
        else:
            print(self.data_name, "Çoğaltma sonucunda görselde obje kalmadığı için çoğaltma işlemi gerçekleştirilemedi")
          
    def slice(self,slice_width:int,slice_height:int,im_save_path:str,txt_save_path:str,cover_objectless_data=False,info=False):
        
        def _get_slice_coordinates(image,slice_width,slice_height):
            height,width,_ = image.shape
            
            tl_slices = (0,slice_height,0,slice_width)
            tr_slices = (0,slice_height,width-slice_width,width)
            bl_slices = (height-slice_height,height,0,slice_width)
            br_slices = (height-slice_height,height,width-slice_width,width)
                        
            return [tl_slices,tr_slices,bl_slices,br_slices]
            
        def _slice_objects(slice_coordinates,objects):
            objs = []
            for y1,y2,x1,x2 in slice_coordinates:
                slice_objs = []
                for obj in objects:
                    new_obj = SpiralObject(obj.label_idx,obj.conf,obj.x1,obj.y1,obj.x2,obj.y2)
                    new_obj.x1,new_obj.y1,new_obj.x2,new_obj.y2 = int(new_obj.x1), int(new_obj.y1),int(new_obj.x2),int(new_obj.y2)

                    if new_obj.x1 > x2 or new_obj.x2 < x1 or new_obj.y1 > y2 or new_obj.y2 < y1:
                        pass
                    else:
                        if new_obj.x1 < x1 :
                            new_obj.x1 = x1

                        if  new_obj.x2 > x2:
                            new_obj.x2 = x2
                        
                        if new_obj.y1 < y1:
                            new_obj.y1 = y1
                        
                        if new_obj.y2 > y2:
                            new_obj.y2 = y2
                        
                        if new_obj.x1 == x1 and new_obj.y1 == y1 and new_obj.x2 == x2 and new_obj.y2 == y2:
                            pass
                        else:
                            if (new_obj.x2-new_obj.x1) * (new_obj.y2-new_obj.y1) > 1000 and (new_obj.x2-new_obj.x1) > 50 and (new_obj.y2-new_obj.y1) > 50:
                                new_obj.x1 -= x1
                                new_obj.x2 -= x1
                                new_obj.y1 -= y1
                                new_obj.y2 -= y1
                                slice_objs.append(new_obj)
                            
                objs.append(slice_objs)
                
            return objs
                                    
        image = cv2.imread(self.image_path)
        objects = self.get_as_absoluate_coordinates(image.shape)

        # Checks
        assert isinstance(image, np.ndarray), TypeError(f"Expected np.ndarray but got {type(image)}")
        height,width,_ = image.shape
        if slice_width < width / 2: warnings.warn("Slice width shorter than half of image width. Could be pixel missings",UserWarning)
        if slice_height < height / 2: warnings.warn("Slice height shorter than half of image height. Could be pixel missings",UserWarning)
        intersection_width = max(0, slice_width * 2 - width)
        intersection_height = max(0, slice_height * 2 - height)
        assert slice_width <= width, f"slice width bigger than image width slice_width:{slice_width} image_width:{width} name:{self.data_name}"
        assert slice_height <= height, f"slice height bigger than image height slice_height:{slice_height} image_height:{height} name:{self.data_name}"
        if info:
            print("İntersection width: ",intersection_width) 
            print("İntersection height: ",intersection_height)
            
            
        slice_coordinates = _get_slice_coordinates(image,slice_width,slice_height)
        
        image_slices = [image[a:b,c:d] for a,b,c,d in slice_coordinates]
        sliced_objects = _slice_objects(slice_coordinates,objects)
        
        topics = ["top_left","top_right","bottom_left","bottom_right"]
        for i, image,objs in zip(range(len(image_slices)),image_slices,sliced_objects):
            if (len(objs) == 0 and cover_objectless_data == True) or len(objs) > 0:
                
                cv2.imwrite(im_save_path + "/" + topics[i] + "_" + self.data_name + ".jpg" ,image)
                f = open(txt_save_path + "/" + topics[i] + "_" + self.data_name +".txt","w")
                for obj in objs:
                    cx = (obj.x1 + obj.x2) / 2 / slice_width
                    cy = (obj.y1 + obj.y2) / 2 / slice_height
                    cw = (obj.x2-obj.x1) / slice_width
                    ch = (obj.y2-obj.y1) / slice_height 
                    f.write(f"{obj.label_idx} {cx} {cy} {cw} {ch}\n")
                f.close()
            