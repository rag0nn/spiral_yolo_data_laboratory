import os
import cv2
from tqdm import tqdm
from spiral.spiral_lib.object_detection.object import Object
from spiral.spiral_lib.object_detection.pipeline import ObjectDetectionPipeline
from spiral.spiral_lib.postprocessing.monitor_helper import MonitorHelper
from enum import Enum
from copy import deepcopy
import logging

class ProcessEnum(Enum):
    NEXT =  "d"
    PREVIOUS = "a"
    DETECTION = "s"
    TRACK_OBJECTS = "w"
    QUIT = "q"
    SAVE = "o"
    CLEAN_OBJS = "r"
    ADD_OBJ = "x"
    CHANGE_LABEL = "v"
    ADD_IGNOREAREA = "m"
    TRACK_IGNORED= "n"
    AUTO_PRED =  "u"
    ADD_FOCUSAREA = "h"
    
    @staticmethod
    def info():
        logging.info("CONTROL KEYS")
        for item in ProcessEnum:
            logging.info(f"{item.name}: '{item.value}'")
            
    @staticmethod
    def paint_info(frame):
        y0 = 20  # başlangıç yüksekliği
        dy = 25  # satırlar arası mesafe
        x_offset = 10  # sağdan boşluk
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        color = (0, 255, 0)  # yeşil
        thickness = 1

        h, w, _ = frame.shape
        for i, item in enumerate(ProcessEnum):
            text = f"{item.name}: '{item.value}'"
            y = y0 + i * dy
            text_size, _ = cv2.getTextSize(text, font, font_scale, thickness)
            text_width = text_size[0]
            x = w - text_width - x_offset  # sağdan hizalama
            cv2.putText(frame, text, (x, y), font, font_scale, color, thickness)
        return frame
    
class ImageData:
    def __init__(self,name,folder_path):
        self.name = name
        self.folder_path = folder_path
    
    @property
    def get_just_name(self):
        n = self.name.split(".")[0]
        return f"{n}"
    
    @property
    def get_image(self):
        return cv2.imread(self.get_path)
    
    @property
    def get_path(self):
        return f"{self.folder_path}/{self.name}"

class Track:
    def __init__(self,track_backbone_path, track_neckhead_path):
        self.track_backbone_path = track_backbone_path
        self.track_neckhead_path = track_neckhead_path
        
    def _get_tracker(self,frame, bbox):
        params = cv2.TrackerNano_Params()
        params.backbone = self.track_backbone_path
        params.neckhead = self.track_neckhead_path
        tracker = cv2.TrackerNano_create(params)
        tracker.init(frame, bbox)
        return tracker
    
    def track_areas(self,prev_image,current_image,data_list:list,prev_index:int,current_index:int):
        """
        data_list: area list (includes all frame objects)
        """
        
        # previous data
        prev_ignores = data_list[prev_index]
        frame_height,frame_width,_ = prev_image.shape
        
        # tracker init
        trackers = []
        for obj in prev_ignores:
            obj:Object
            c_obj = deepcopy(obj)
            c_obj.to_absolute(frame_width,frame_height)
            
            x,y,w,h = int(c_obj.x1),int( c_obj.y1), int(c_obj.x2 -c_obj.x1), int(c_obj.y2 - c_obj.y1)
            tracker = self._get_tracker(prev_image,[x,y,w,h])
            trackers.append((tracker,c_obj.label))
            
        # current data
        for tracker, lbl in trackers:
            success, bbox = tracker.update(current_image)
        
            if success:
                x, y, w, h = [int(v) for v in bbox]
                x1,y1,x2,y2 = x,y,x+w,y+h
                
                if x1 <= 0 or y1 <= 0 or x2 >= frame_width or y2 >= frame_height:
                    logging.warning("Tracking passed, box intersects with borders")
                    continue
                o = Object.fromStringXYXYI(f"{lbl} {x1} {y1} {x2} {y2}",frame_width,frame_height)
                o.to_normalized()
                data_list[current_index].append(o)
                  
