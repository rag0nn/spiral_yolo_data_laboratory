import os
import cv2
from tqdm import tqdm
from spiral.spiral_lib.object_detection.object import Object
from spiral.spiral_lib.postprocessing.monitor_helper import MonitorHelper

# an onnx file downloaded from the url displayed in (your doc)[https://docs.opencv.org/4.7.0/d8/d69/classcv_1_1TrackerNano.html]
BACKBONE_PATH = os.path.join(os.path.dirname(__file__), "nanotrack_backbone_sim.onnx")
NECKHEAD_PATH = os.path.join(os.path.dirname(__file__), "nanotrack_head_sim.onnx")
        
class TagTracker:
    
    def __init__(self,src_path,dst_path):
        self.src_path = src_path
        self.dst_folder_path = dst_path
        self.im_names = os.listdir(src_path)  
        self.trackers = []
        self.results = {}
        self.counter = 0
        self.label = 0 
        self.mon_helper = MonitorHelper()
        self.mon_Shape = (1200,750)
        self.mon_obj = Object(1,1,self.mon_Shape[0]-1,self.mon_Shape[1]-1,1.0,0,False,self.mon_Shape[0],self.mon_Shape[1])
        
        print()
        print("q"," ---> ","OUT")
        print("a"," ---> ","previous")
        print("d"," ---> ","next")
        print("w"," ---> ","select bbox")
        print("c"," ---> ","change label")
        print("z"," ---> ","save and quit")
        print("r"," ---> ","remove current results and trackers on index")
        print()
        
        self.show_frame(False)
        
    def get_tracker(self,frame,bbox):
        params = cv2.TrackerNano_Params()
        params.backbone = BACKBONE_PATH
        params.neckhead = NECKHEAD_PATH
        tracker = cv2.TrackerNano_create(params)
        tracker.init(frame, bbox)
        return tracker
        
    def add_tracker(self,frame,bbox,frame_index):
        tracker = self.get_tracker(frame,bbox)
        self.trackers.append((tracker,self.label))
        
        x, y, w, h = [int(v) for v in bbox]
        x1,y1,x2,y2 = x,y,x+w,y+h
        height,width,_ = frame.shape
        self.insert_object(x1,y1,x2,y2,len(self.trackers)-1,width,height,self.label,frame_index)
        
    def insert_object(self,x1,y1,x2,y2,id,im_w,im_h,label,frame_index):
        o = Object(x1,y1,x2,y2,1.0,label,False,image_width=im_w,image_height=im_h,id=id)
        if frame_index not in list(self.results.keys()):
            self.results[frame_index] = [o]
        else:   
            self.results[frame_index].append(o)  
    
    def update_trackers(self,frame,frame_index):
        height,width,_ = frame.shape
        will_delete = []
        for trac_i,(tracker, track_lbl) in enumerate(self.trackers):
            success, bbox = tracker.update(frame)
            if success:
                x, y, w, h = [int(v) for v in bbox]
                x1,y1,x2,y2 = x,y,x+w,y+h
                
                if x1 < 0 or y1 < 0 or x2 > width or y2 > height:
                    will_delete.append((tracker,track_lbl))
                else:
                    self.insert_object(x1,y1,x2,y2,trac_i,width,height,track_lbl,frame_index) 
            else:
                will_delete.append((tracker,track_lbl))

                
        for trc in will_delete[::-1]:
            print(self.trackers)
            print(trc)
            print("Tracker Deleted")
            self.trackers.remove(trc)
            
    def show_frame(self,forward:bool):

        
        image = cv2.imread(self.src_path + "/" + self.im_names[self.counter])
        image = cv2.resize(image,self.mon_Shape)
        if forward:
            self.update_trackers(image,self.counter)
            
        if self.counter in self.results.keys():  
            print(self.counter,"-->",self.results[self.counter])
        else:
            print(self.counter,"--> Empty")
            
        if self.counter in list(self.results.keys()):
            objs = self.results[self.counter]
            image = self.mon_helper.paint_objects(image,objs)
            
        
        cv2.imshow("OUT",image)
        key = cv2.waitKey(0)
        if key == ord("q"):
            pass
        elif key == ord("a"):
            self.counter -=1
            self.show_frame(False)
        elif key == ord("d"):
            self.counter +=1
            self.show_frame(True)
        elif key == ord("w"):
            bbox = cv2.selectROI("OUT", image, True)
            self.add_tracker(image,bbox,self.counter)
            self.counter += 1
            self.show_frame(True)
        elif key == ord("c"):
            self.label = int(input(f"current: {self.label}, new: "))
            self.show_frame(False)
        elif key == ord("z"):
            self.save_results()
        elif key == ord("r"):
            self.trackers.clear()
            if self.counter in self.results.keys():   
                self.results[self.counter].clear()
            self.show_frame(False)

            
    def save_results(self):
        for i,name in tqdm(enumerate(self.im_names),"--> "):
            
            f = open(self.dst_folder_path + "/" +  name.split(".")[0] + ".txt","w")
            if i in self.results.keys():
                for obj in self.results[i]:
                    obj:Object
                    obj.to_normalized()
                    obj_text = Object.XYXY_to_XYWH(f"{obj.label} {obj.x1} {obj.y1} {obj.x2} {obj.y2}",'f')
                    f.write(obj_text +"\n")
            f.close()
            
            
src_pat = r"C:\Users\asus\Desktop\TEKNOFEST_DATA\ETIKETSIZ\T22_04_1_1" 
dst_pat = r"C:\Users\asus\Desktop\outputs" 
TagTracker(src_pat,dst_pat)