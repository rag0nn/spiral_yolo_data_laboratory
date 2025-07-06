from pathlib import Path
import logging
import cv2
from typing import Optional, Callable
import numpy as np
import shutil
import os
from typing import Tuple

from .enums import Category,FileType,DatasetFolders
from .object import Object
            

class BaseData:
    def __init__(self, path: Path, file_type: FileType):
        self.type = file_type
        self.path = path
        self.cat = self._extract_category()
        
    def __str__(self):
       return  f"{self.type.value} {self.cat.value}"
   
    def _extract_category(self) -> Optional[Category]:
        try:
            return Category(self.path.parts[-2])
        except:
            valid_cats = ", ".join(i.value for i in Category)
            logging.error(f"Data has not got category like: '{valid_cats}'")
            return None
        
    def rename(self, name: str):
        """
        Renames the file (either .jpg or .txt) to the given name, preserving the file extension.
        Updates the internal path to the new file location.
        """
        new_path = self.path.with_stem(f"{name}")
        try:
            # Move the file to the new path (rename)
            shutil.move(str(self.path), str(new_path))
            self.path = new_path
            logging.debug(f"Renamed file to {new_path}")
        except Exception as e:
            logging.error(f"Failed to rename file: {e}")
        

class ImageData(BaseData):
    def __init__(self, path: Path):
        super().__init__(path, FileType.IMAGE)
        
    def __str__(self):
        return  f"{super().__str__()} {self.shape}"
        
    def get_image(self) -> Optional[np.ndarray]:
        """
        Returns the image file as a numpy array.
        """
        return cv2.imread(str(self.path), cv2.IMREAD_UNCHANGED)
    
    def resize(self,newshape):
        newimage = cv2.resize(self.get_image(),newshape)
        cv2.imwrite(self.path,newimage)
        logging.debug(f"Image Resized to {newshape}: {self.path.name}")

    def get_stats(self):
        return {
            "shape" : self.shape,
            "count" : 1
        }
        
    def apply_filter(self,filter_func:Callable[[np.array],np.array]):
        image = self.get_image()
        new_image = filter_func(image)
        cv2.imwrite(self.path,new_image)
        logging.debug(f"Image Filtered: {self.path}")
        
    def slice(self,density_offset=Tuple[int, int],slice_shape=Tuple[int,int]):
        """
        Slices the dataset based on the specified density offset and slice shape.
        Args:
            density_offset width, height(Tuple[int, int]): Density coordinates of objects. It using for most objects included image slice.
            slice_shape (Tuple[int, int]): The (height, width) of the slice to extract.
        """
        orig_h, orig_w, _ = self.shape
        slice_w, slice_h = slice_shape
        center_x, center_y = density_offset
        if slice_w <= orig_w and slice_h <= orig_h:
            x1 = int(center_x - int(slice_w / 2))
            x2 = int(center_x + int(slice_w / 2))
            y1 = int(center_y - int(slice_h / 2))
            y2 = int(center_y + int(slice_h / 2))
        
            if x1 < 0:
                diff = x1
                x1 += abs(diff)
                x2 += abs(diff)
            elif x2 > orig_w:
                diff = x2 - orig_w
                x1 -= abs(diff)
                x2 -= abs(diff)
            if y1 < 0:
                diff = y1
                y1 += abs(diff)
                y2 += abs(diff)
            elif y2 > orig_h:
                diff = y2 - orig_h
                y1 -= abs(diff)
                y2 -= abs(diff)
            
            image = self.get_image()
            slice_image = image[y1:y2,x1:x2]
            cv2.imwrite(self.path,slice_image)
            logging.debug(f"Image sliced: {self.path}")
        else:
            logging.error("Slice shape bigger than original image shape")
        

        
    
    @property
    def shape(self):
        """
        Returns the shape of the image as a tuple. If the image does not have three dimensions,
        adds a singleton channel dimension to ensure the output is always a 3-tuple.

        Returns:
            tuple: The shape of the image in (height, width, channels) format.
        """
        sp = self.get_image().shape
        if len(sp) != 3:
            sp = sp + (1)
        return sp