class TagTracker:
    
    def __init__(self,images_path,dst_path,track_backbone_path,track_neckhead_path):
        # const
        self.track_backbone_path = track_backbone_path
        self.track_neckhead_path = track_neckhead_path
        self.images_path = images_path
        self.image_datas= list(ImageData(name, images_path) for name in tqdm(os.listdir(images_path)))
        self.image_datas: list[ImageData]
        self.win_name = "OUT"
        self.win_width, self.win_height = 1200,750
        self.dst_path = dst_path
        self.data_size = len(self.image_datas)
        self.auto_pred_coverage = 10
        self.tracker = Track(self.track_backbone_path,self.track_neckhead_path)
        # processers
        self.mon_helper = MonitorHelper()
        self.model = ObjectDetectionPipeline()

        # params
        self.index = 0
        self.index_prev = None
        self.objects = dict(list( (i,[]) for i in range(len(self.image_datas))))
        self.ignores = dict(list( (i,[]) for i in range(len(self.image_datas))))
        self.focuses = dict(list( (i,[]) for i in range(len(self.image_datas))))
        self.chosen_label = 0
        
        # start
        ProcessEnum.info()
        self.session()

    def detect_objects(self):
        objs = self.model.predict(self.image_datas[self.index].get_image)
        objs:list[Object]
        for obj in objs:
            obj.to_normalized()
            self.objects[self.index].append(obj)
            
    def remove_current_objs(self):
        self.objects[self.index].clear()
        self.ignores[self.index].clear()
        
    def track_objects(self):

        def _get_tracker(frame, bbox):
            params = cv2.TrackerNano_Params()
            params.backbone = self.track_backbone_path
            params.neckhead = self.track_neckhead_path  # HATA BURADAYDI
            tracker = cv2.TrackerNano_create(params)
            tracker.init(frame, bbox)
            return tracker

        # previous data
        prev_im = self.image_datas[self.index_prev].get_image
        prev_objs = self.objects[self.index_prev]
        frame_height,frame_width,_ = prev_im.shape
        
        # tracker init
        trackers = []
        for obj in prev_objs:
            obj:Object
            c_obj = deepcopy(obj)
            c_obj.to_absolute(frame_width,frame_height)
            
            x,y,w,h = int(c_obj.x1),int( c_obj.y1), int(c_obj.x2 -c_obj.x1), int(c_obj.y2 - c_obj.y1)
            tracker = _get_tracker(prev_im,[x,y,w,h])
            trackers.append((tracker,c_obj.label))
            
        # current data
        im = self.image_datas[self.index].get_image
        for tracker, lbl in trackers:
            success, bbox = tracker.update(im)
            if success:
                x, y, w, h = [int(v) for v in bbox]
                x1,y1,x2,y2 = x,y,x+w,y+h
                if x1 <= 0 or y1 <= 0 or x2 >= frame_width or y2 >= frame_height:
                    logging.warning("Tracking passed, box intersects with borders")
                    continue
                o = Object.fromStringXYXYI(f"{lbl} {x1} {y1} {x2} {y2}",frame_width,frame_height)
                o.to_normalized()
                self.objects[self.index].append(o)

    def add_obj(self):
        o = self.get_area()
        self.objects[self.index].append(o)
        
    def add_focus_area(self):
        o = self.get_area(label=4)
        self.focuses[self.index].append(o)
        
    def add_ignore_area(self):
        o = self.get_area(label=4)
        self.ignores[self.index].append(o)
        
    def get_area(self,label=None):
        im = self.image_datas[self.index].get_image
        im = cv2.resize(im,(self.win_width,self.win_height))
        box = cv2.selectROI(self.win_name,im,printNotice=True)   
        height,width,_ = im.shape
        x,y,w,h = box        
        x1,y1,x2,y2 = x,y,x+w,y+h
        o = Object.fromStringXYXYI(f"{label or self.chosen_label} {x1} {y1} {x2} {y2}",width,height)
        o.to_normalized()
        return o
         
    def change_chosen_label(self):
        self.chosen_label = int(input("Chosen Label: "))
        
    def track_ignored_areas(self):
        def _get_tracker(frame, bbox):
            params = cv2.TrackerNano_Params()
            params.backbone = self.track_backbone_path
            params.neckhead = self.track_neckhead_path  # HATA BURADAYDI
            tracker = cv2.TrackerNano_create(params)
            tracker.init(frame, bbox)
            return tracker

        # previous data
        prev_im = self.image_datas[self.index_prev].get_image
        prev_ignores = self.ignores[self.index_prev]
        frame_height,frame_width,_ = prev_im.shape
        
        # tracker init
        trackers = []
        for obj in prev_ignores:
            obj:Object
            c_obj = deepcopy(obj)
            c_obj.to_absolute(frame_width,frame_height)
            
            x,y,w,h = int(c_obj.x1),int( c_obj.y1), int(c_obj.x2 -c_obj.x1), int(c_obj.y2 - c_obj.y1)
            tracker = _get_tracker(prev_im,[x,y,w,h])
            trackers.append((tracker,c_obj.label))
            
        # current data
        im = self.image_datas[self.index].get_image
        for tracker, lbl in trackers:
            success, bbox = tracker.update(im)
        
            if success:
                x, y, w, h = [int(v) for v in bbox]
                x1,y1,x2,y2 = x,y,x+w,y+h
                
                if x1 <= 0 or y1 <= 0 or x2 >= frame_width or y2 >= frame_height:
                    logging.warning("Tracking passed, box intersects with borders")
                    continue
                o = Object.fromStringXYXYI(f"{lbl} {x1} {y1} {x2} {y2}",frame_width,frame_height)
                o.to_normalized()
                self.ignores[self.index].append(o)
    
    def save_outputs(self):
        for i,im_data in tqdm(enumerate(self.image_datas)):
            txt_name = im_data.get_just_name + ".txt"
            abs_path = self.dst_path + "/" + txt_name
            f = open(abs_path,"w")
            objs = self.objects[i]
            for obj in objs:
                obj:Object
                out_normalized_text = Object.XYXY_to_XYWH(f"{obj.label} {obj.x1} {obj.y1} {obj.x2} {obj.y2}","f") + "\n"
                f.write(out_normalized_text)
            f.close()
    
    def index_increase(self):
        self.index = (self.index + 1) % self.data_size
        self.index_prev = self.index - 1
        
    def index_decrease(self):
        self.index = (self.index - 1 + self.data_size) % self.data_size
        self.index_prev = self.index - 1
        
    def show_frame(self,wait=0):
        # monitor data
        frame = self.image_datas[self.index].get_image
        objs = self.objects[self.index]
        ignores = self.ignores[self.index]
        focuses = self.focuses[self.index]
        frame = self.mon_helper.paint_objects(frame,objs)
        frame = self.mon_helper.paint_objects(frame,ignores)
        frame = self.mon_helper.paint_objects(frame,focuses)
        
        # monitoring
        frame = cv2.resize(frame,(self.win_width,self.win_height))
        frame = ProcessEnum.paint_info(frame)
        cv2.imshow(self.win_name,(frame))
        cv2.resizeWindow(self.win_name,self.win_width,self.win_height)
        
        if wait == 0:
            # process choises
            key = cv2.waitKey(0)
            char = chr(key)
            for action in ProcessEnum:
                if action.value == char:
                    return action
        else:
            cv2.waitKey(wait)
            return None
        return None
    
    def track_focus_areas(self):
        self.tracker.track_areas(
            self.image_datas[self.index_prev].get_image,
            self.image_datas[self.index].get_image,
            self.focuses,
            self.index_prev,
            self.index)
        
    def apply_focus(self):
        #TODO eğer önceki frame'de obje varsa track olarak al ve ekle
        #TODO eğer yoksa object detection modelle tahmin et ve ekle
        pass
    
    def clean_objects_in_ignore_areas(self):
        # cleaning via ignore areas
        for area in self.ignores[self.index]:
            area:Object
            for obj in self.objects[self.index][::-1]: 
                if area.intersects(obj):
                    self.objects[self.index].remove(obj)       
                    
    def session(self):
        while True:
            self.clean_objects_in_ignore_areas()
            
            # step
            key = self.show_frame()
            if key == ProcessEnum.NEXT:
                self.index_increase()
            elif key == ProcessEnum.PREVIOUS:
                self.index_decrease()
            elif key == ProcessEnum.TRACK_OBJECTS:
                self.track_objects()
            elif key == ProcessEnum.DETECTION:
                self.detect_objects()
            elif key == ProcessEnum.CLEAN_OBJS:
                self.remove_current_objs()
            elif key == ProcessEnum.ADD_OBJ:
                self.add_obj()
            elif key == ProcessEnum.CHANGE_LABEL:
                self.change_chosen_label()
            elif key == ProcessEnum.TRACK_IGNORED:
                self.track_ignored_areas()
            elif key == ProcessEnum.ADD_FOCUSAREA:
                self.add_focus_area()
            elif key == ProcessEnum.ADD_IGNOREAREA:
                self.add_ignore_area()
            elif key == ProcessEnum.AUTO_PRED:
                self.auto_prediction()
            elif key == ProcessEnum.QUIT:
                cv2.destroyWindow(self.win_name)
                break
            elif key == ProcessEnum.SAVE:
                cv2.destroyWindow(self.win_name)
                self.save_outputs()
                break
            else:
                continue
            
    def auto_prediction(self):
        self.index_increase()

        for i in tqdm(range(self.auto_pred_coverage),desc="Auto Prediction process... "):
            # remove old object and ignore areas
            if self.objects[self.index]:
                self.objects[self.index].clear()
            if self.ignores[self.index]:
                self.ignores[self.index].clear()
                
            self.detect_objects()
            if not self.objects[self.index]:
                self.track_objects()
            self.track_ignored_areas()
            self.track_focus_areas()
            self.clean_objects_in_ignore_areas()
            
            self.show_frame(wait=30)
            self.index_increase()
            
        for i in range(self.auto_pred_coverage):
            self.index_decrease()
        
        
        
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run TagTracker tool.")
    parser.add_argument("--src", required=True, help="Path to input image frames")
    parser.add_argument("--dst", required=True, help="Path to save results")
    parser.add_argument("--backbone", default=os.path.join(os.path.dirname(__file__), "nanotrack_backbone_sim.onnx"),
                        help="(Optional) Path to tracker backbone .onnx file")
    parser.add_argument("--neckhead", default=os.path.join(os.path.dirname(__file__), "nanotrack_head_sim.onnx"),
                        help="(Optional) Path to tracker neckhead .onnx file")
    
    args = parser.parse_args()

    TagTracker(args.src, args.dst, args.backbone, args.neckhead)
    
