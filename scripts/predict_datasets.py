from ultralytics import YOLO
import os
import cv2
from tqdm import tqdm


def process(src_path,dst_path,pipe,new_ds_name,video=False):
    name = new_ds_name + "_pred"
    
    out_images_path = dst_path + "/" + name + "/images"
    out_labels_path = dst_path + "/" + name + "/labels"
    
    os.mkdir(dst_path + "/" + name)
    os.mkdir(out_labels_path)
    os.mkdir(out_images_path)
    
    def _write_objects(name,boxes,width,height):
        with open(out_labels_path + "/" + name + ".txt", "w") as f:
            for cls, box in zip(boxes.cls, boxes.xywh):
                cx, cy, w, h = box.tolist()

                # Normalizasyon: (0-1) arası değerler
                cx /= width
                cy /= height
                w /= width
                h /= height

                # Yaz: label_id cx cy w h
                line = f"{int(cls)} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}\n"
                f.write(line)
    def _write_frame(name,frame):
        pth = out_images_path + "/" + name
        cv2.imwrite(pth,frame)
            
    if video:
        cap = cv2.VideoCapture(src_path)
        counter = 0
        while tqdm(cap.isOpened()):
            ret, image = cap.read()
            if not ret:
                break  # Video bitti
            image_name = f"frame_{counter}.jpg"
            results = pipe.predict(image)
            boxes = results[0].boxes 
            height, width = image.shape[:2]
            _write_objects(image_name.split(".")[-2],boxes,width,height)
            _write_frame(image_name,image) 
            
            counter += 1
        cap.release()
    else:
        image_names = os.listdir(src_path)
        for image_name in tqdm(image_names):
            image_path = src_path + "/" + image_name
            image = cv2.imread(image_path)
            results = pipe.predict(image,imgsz=1920)
            boxes = results[0].boxes 
            height, width = image.shape[:2]
            _write_objects(image_name.split(".")[-2],boxes,width,height)
            _write_frame(image_name,image)
            
            
def apply():
    names_ = ['T22_04_2', 'T22_O1_1_1', 'T22_O1_1_2', 'T22_O1_2', 'T22_O3_1', 'T22_O3_2', 'T22_O3_3']
    
    for na_ in names_:
        new_ds_name = na_
        model_path = "C:/Users/asus/Codes/envs/spiral-with-torch-gpu/Lib/site-packages/spiral/spiral_lib/object_detection/models/yolov8m_spiral_vision_v10.pt"
        src_path = f"C:/Users/asus/Desktop/TEKNOFEST_DATA/ETIKETSIZ/{new_ds_name}" # video_path or image_folder_path
        dst_path = "C:/Users/asus/Desktop/output" # output folder path

        pipe = YOLO(model_path)
        process(src_path,dst_path,pipe,new_ds_name)
        
apply()