class AnnotationData(BaseData):
    def __init__(self, path: Path):
        super().__init__(path, FileType.ANNOTATION)
        self.objects, self.errors = self._load_objects()

    def __str__(self):
        return f"{super().__str__()} object_count: {len(self.objects)}"

    def _load_objects(self):
        f = open(self.path, "r")
        lines = f.readlines()
        f.close()

        objects = []
        errors = []
        unique_set = set()
        for i, line in enumerate(lines):
            try:
                obj = Object.fromStringXYWHF(line)
                # Uniqueness key: (label, x1, y1, x2, y2)
                key = (obj.label, obj.x1, obj.y1, obj.x2, obj.y2)
                if key not in unique_set:
                    unique_set.add(key)
                    objects.append(obj)
                else:
                    logging.warning(f"Duplicate object detected: {self.path} line: {i} -> {line.strip()}")
            except Exception:
                logging.error(f"Object Error Occured: {self.path} line: {i} -> {line}")
                errors.append(f"{self.path},{i},[{line[:-2]}]")

        return objects, errors

    def get_stats(self):
        results = {}
        for obj in self.objects:
            obj.label
            if obj.label in results.keys():
                results[obj.label] += 1
            else:
                results[obj.label] = 1
        return {k: results[k] for k in sorted(results.keys())}
    
    def convert_objects(self,targets_dict:dict):
        """
        Converts the labels of objects in the current instance using a provided mapping dictionary.
        For each object in self.objects, retrieves its label and bounding box information,
        attempts to map the label using targets_dict, and writes the updated labels and coordinates
        back to the file at self.path in the format: "<label> <center_x> <center_y> <width> <height>".
        If a label is not found in targets_dict, it remains unchanged and a log message is generated.
        Args:
            targets_dict (dict): A dictionary mapping original label integers to new label values.
            etc: {0:1,1:1,3:4} values must be int
        Side Effects:
            Overwrites the file at self.path with the new label data.
            Logs info messages for labels not found in targets_dict.
        """
        new_labels = []
        for obj in self.objects:
            obj:Object
            text = obj.get_XYWHF_string()
            lbl,c_x,c_y,w,h = text.split(" ")
            new_label = None
            try:
                new_label = targets_dict[int(lbl)]
            except:
                new_label = lbl
                logging.info(f"label convertion target dict has not this element: {lbl}, it will not change")
            new_row = f"{str(new_label)} {c_x} {c_y} {w} {h}\n"
            new_labels.append(new_row)
            
        f = open(self.path,"w")
        f.writelines(new_labels)
        f.close()
        
    def get_objects_density_offset(self)->Tuple[int,int]:
        """
        Returns:
            x,y (int, int): Coordinates of Density offset of objects on image. Density offset is mean of coordinates in the image 
        """
        x = 0
        y = 0
        if len(self.objects) != 0:

            for obj in self.objects:
                obj:Object
                o_x,o_y = obj.center
                x += o_x
                y += o_y

            x /= len(self.objects)
            y /= len(self.objects)
        else:
            x = 0
            y = 0    
        return x,y        

class Data:
    def __init__(self,ds_path:Path,cat:Category,data_stem:str):        
        image_path = Path(ds_path,"detect",DatasetFolders.IMAGES.value[0],cat.value,data_stem).with_suffix('.jpg')
        txt_path = Path(ds_path,"detect",DatasetFolders.LABELS.value[0],cat.value,data_stem).with_suffix('.txt')
        
        self.image_data = ImageData(image_path) if image_path.exists() else None
        self.annotation_data = AnnotationData(txt_path) if txt_path.exists() else None
        self.conjugated = self.image_data is not None and self.annotation_data is not None
        self.category = cat
        self.name = Path(image_path).stem
        missing = []
        if self.image_data is None:
            missing.append(FileType.IMAGE.value)
        if self.annotation_data is None:
            missing.append(FileType.ANNOTATION.value)
        if missing:
            logging.error(f"{ds_path.name} {cat} {data_stem} missing data: {', '.join(missing)}")
            
    def __str__(self):
        return f"{self.image_data} {self.annotation_data}"
    
    def change_category(self, target_category:Category):
        # image 
        ip_parts = list(Path(self.image_data.path).parts)
        ip_parts[-2] = f"{target_category.value}"  
        target_image_path = Path(*ip_parts)
        shutil.move(self.image_data.path,target_image_path)
        #annotations
        ap_parts = list(Path(self.annotation_data.path).parts)
        ap_parts[-2] = f"{target_category.value}"  
        target_annotation_path = Path(*ap_parts)
        shutil.move(self.annotation_data.path,target_annotation_path)
        
    def copy(self,image_path,annotation_path):
        # image
        new_path_im = Path(image_path,self.image_data.path.name)
        shutil.copy(str(self.image_data.path), new_path_im)
        
        # annotation
        new_path_anno = Path(annotation_path,self.annotation_data.path.name)
        shutil.copy(str(self.annotation_data.path),new_path_anno)
        
    def rename(self,name):
        self.annotation_data.rename(name)
        self.image_data.rename(name)
    
    def remove(self):
        os.remove(self.image_data.path)
        logging.info(f"Data:{self.name}, Image Gile Removed")
        
        os.remove(self.annotation_data.path)
        logging.info(f"Data:{self.name}, Annotation File Removed")
        
    def slice(self,slice_shape:Tuple[int,int]):
        center_x, center_y = self.annotation_data.get_objects_density_offset()
        h,w,_ = self.image_data.shape
        if center_x >= 0 and 1 >= center_x:
            center_x = int(center_x * w)
        if center_y >= 0 and 1 >= center_y:
            center_y = int(center_y * h)
        self.image_data.slice((center_x,center_y),slice_shape)