def track_ignored_areas(self,data:list):
    """
    data: self.objects or self.ignores or self.focuces
    """
    def _get_tracker(frame, bbox):
        params = cv2.TrackerNano_Params()
        params.backbone = self.track_backbone_path
        params.neckhead = self.track_neckhead_path  # HATA BURADAYDI
        tracker = cv2.TrackerNano_create(params)
        tracker.init(frame, bbox)
        return tracker

    # previous data
    prev_im = self.image_datas[self.index_prev].get_image
    prev_ignores = self.data[self.index_prev]
    frame_height,frame_width,_ = prev_im.shape
    
    # tracker init
    trackers = []
    for obj in prev_ignores:
        obj:Object
        c_obj = deepcopy(obj)
        c_obj.to_absolute(frame_width,frame_height)
        
        x,y,w,h = int(c_obj.x1),int( c_obj.y1), int(c_obj.x2 -c_obj.x1), int(c_obj.y2 - c_obj.y1)
        tracker = _get_tracker(prev_im,[x,y,w,h])
        trackers.append((tracker,c_obj.label))
        
    # current data
    im = self.image_datas[self.index].get_image
    for tracker, lbl in trackers:
        success, bbox = tracker.update(im)
    
        if success:
            x, y, w, h = [int(v) for v in bbox]
            x1,y1,x2,y2 = x,y,x+w,y+h
            
            if x1 <= 0 or y1 <= 0 or x2 >= frame_width or y2 >= frame_height:
                logging.warning("Tracking passed, box intersects with borders")
                continue
            o = Object.fromStringXYXYI(f"{lbl} {x1} {y1} {x2} {y2}",frame_width,frame_height)
            o.to_normalized()
            self.ignores[self.index].append(o)