from ..object import Object
from ..utils import get_conf
import numpy as np
import cv2
import logging
import copy
     
from ..data import Data

class MonitorHelper:
    
    def __init__(self):
        self.config = get_conf()
        self.monitor_width,self.monitor_height = self.config.review_monitor.monitor_width, self.config.review_monitor.monitor_height
        self.background_opacity = self.config.review_monitor.graphics.opacity
        self.background_color = self.config.review_monitor.graphics.background_color
        self.foreground_color = self.config.review_monitor.graphics.foreground_color
        
    def _paint_weighted_color(self,image,x1,y1,x2,y2,color=[255,255,255],scale=0.7):
        """
        Adds semi opacity on given coordinates to image
        return:
            image
        """
        try:
            roi = image[y1:y2,x1:x2]
        except Exception as e:
            raise f"Error occured when trieng weigted color {e}"

        color_filter = np.resize(np.array(color,dtype=np.uint8),roi.shape)      
        colored = cv2.addWeighted(roi,scale,color_filter,0.3,0.0)

        image[y1:y2,x1:x2] = colored
        return image

    def _get_label_color(self, idx):
        default_colors = self.config.review_monitor.label_color_rgb
        if idx in list(range(4)):
            return default_colors[idx]
        else:
            # Generate a distinct random color for other indices
            rng = np.random.default_rng(idx)  # Seed with idx for consistency
            color = rng.integers(0, 256, size=3)
            return tuple(int(c) for c in color)
        
    def _get_label_text(self, texts, idx):
        if idx < len(texts):
            return texts[idx]
        else:
            return "UNKWN"
        
        
    def paint_objects(self,image:np.array , data:Data, label_texts:list):
        """
        Paints given objects
        inputs:
            image: np.array
            objects: list of Spiral Objects
        """
    
        objects = copy.deepcopy(data.annotation_data.objects)
        image_height, image_width, c = image.shape
        
        cfg = self.config.review_monitor.object_monitoring
        if len(objects) > 0:
            for obj in objects:
                if obj.normalized:
                    obj.to_absolute(image_width,image_height)
                
                id_text =   ""
                label_color = self._get_label_color(obj.label)
                label_text = self._get_label_text(label_texts,obj.label)
                
                text_x,text_y = obj.x1+ cfg.text_x, obj.y1+cfg.text_y
                text_box_x1,text_box_y1 = obj.x1 + cfg.textbox_x1, obj.y1 + cfg.textbox_y1
                if obj.x2 - obj.x1 < cfg.textbox_x2_if_low:
                    text_box_x2,text_box_y2 = obj.x1 + cfg.textbox_x2_if_low, obj.y1 + cfg.textbox_y2
                else:
                    text_box_x2,text_box_y2 = obj.x2 + cfg.textbox_x2_if_normal, obj.y1 + cfg.textbox_y2
                
                # object
                image = self._paint_weighted_color(image,obj.x1,obj.y1,obj.x2,obj.y2,label_color,cfg.objbackbox_opacity)
                cv2.rectangle(image,(obj.x1,obj.y1),(obj.x2,obj.y2),(255,255,255),cfg.objbox_thickness)
                
                # text box
                cv2.rectangle(image,(text_box_x1,text_box_y1),(text_box_x2,text_box_y2),(255,255,255),-1)
                cv2.putText(image,f"{id_text}{label_text} ",(text_x,text_y),cv2.FONT_HERSHEY_DUPLEX,cfg.text_scale,cfg.text_color)
            logging.debug("Objects Painted")
        return image
        
    def paint_info(self,image, data:Data, index):
        menu_x, menu_y = self.config.review_monitor.info.menu_x, self.config.review_monitor.info.menu_y
        shift_x, shift_y = self.config.review_monitor.info.shift_x,self.config.review_monitor.info.shift_y
        cfg = self.config.review_monitor.object_monitoring
        shape = data.image_data.shape
        cv2.putText(image, f"{index}",(menu_x, menu_y),cv2.FONT_HERSHEY_DUPLEX,cfg.text_scale,self.config.review_monitor.info.text_color)
        menu_y += shift_y
        menu_x += shift_x
        cv2.putText(image, f"{data.name}",(menu_x, menu_y),cv2.FONT_HERSHEY_DUPLEX,cfg.text_scale,self.config.review_monitor.info.text_color)
        menu_y += shift_y
        menu_x += shift_x
        cv2.putText(image,f"{str(shape)}",(menu_x, menu_y),cv2.FONT_HERSHEY_DUPLEX,cfg.text_scale,self.config.review_monitor.info.text_color)
        menu_y += shift_y
        menu_x += shift_x
        for idx, (key, value) in enumerate(data.annotation_data.get_stats().items()):
            cv2.putText(image,f"{str(key)} : {str(value)}",(menu_x + shift_x*idx, menu_y +shift_y*idx),cv2.FONT_HERSHEY_DUPLEX,cfg.text_scale,self.config.review_monitor.info.text_color)
        return image