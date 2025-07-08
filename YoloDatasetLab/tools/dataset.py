from pathlib import Path
from omegaconf import OmegaConf
import logging
import numpy as np
from glob import glob
from tqdm import tqdm
import os 
import shutil
from typing import Union, Callable, Tuple
import cv2

from .data import Data
from .reports import *
from .enums import Category,DatasetFolders
from .utils import datetime_id, get_conf
from .object import Object


class Dataset:
    def __init__(self,path):
        self.path = path
        self.name = Path(path).stem
        self.images_path_dict = self._get_data_paths(DatasetFolders.IMAGES)
        self.annotations_path_dict = self._get_data_paths(DatasetFolders.LABELS)
        matches, unmatched_images, unmatched_annotations=  self._data_conjugations()
        self.matches = matches
        self.unmatched_images = unmatched_images
        self.unmatched_annotations = unmatched_annotations
        
    def __str__(self):
        return f"{Path(self.path).stem} Dataset" 
        
    def _get_data_paths(self,folder_type:DatasetFolders):
        result_dict = {}
        for cat in Category:
            result_dict.update({
                cat: glob(os.path.join(Path(self.path,"detect",folder_type.value[0],cat.value),folder_type.value[1]))
            })
        return result_dict

    def _data_conjugations(self):
        matches = {}
        unmatched_images = {}
        unmatched_annotations = {}
        
        for cat in Category:
            matches_ = set()
            unmatched_ims = set()
            unmatched_annos = set()
            
            image_paths = self.images_path_dict[cat]
            annotation_paths = self.annotations_path_dict[cat]    
            
            image_names = list( Path(path).stem for path in image_paths)
            annotation_names = list(Path(path).stem for path in annotation_paths)
            
            for image_name in tqdm(image_names,desc=f"{cat.value} image conjugations checks..."):
                if image_name not in annotation_names:
                    unmatched_ims.add(image_name)
                    logging.info(f"Unmatched Image data: {image_name}")
                else:
                    matches_.add(image_name)
                    
            for anno_name in tqdm(annotation_names,f"{cat.value} annotation conjugations checks..."):
                if anno_name not in image_names:
                    unmatched_annos.add(anno_name)
                    logging.info(f"Unmatched Annotation data: {anno_name}")
                else:
                    matches_.add(anno_name)
                    
            matches[cat] = sorted(list(matches_))
            unmatched_images[cat] = unmatched_ims
            unmatched_annotations[cat] = unmatched_annos
            logging.info(f" {cat.value} conjugations: {len(matches_)} unmatched_images: {len(unmatched_ims)} unmatched_annotations: {len(unmatched_annos)}")
                    
        return matches,unmatched_images,unmatched_annotations
    
    def check_object_errors(self):
        errors = []
        for cat in Category:
            datas = self.get_data(cat)
            for data in datas:
                for err in data.annotation_data.errors:
                    errors.append(str(err) + "\n") 
                
        if errors:
            path = Path(self.path,"output","object_errors.txt")
            f = open(path,"w")
            f.writelines(errors)
            f.close()
            logging.info(f"Object Errors Writed tos {path}")
        
        return errors
    
    def fix_object_errors(self):
        errors_path = Path(self.path,"output","object_errors.txt")
        if os.path.exists(errors_path):
            f = open(errors_path,"r")
            lines = f.readlines()
            lines.reverse()
            f.close()
            for line in tqdm(lines):
                pth, idx, labels_line = line.split(",")
                print(pth)
                with open(pth, "r") as f:
                    lines = f.readlines()

                del lines[int(idx)]
                
                with open(pth, "w") as f:
                    f.writelines(lines)
                    
                logging.debug(f"Writed {pth}")
            return True
        else:
            logging.info(f"Dataset hasn't got any object errors")
            return False
            

    def get_data(self,category:Category,f_index:Union[None,int]=None,l_index:Union[None,int]=None,random=False)->list[Data]:
        assert isinstance(category,Category) , "Category must be element of category enum"
        
        datas = []
        names =self.matches[category]
        if random:
            np.random.shuffle(names)
        
        for name in names[f_index:l_index]:
            datas.append(Data(self.path,category,name))
        return datas
    
    def get_report(self,anno_stats=True,image_stats=True,save=True):
        categories = []
        reports = []
        
        for cat in Category:
            logging.info(f"Category Report preparing: {cat.value}...")
            datas = self.get_data(cat)
            data_reports = list( DataReports(data,anno_stats,image_stats) for data in datas)
            reports.append(CategoryReports(data_reports))
            categories.append(cat)
                 
        logging.info(f"Dataset Report Preparing: {self.path}")
        output = DatasetReports(categories,reports)
        logging.info(f"Dataset Report: \n{output}")
        if save ==True:
            p = Path(self.path,"output")
            create_statistic_yaml(output.results,str(p))
        return output
        
    def copy(self,dst_path):
        dateid = datetime_id(with_line=False)
        self.build_skeleton(dst_path)
        detect_path = Path(dst_path,"detect")
        detect_path.mkdir(exist_ok=True)
        for cat in Category:
            anno_paths = self.annotations_path_dict[cat]
            im_paths = self.images_path_dict[cat]
            
            dst_imgs_path = Path(detect_path,"images",cat.value)
            dst_annos_path = Path(detect_path,"labels",cat.value)
            
            logging.info(f"{Path(self.path).stem} {cat.value} copy process")
            for pth in tqdm(anno_paths,desc="Annotiations duplicating..."):
                new_anno_name = self.path.stem + "_" + dateid + "_" + Path(pth).name
                shutil.copy(pth, Path(dst_annos_path, new_anno_name))
            for pth in tqdm(im_paths,desc=" images duplicating..."):
                new_im_name =  self.path.stem + "_" + dateid +  "_" + Path(pth).name
                shutil.copy(pth, Path(dst_imgs_path, new_im_name))
        shutil.copy(Path(self.path,"detect","detect.yaml"),str(Path(detect_path,"detect.yaml")))
        logging.info("Duplications Completed")
            
    def copy_to_same_folder(self,dst_path):
        """
        Copies dataset datas to same folder like [frame_02.jpg, frame_02.txt]
        Args:
            dst_path (str): destination folder
        """
        for cat in Category:
            anno_paths = self.annotations_path_dict[cat]
            im_paths = self.images_path_dict[cat]
            
            logging.info(f"{Path(self.path).stem} {cat.value} copy process")
            for pth in tqdm(anno_paths,desc="Annotiations duplicating..."):
                new_anno_name = self.path.stem + "_" + Path(pth).name
                shutil.copy(pth, Path(dst_path, new_anno_name))
            for pth in tqdm(im_paths,desc=" images duplicating..."):
                new_im_name =  self.path.stem + "_" + Path(pth).name
                shutil.copy(pth, Path(dst_path, new_im_name)) 
        logging.info("Duplications to Same Folder Completed")
        
    def import_from_same_folder(self, src_path):
        """
        Duplicates images and text files from same folder and converts to Dataset
        Args:
            src_path (str): Source folder path
        """
        im_names = glob(f"{src_path}/*.jpg")
        label_names = glob(f"{src_path}/*.txt")
        im_paths = list( Path(src_path, name) for name in im_names)
        label_paths = list( Path(src_path, name) for name in label_names)
        
        for pth in tqdm(im_paths, desc="images locating..."):
            shutil.copy(pth, Path(self.path,"detect","images","train"))
        for pth in tqdm(label_paths, desc="txt files locating..."):
            shutil.copy(pth, Path(self.path,"detect","labels","train"))
        logging.info(f"Imported images from {src_path} to {self.path} Dataset")
            
    def resize_images(self,newshape:tuple,apply_smaller_images=True):
        """
        Resize images in the dataset to a specified shape.
        Args:
            newshape (tuple): The target shape for resizing as (width, height).
            apply_smaller_images (bool, optional): If True, resize all images regardless of their original size.
                If False, only resize images that are larger than the target shape; images with a larger area are skipped.
                Defaults to True.
        Raises:
            AssertionError: If `newshape` does not have exactly two dimensions.
        Notes:
            - Iterates over all categories and their associated data.
            - When `apply_smaller_images` is False, images with a larger area than `newshape` are not resized and a log message is generated.
        """
        assert len(newshape) == 2, "New shape must have 2 dimension"
        
        for cat in Category:
            datas = self.get_data(cat)
            for data in tqdm(datas,desc=f"Resizing {cat.name} datas"):
                if apply_smaller_images:
                    data.image_data.resize(newshape)
                else:
                    (height, width, _) = data.image_data.shape
                    nw,nh = newshape
                    if nw > width or nh > height:
                        logging.info(f"{data.name} resize process passed because it has larger area")
                        continue
                    else:
                        data.image_data.resize(newshape)
                   
    def split_standart(self,train:float,val:float,test:float,random=True):
        """
        Splits the dataset into training, validation, and test sets according to the specified ratios.
        Args:
            train (float): Proportion of the dataset to use for training. Should be between 0 and 1.
            val (float): Proportion of the dataset to use for validation. Should be between 0 and 1.
            test (float): Proportion of the dataset to use for testing. Should be between 0 and 1.
            random (bool, optional): Whether to shuffle the data before splitting. Defaults to True.
        Raises:
            AssertionError: If the sum of train, val, and test is not equal to 1.
        Side Effects:
            Changes the category of each data item in the dataset to TRAIN, VALIDATION, or TEST.
            Logs the split information and success message.
        Note:
            The function assumes that self.get_data(cat) returns a list of data items for the given category,
            and that each data item has a change_category method.
        """
        assert int(train + test + val) == 1, "train + test + val must equal to 1.0"

        pool = []
        for cat in Category:
            pool.extend(self.get_data(cat))
            
        if random:
            np.random.shuffle(pool)
            
        count = len(pool)
        count_train = int(count * train)
        count_val = int(count * val)
        count_test = int(count - count_train - count_val)
        
        logging.info(f"{count} = {count_train}(train,{train}) {count_val}(val,{val}) {count_test}(test,{test})")
          
        for i,data in enumerate(tqdm(pool,"Splitting")):
            data:Data
            if i >= 0 and i < count_train:
                data.change_category(Category.TRAIN)
            elif i >= count_train and i < count_train + count_val:
                data.change_category(Category.VALIDATION)
            else:
                data.change_category(Category.TEST)
        
        logging.info(f"Dataset: {self.path.stem} Splitted Successfully")
    
    def split_balanced(self, train: float = 0.5, val: float = 0.3, test: float = 0.2):
        """
        Splits the dataset into train, validation, and test sets while balancing label distributions as much as possible.
        The method aims to minimize label starvation (i.e., the lack of certain labels) in each split. The process is as follows:
            - For train, test, and validation, label starvation counts are calculated, e.g., {train: 0:256, 1:120, 2:10, 3:20, test: ...}.
            - A global list of label counts is created, e.g., [(data_01, {0:12, 1:5, 2:0, 3:1}), ...].
            - For each label, a list is maintained, sorted from the data item with the most of that label to the least, e.g., 0: [(data_04), (data_02), ...], where data_04 has the most label 0.
            - In each iteration, the split category (train, val, or test) with the highest total starvation is selected, e.g., test: {0:130, 1:12}, total_starvation = 142.
            - The label with the highest starvation in the selected category is chosen, e.g., 130 → label 0 is most needed.
            - The first data item from the sorted list for that label is selected if it is still available in the global counts list; otherwise, the next item is checked, and so on.
        Args:
            train (float): Proportion of data to allocate to the training set. Default is 0.5.
            val (float): Proportion of data to allocate to the validation set. Default is 0.3.
            test (float): Proportion of data to allocate to the test set. Default is 0.2.
        Raises:
            AssertionError: If the sum of train, val, and test ratios does not equal 1.0.
        Returns:
            None
        """

        # train, test ve val için label starvations olacak {train: 0:256, 1: 120, 2:10, 3:20, test: ...}#
        # global bir label counts listesi olacak [(data_01, {0: 12, 1:5, 2:0, 3:1}),(...] #
        # her label için max to min olacak şekilde liste tutulacak 0:[(data_04),(data_02),] örn: data_04 en çok 0 verisine sahip veriymiş #
        # train test ve val kategorileri için her iterasyonda en fazla total starvationu olan kategori seçilecek örn: test: {0:130,1:12}, total_starvation = 142
        # seçilen kategorinin en fazla ihtiyaç duyduğu label seçilecek örn: 130 -> yani 0 isteniyor en fazla
        # 0 kategorisinin listesinden önce gelen data global counts listesinde var ise çekilecek yok ise bir sonraki ve bir sonrakine geçilerek devam edilecek
        assert int(train + test + val) == 1, "train + test + val must equal to 1.0"
        assert 0.0 < train < 1.0 and 0.0 < val < 1.0 and 0.0 < test < 1.0, "Ratios must be between 0 and 1"
        
        # total label counts
        result_names = self.get_report(anno_stats=True,image_stats=False,save=False).results
        label_counts_dict:dict = result_names['total']['annotation']
        labels = list(label_counts_dict.keys())
        
        # find starvations for each category according to train, test, val split ratios 
        train_starvations, test_starvations, val_starvations = {}, {}, {}
        for key, value in label_counts_dict.items():
            train_starvations.update({key : int(value * train)})
            val_starvations.update({key : int(value * val)})
        for key, value in label_counts_dict.items():
            test_starvations.update({
                key : value - train_starvations[key] - val_starvations[key]
            })
        train_starvations = {k: train_starvations[k] for k in sorted(train_starvations.keys())}
        test_starvations = {k: test_starvations[k] for k in sorted(test_starvations.keys())}
        val_starvations = {k: val_starvations[k] for k in sorted(val_starvations.keys())}
        logging.info(f"Starvation counts for each category: \ntrain:{train_starvations}\nval:{val_starvations}\ntest:{test_starvations}")
        
        # Prepare data pool
        data_names = [] # [(frame_0095),(),...]
        data_current_cats = []
        data_label_counts_list = [] # [{0:121, 1:42, ...},{},...]
        for cat in Category:
            cat_d = self.get_data(cat)
            for data in cat_d:
                data_names.append((data.name))
                data_current_cats.append(cat)
                data_label_counts_list.append(data.annotation_data.get_stats())
        
        # add label padding for each data, ex: {0:1} -> {0:1, 1:0, 2:0, 3:0}
        for idx, cts in enumerate(data_label_counts_list):
            padded = {}
            for label in labels:
                if label not in cts.keys():
                    padded.update({label : 0})
                else:
                    padded.update({label: cts[label]})
            data_label_counts_list[idx] = padded   
                 
        # creating data list sorted values (max to min) for each label      
        sorted_data_names = {} # {2: [(frame_0095),(),...]}
        sorted_data_counts = {} # [2: {0:121, 1:42, ...},{},...]
        for label in labels:
            srtd_data_names, srtd_data_counts = zip(*sorted(
                zip(data_names, data_label_counts_list),
                key=lambda x: x[1][label],
                reverse=True
            ))
            sorted_data_names.update({label : list(srtd_data_names)})
            sorted_data_counts.update({label : list(srtd_data_counts)})
        
        # step functions 
        def cat_total_starvation(dic:dict):
            return sum(dic.values())
        
        def most_hungary_cat():
            return sorted(zip(
                [Category.TRAIN, Category.TEST, Category.VALIDATION],
                [train_starvations, test_starvations, val_starvations]),
                    key= lambda x: cat_total_starvation(x[1]),
                    reverse=True
                )[0]
            
        def most_needed_food(dic:dict):
            return sorted(dic.items(),
                          key= lambda x: x[1],
                          reverse=True
                          )[0][0]
        
        def remove_food_from_every_list(data_name):
            for lbl in labels:
                data_idx = sorted_data_names[lbl].index(data_name)
                sorted_data_names[lbl].pop(data_idx)
                sorted_data_counts[lbl].pop(data_idx)
        
        # results pool
        result_names = {
            Category.TRAIN : [],
            Category.TEST: [],
            Category.VALIDATION : [],
        }
        results_counts = {
            Category.TRAIN: {label: 0 for label in labels},
            Category.TEST: {label: 0 for label in labels},
            Category.VALIDATION: {label: 0 for label in labels},
        }
        
        # process
        for _ in range(len(data_names)):
            category, cat_starvation = most_hungary_cat()
            food = most_needed_food(cat_starvation)
            food_data_name = sorted_data_names[food][0]
            food_data_count = sorted_data_counts[food][0]
            remove_food_from_every_list(food_data_name)
            
            for lbl in labels:
                cnt = food_data_count[lbl]
                cat_starvation[lbl] -= cnt
                
            i = data_names.index(food_data_name)
            
            result_names[category].append((food_data_name, data_current_cats[i]))
            for l in labels:
                results_counts[category][l] += food_data_count[l]   
            
        # Locating   
        for cat in Category:
            results_counts[cat] = {k: results_counts[cat][k] for k in sorted(results_counts[cat].keys())}
            logging.info(f"Result {cat.value} Feeding Counts:{results_counts[cat]}")
            
        for cat, strvtn in zip(Category, [train_starvations, test_starvations, val_starvations]):
            strvtn = {k: strvtn[k] for k in sorted(strvtn.keys())}
            logging.info(f"Leftover {cat.value} Starvation {strvtn}")
 
        for cat in Category:
            names =  result_names[cat]
            for name, old_category in tqdm(names,desc=f'{cat.value} values locating... '):
                data = Data(self.path,old_category,name)
                data.change_category(cat)
    
    def sub_dataset(self,ratio:float,random=True,path=None):
        assert 0.0 < ratio < 1.0, "Ratio must be between 0.0 and 1.0 (exclusive)"
        if path is None:
            path = Path(self.path,"output")
            
        new_ds_path = Path(path,f"sub_{self.path.stem}_{ratio}_rand-{random}_{datetime_id()}")
        new_ds_path.mkdir()
        self.build_skeleton(new_ds_path)
        
        for cat in Category:
            datas = self.get_data(cat)
            if random:
                np.random.shuffle(datas)
            count = int(len(datas) * ratio)
            
            for data in tqdm(datas[:count]):
                new_images_path = str(Path(new_ds_path,"detect",DatasetFolders.IMAGES.value[0],cat.value))
                new_annos_path = str(Path(new_ds_path,"detect",DatasetFolders.LABELS.value[0],cat.value))
                data.copy(new_images_path,new_annos_path)
        
        return new_ds_path
            
    def rename_datas_consecutive(self, prefix: str = "", keep_current_names=True, zero_pad: int = 7):
        """
        Renames all data items consecutively with zero-padded numbers for correct sorting.

        Args:
            prefix (str): Prefix for the new names.
            keep_current_names (bool): Whether to append the current name to the new name.
            zero_pad (int): Number of digits for zero-padding the counter.
        """
        logging.info("Renaming Process Started")
        counter = 0
        for cat in Category:
            datas = self.get_data(cat)
            for data in tqdm(datas):
                newname = f"{prefix}_{str(counter).zfill(zero_pad)}"
                if keep_current_names:
                    newname += f"_{data.name}"
                data.rename(newname)
                counter += 1

        logging.info("Renamed all datas successfully")
                    
    def remove_data(self,data:Data):
        data.remove()
    
    def export_unmatches(self,path=None):
        """
        Moves unmacthed datas to target path
        """
        target_path = path or Path(self.path,"output",f"unmatched_data_{datetime_id()}")
        target_path.mkdir()
        images_path = Path(target_path,"images")
        images_path.mkdir()
        annos_path = Path(target_path,"annotations")
        annos_path.mkdir()
        
        for cat in Category:
            names = self.unmatched_images[cat]
            for name in tqdm(names,desc=f"{cat.value} unmacthed images"):
                im_path = Path(self.path,"detect","images",cat.value,name).with_suffix(".jpg")
                dst_im_path = Path(images_path,name).with_suffix(".jpg")
                shutil.move(im_path,dst_im_path)
                
            names = self.unmatched_annotations[cat]
            for name in tqdm(names,desc=f"{cat.value} unmacthed annotations"):
                anno_path = Path(self.path,"detect","labels",cat.value,name).with_suffix(".txt")
                dst_anno_path = Path(annos_path,name).with_suffix(".txt")
                shutil.move(anno_path,dst_anno_path)
        
    def convert_annotations(self,targets_dict:dict):
        for cat in Category:
            datas = self.get_data(cat)
            for data in tqdm(datas,desc=f"{cat.value} converting {targets_dict}"):
                data.annotation_data.convert_objects(targets_dict)
        
    def apply_filter(self,filter_func:Callable[[np.array],np.array]):
        for cat in Category:
            datas = self.get_data(cat)
            for data in tqdm(datas,desc=f"{cat.value} filtering "):
                data.image_data.apply_filter(filter_func)
    
    def slice_images(self,target_shape:Tuple[int, int]):
        """
        Args:
            target_shape (width:int ,height:int) : Target slice shape.
        
        """
        for cat in Category:
            datas = self.get_data(cat)
            for data in tqdm(datas,desc=f"{cat.value} slicing "):
                data.slice(target_shape)
        
        logging.info(f"Image sliced to {target_shape}")
        
    def review_dataset(self):
        from tools.monitor.monitor_helper import MonitorHelper
        import cv2
        import math
        
        ds_config = OmegaConf.load(Path(self.path,"detect","detect.yaml"))
        helper = MonitorHelper()
        global_cfg = get_conf()
        _controls_dict = {
            "q" : "exit",
            "space" : "jump category",
            "a" : "back",
            "d" : "forward",
            "k" : "paint object color"
        }

        paint_object_color = True
        for cat in Category:
            part_index = 0
            data_index = 0
            data_len = len(self.matches[cat]) 
            chunk_size = 100
            part_count = math.ceil(data_len / chunk_size)
            extra = data_len % chunk_size
            fl_indexes = []
            exit_category = False
            winname = f"{Path(self.path).stem}-{cat.value}"
            
            
            if data_len == 0:
                logging.info(f"{cat} hasn' got data")
                continue
            # first and last indexes of parts
            counter = 0
            while True:
                f = counter * chunk_size
                l = (counter + 1) * chunk_size
                if not l > data_len:
                    fl_indexes.append((f,l))
                else:
                    if extra != 0:
                        fl_indexes.append((f,f + extra))
                    break
                counter += 1
            
            # data surf
            while True:
                f,l = fl_indexes[part_index]
                datas = self.get_data(cat,f,l)    
                while True:
                    data = datas[data_index]
                    
                    #surf
                    frame = data.image_data.get_image()
                    frame = helper.paint_objects(frame, data, list(label for label in ds_config.names.values()),paint_color=paint_object_color)
                    frame = cv2.resize(frame, (global_cfg.review_monitor.monitor_width, global_cfg.review_monitor.monitor_height))
                    frame = helper.paint_info(frame, data, data_index, f,l, part_index, part_count, _controls_dict)
                    
                    cv2.imshow(winname, frame)
                    key = cv2.waitKey(0)
                    if key == ord("q"):
                        cv2.destroyAllWindows()
                        return
                    elif key == ord(" "):
                        cv2.destroyWindow(winname)
                        exit_category = True
                        break
                    elif key == ord("d"):
                        data_index += 1
                    elif key == ord("a"):
                        data_index -= 1
                    elif key == ord("k"):
                        paint_object_color = not paint_object_color
                    # surf
                    
                    # back with data_index
                    if data_index == -1:
                        if part_index != 0:
                            part_index -= 1
                            data_index = fl_indexes[part_index][1] - fl_indexes[part_index][0] -1
                            break
                        else:
                            data_index = 0
                    # forward with data_index
                    if data_index == fl_indexes[part_index][1] - fl_indexes[part_index][0]:
                        if part_index != part_count-1:
                            part_index += 1
                            data_index = 0
                            break
                        else:
                            data_index = fl_indexes[part_index][1] - fl_indexes[part_index][0]-1
                        
                if exit_category:
                    break

    def get_backround_parts_of_images(self) -> dict[Category, Tuple[np.array, str]]:
        """
        Find background image using objectless areas
        Returns:
            Results_dict (dict[Category,Tuple[np.array,str]]) : Dictionary for per category which includes Tuple of image,image_name like 
                {'train': [(frame, frame_name),(),...], 'test': [(),...], 'val' : [(),...]}
        """

        def _find_objecteless_part(frame, objects: list[Object]):
            h, w, _ = frame.shape
            for obj in objects:
                obj.to_absolute(w, h)

            mask = np.zeros((h, w), dtype=np.uint8)
            for obj in objects:
                mask[obj.y1:obj.y2, obj.x1:obj.x2] = 1

            def max_histogram_area(heights):
                stack = []
                max_area = 0
                left = 0
                right = 0
                height = 0
                i = 0
                while i <= len(heights):
                    h = heights[i] if i < len(heights) else 0
                    if not stack or h >= heights[stack[-1]]:
                        stack.append(i)
                        i += 1
                    else:
                        top = stack.pop()
                        width = i if not stack else i - stack[-1] - 1
                        area = heights[top] * width
                        if area > max_area:
                            max_area = area
                            height = heights[top]
                            right = i
                            left = i - width
                return max_area, left, right, height

            max_area = 0
            final_rect = None
            histogram = [0] * w

            for y in range(h):
                for x in range(w):
                    histogram[x] = 0 if mask[y, x] else histogram[x] + 1
                area, left, right, height = max_histogram_area(histogram)
                if area > max_area:
                    max_area = area
                    final_rect = (left, y - height + 1, right, y + 1)

            if final_rect:
                x1, y1, x2, y2 = final_rect
                crop = frame[y1:y2, x1:x2]
                return cv2.resize(crop, (w, h))
            else:
                return None

        results = {
            'train': [],
            'val': [],
            'test': []
        }
        for cat in Category:
            datas = self.get_data(cat)
            for data in tqdm(datas, desc=cat.value):
                frame = data.image_data.get_image()
                objects = data.annotation_data.objects
                output = _find_objecteless_part(frame, objects)
                if output is not None:
                    results[cat.value].append((output, data.image_data.path.name))

        return results
                
    @staticmethod      
    def build_skeleton(path):
        """
        Creates a directory skeleton for a dataset at the specified path.

        This function generates the following structure:
        - A 'detect' directory containing subdirectories for each dataset folder (as defined in DatasetFolders),
            each of which contains subdirectories for each category (as defined in Category).
        - An 'output' directory.

        If any of the directories already exist, they will not be recreated.

        Args:
                path (str or Path): The root directory where the dataset skeleton will be created.

        Raises:
                OSError: If a directory cannot be created due to a system-related error.
        """
        detect_path = Path(path, "detect")
        detect_path.mkdir(exist_ok=True)
        output_path = Path(path, "output")
        output_path.mkdir(exist_ok=True)
        for folder in DatasetFolders:
            ds_folder_path = Path(detect_path, folder.value[0])
            ds_folder_path.mkdir(exist_ok=True)
            for cat in Category:
                cat_folder_path = Path(ds_folder_path, cat.value)
                cat_folder_path.mkdir(exist_ok=True)  
        logging.info("Dataset Skeleton Build")
        
    @classmethod  
    def create(cls, name, path, detect_yaml_dict: dict):
        ds_path = Path(path, name)
        ds_path.mkdir(exist_ok=True)
        detect_path = Path(ds_path,"detect","detect.yaml")
        cls.build_skeleton(ds_path)
        
        conf = OmegaConf.create(detect_yaml_dict)
        OmegaConf.save(config=conf, f=str(detect_path))
        logging.info(f"Created Dataset {ds_path.name}")
        return cls(str(ds_path))