import os
from pathlib import Path
from tqdm import tqdm
import logging
from omegaconf import OmegaConf
from enum import Enum
import time
from glob import glob
from typing import Tuple
import cv2

from tools.project import Project
from tools.dataset import Dataset
from tools.enums import MainPaths
from tools.utils import evalute_model, datetime_id, get_conf
from tools.image_filters import Filters


MAINPATH = MainPaths.MAINPATH.value
PROJECTSPATH = MainPaths.PROJECTSPATH.value
CONFIG_PATH = MainPaths.CONFIG_PATH.value
LOGGING_PATH = MainPaths.LOGGING_PATH.value
MODELS_PATH = MainPaths.MODELSPATH.value

def _save_conf(newconf):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        OmegaConf.save(config=newconf, f=f.name)
   
def _list_datasets():
    cfg = get_conf()
    p = _get_current_project(cfg)
    for i, name in enumerate(p.dataset_list):
        logging.info(f"{i}:{name}")
        
def _select_dataset() -> Tuple[Dataset, int]:
    cfg = get_conf()
    p = _get_current_project(cfg)
    for i, name in enumerate(p.dataset_list):
        logging.info(f"{i}:{name}")
            
    idx = input("Dataset Index ('d' for different): ")
    if idx == "d":
        external_ds_path = input("External Dataset Path: ")
        d = Dataset(external_ds_path)
    else:
        chosen_ds_name = p.dataset_list[int(idx)]
        d = Dataset(Path(p.path, "datasets", chosen_ds_name))
    return d, idx

def _select_model():
    from ultralytics import YOLO

    names = glob(f"{MODELS_PATH}/*.pt")
    for i, name in enumerate(names):
        logging.info(f"{i}:{Path(name).stem}")
    idx = int(input("Model Index: "))
    chosen_ds_name = names[idx]
    model = YOLO(Path(MODELS_PATH,chosen_ds_name))
    return model, idx

def _get_current_project(conf) -> Project:
    return Project(conf.chosen_project)     
        
def _timer(message="PROCESS STARTED",level=10):
    def decorator(func):
        def inner(*args, **kwargs):
            logging.info("#" * level + f" {message}")
            start = time.time()
            result = func(*args, **kwargs)
            end = time.time()
            logging.info("#" * level + f" {message} Process completed in {end - start:.2f} seconds")
            return result
        return inner
    return decorator

class EditOperations(Enum):
    """
    Operations which change something about data
    """
    @_timer("Create Project")
    def create_project():
        conf = get_conf()
        name = str(input("New Project Name: "))
            
        # create project
        Project.create(PROJECTSPATH, name, labels=list(conf.default_classes))
        
        # switch chosen project on conf
        project_path = Path(PROJECTSPATH, name)
        conf.chosen_project = str(project_path)
        _save_conf(conf)
        
        logging.info("Chosen project changed to new project")
        
    @_timer("Create Dataset")
    def create_dataset():
        conf = get_conf()
        name = str(input("New Dataset Name: "))
        logging.info("Default Project Labels Will Use")
        chosen_project = _get_current_project(conf)
        chosen_project.create_dataset(name,conf.default_classes)

    @_timer("Merge Datasets")
    def merge_datasets():
        conf = get_conf()
        p = _get_current_project(conf)
        p.merge()

    @_timer("Project Balanced Split")
    def project_balanced_split():
        conf = get_conf()
        chosen_project = _get_current_project(conf)
        train= float(input("Train Ratio: "))
        val= float(input("Validation Ratio: "))
        test = float(1-train-val)
        for dataset in chosen_project.dataset_list:
            dataset:Dataset
            ds = Dataset(Path(chosen_project.path,"datasets",dataset))
            ds.split_balanced(train,val,test)
            logging.info(f"Applied Balanced Train Test Split: Train:{train} Test:{test} Val:{val}")
        
    @_timer("Fix Project Object Errors")
    def fix_project_object_errors():
        conf = get_conf()
        chosen_project = _get_current_project(conf)
        chosen_project.fix_object_errors()
         
    @_timer("Copy Dataset")
    def copy_dataset():
        logging.info("Copy Dataset")
        dataset, idx = _select_dataset()
        logging.info(f"Chosen Dataset to Copy: {dataset}")
        dst = str(input("\n\nPath: "))
        dst = dst.replace("\\", "/")
        dst = Path(dst)
        dataset.copy(dst)
        
    @_timer("Copy Dataset to Same Folder")
    def copy_dataset_to_same_folder():
        logging.info("Copy Dataset Same Folder")
        dataset, idx = _select_dataset()
        logging.info(f"Chosen Dataset to Copy: {dataset}")
        dst = str(input("\n\nPath: "))
        dst = dst.replace("\\", "/")
        dst = Path(dst)
        dataset.copy_to_same_folder(dst)
    
    @_timer("Import From Same Folder")  
    def import_from_same_folder():
        logging.info("Import from same folder")
        dataset, idx = _select_dataset()
        logging.info(f"Chosen Dataset to import: {dataset}")
        dst = str(input("\n\n Source Path: "))
        dst = dst.replace("\\", "/")
        dst = dst.replace("\"","")
        dst = Path(dst)
        dataset.import_from_same_folder(dst)
    
    @_timer("Resize Images")
    def resize_images():
        dataset, idx = _select_dataset()
        w = int(input("Width: "))
        h = int(input("Height: "))
        dataset.resize_images((w,h))
        logging.info(f"Resized to Width:{w} Height:{h}")
        
    @_timer("Standard Split")
    def standart_split():
        dataset,idx = _select_dataset()
        train= float(input("Train Ratio: "))
        val= float(input("Validation Ratio: "))
        test = float(1-train-val)
        dataset.split_standart(train,val,test)
        logging.info(f"Applied Train Test Split: Train:{train} Test:{test} Val:{val}")
    
    @_timer("Balanced Split")
    def balanced_split():
        dataset,idx = _select_dataset()
        train= float(input("Train Ratio: "))
        val= float(input("Validation Ratio: "))
        test = float(1-train-val)
        dataset.split_balanced(train,val,test)
        logging.info(f"Applied Balanced Train Test Split: Train:{train} Test:{test} Val:{val}")
    
    @_timer("Create Sub Dataset")
    def create_sub_dataset():
        dataset,idx = _select_dataset()
        ratio = float(input("Slice Ratio: "))
        dataset.sub_dataset(ratio)

    @_timer("Rename Datas Consecutively")
    def rename_datas_consecutively():
        dataset,idx = _select_dataset()
        prefix = input("Prefix (Not Necessary): ")
        keep_current = input("Keep current data names (t/f): ")
        keep_current_decision = True
        if keep_current == "f":
            keep_current_decision = False
        dataset.rename_datas_consecutive(prefix,keep_current_decision)

    @_timer("Export Unmatches")
    def export_unmatches():
        dataset,idx = _select_dataset()
        dataset.export_unmatches()

    @_timer("Convert Annotations")
    def convert_annotations():
        dataset,idx = _select_dataset()
        targets = input("Targets (0:1,1:0..) etc: ")
        items = targets.split(",")
        dict_ = {}
        for item in items:
            current,target = item.split(":")
            current = int(current)
            target = int(target)
            dict_.update({current:target})
        dataset.convert_annotations(dict_)

    @_timer("Apply Filters")
    def apply_filters():
        dataset, _ = _select_dataset()
        for idx, filter in enumerate(Filters):
           filter_name, func = filter.value
           logging.info(f"{idx}:{filter_name}")
        n = int(input("Select Filter: "))
        assert 0 <= n < len(Filters), "Wrong Index"
        c_filter_name, c_func = list(Filters)[n].value
        logging.info(f"Apply: {c_filter_name}")
        dataset.apply_filter(c_func)
        
    @_timer("Slice Images")
    def slice_images():
        dataset, idx = _select_dataset()
        w = int(input("Slice width: "))
        h = int(input("Slice height: "))
        dataset.slice_images(target_shape=(w,h))
    
    @_timer("Fix Dataset Object Errors")
    def fix_dataset_object_errors():
        dataset, idx = _select_dataset()
        dataset.fix_object_errors()
        
    @_timer("Get Objectless Parts (Background)")
    def get_objectless_background_images():
        dataset, idx = _select_dataset()
        conf = get_conf()
        chosen_project = _get_current_project(conf)
        new_ds = chosen_project.create_dataset(f"{dataset.name}_BACKGROUND",["tasit","insan","UAP","UAI"])
        results = dataset.get_backround_parts_of_images()
        for title in ['train','test','val']:
            datas = results[title]
            for frame, name in tqdm(datas,desc=title):
                out_path = Path(new_ds.path,'detect','images',title,name)
                cv2.imwrite(out_path,frame)
                txt_path = Path(new_ds.path,'detect','labels',title,name.split(".")[0]+ ".txt")
                f = open(txt_path,"w")
                f.close()
    
        
    ProjectCreateProject = ("Create Project", create_project)
    ProjectCreateDataset = ("Create Dataset", create_dataset)
    ProjectMergeDatasets = ("Merge Datasets", merge_datasets)
    ProjectBalancedSplit = ("Project Balanced Split", project_balanced_split)
    ProjectFixObjectErrors = ("Project Fix Object Errors", fix_project_object_errors)
    DatasetCopyDataset = ("Copy Dataset", copy_dataset)
    DatasetCopyDatasetToSameFolder = ("Copy Dataset To Same Folder", copy_dataset_to_same_folder)
    DatasetImportFromSameFolder = ("Import From Same Folder to Dataset", import_from_same_folder)
    DatasetResizeImages = ("Resize Images", resize_images)
    DatasetStandartSplit = ("Standard Split", standart_split)
    DatasetBalancedSplit = ("Balanced Split", balanced_split)
    DatasetCreateSubDataset = ("Create Sub Dataset", create_sub_dataset)
    DatasetRenameDatasConsecutively = ("Rename Datas Consecutively", rename_datas_consecutively)
    DatasetExportUnmatches = ("Export Unmatches", export_unmatches)
    DatasetConvertAnnotations = ("Convert Annotations", convert_annotations)
    DatasetApplyFilter = ("Apply Filter", apply_filters)
    DatasetSliceImages = ("Slice Images", slice_images)
    DatasetFixObjectErrors = ("Dataset Fix Object Errors", fix_dataset_object_errors)
    DatasetGetObjectlessParts = ("Get Objectless Parts (Background)", get_objectless_background_images)
    
class ReviewOperations(Enum):
    """
    Operations which not change anything about data
    """
    @_timer("Switch Project")
    def switch_project():
        cfg = get_conf()
        project_names = [
            name for name in os.listdir(PROJECTSPATH)
            if os.path.isdir(os.path.join(PROJECTSPATH, name)) and not name.startswith('__')
        ]
        logging.info(f"Switch Chosen Project (current : {cfg.chosen_project})")

        for i, name in enumerate(project_names):
            logging.info(f"{i}:{name}")       
        idx = int(input("Swict Index: ")) 
        
        current_project_path = Path(cfg.chosen_project)
        new_project_path = str(current_project_path.with_name(project_names[idx]))
        cfg.chosen_project = new_project_path
        _save_conf(cfg)
        logging.info(f"Switched to {new_project_path}")
    
    @_timer("Project Analysis")
    def project_analysis():
        cfg = get_conf()
        p = _get_current_project(cfg)
        output_dict = p.analysis()
        logging.info(f"Results--\n{output_dict}")
    
    @_timer("List Datasets")
    def project_list_datasets():
        _list_datasets()
    
    @_timer("Check Project Object Errors")
    def project_check_object_errors():
        cfg = get_conf()
        p = _get_current_project(cfg)
        p.check_object_errors()
        
    @_timer("Dataset Analysis")
    def dataset_analysis():
        d, idx = _select_dataset()
        report = d.get_report()
        logging.info(f"Results {report}")
        
    @_timer("Review Dataset")
    def dataset_review():
        dataset, idx = _select_dataset()
        dataset.review_dataset()
    
    @_timer("Check Dataset Object Errors")
    def dataset_check_object_errors():
        dataset, idx = _select_dataset()
        dataset.check_object_errors()

    ProjectSwitchProject = ("Switch Project", switch_project)
    ProjectAnalysis = ("Project Statistics", project_analysis)
    ProjectListDatasets = ("List Datasets", project_list_datasets)
    ProjectCheckObjectErrors = ("Check Project Object Errors", project_check_object_errors)
    DatasetAnalysis = ("Dataset Analysis", dataset_analysis)
    DatasetReview = ("Dataset Review", dataset_review)
    DatasetCheckObjectErrors = ("Check Dataset Object Errors", dataset_check_object_errors)

class ModelOperations(Enum):
    
    @_timer("Evaluate Model")
    def model_evaluation():
        conf = get_conf()
        p = Project(conf.chosen_project)
        detect_paths = []
        model, idx = _select_model()
        ae = True
        ae_ = input("All Evaluation (t/f): ")
        if ae_ == 'f':
            ae = False
            
        if ae:
            for name in p.dataset_list:
                detect_paths.append(Path(p.path,"datasets",name,"detect","detect.yaml")) 
        else:
            d,idx = _select_dataset()
            detect_paths.append(Path(d.path,"detect","detect.yaml"))
        
        out_name = f"{datetime_id()}"
        for pth in detect_paths:
            o1 = Path(MODELS_PATH, "output")
            o2 = Path(o1,Path(str(model.model_name)).stem)
            o2.mkdir(exist_ok=True)
            o3 = Path(o2,Path(pth).parts[-3])
            o3.mkdir(exist_ok=True)
            o4 = Path(o3,out_name)
            o4.mkdir(exist_ok=True)
            print(o1,o2,o3,o4)
            results = evalute_model(model,pth,o4)
            
    @_timer("Dataset With Model Prediction")
    def dataset_with_model_prediction():
        conf = get_conf()
        p = Project(conf.chosen_project)
        model, idx = _select_model()
        images_path = str(input("Images Path: "))
        new_ds = p.create_dataset(f"{Path(images_path).stem}_PREDICTED",["tasit","insan","UAP","UAI"])
        for pth in tqdm(glob(images_path + "/*.jpg")):
            frame = cv2.imread(pth)
            labels = []
            results = model.predict(frame)[0]
            label_list = results.boxes.cls.cpu().numpy()
            bbox_list = results.boxes.xywhn.cpu().numpy()
            for lbl, (x,y,w,h) in zip(label_list,bbox_list):
                label_string = f"{int(lbl)} {x} {y} {w} {h}\n"
                labels.append(label_string)
            
            pth = Path(pth)
            im_path = Path(new_ds.path,"detect","images","train",pth.name)
            txt_path = Path(new_ds.path,"detect","labels","train",pth.stem + ".txt")
            cv2.imwrite(im_path,frame)
            f = open(txt_path,"w")
            f.writelines(labels)
            f.close()
    
    ModelEvaluation = ("Model Evaluation", model_evaluation)
    DatasetWithModelPrediction = ("Dataset With Model Prediction", dataset_with_model_prediction)

class Operations(Enum):
    REVIEW = ("Review Operations",ReviewOperations)
    EDIT = ("Editing Operations",EditOperations)
    MODEL = ("Model Operations",ModelOperations)

class Menu:
    
    def __init__(self):
        self.step(Operations)
        logging.info("Session Ended")

    def step(self, category: Enum):
        while True:
            selection = self.chose(category)
            if selection == -1:
                break
            # Eğer selection bir Enum class'ı ise (ör: ReviewOperations gibi), step ile devam et
            if isinstance(selection, type) and issubclass(selection, Enum):
                self.step(selection)
            else:
                selection()
                  
    def chose(self,enum_cat:Enum):
        """
        Prompts the user to select an option from an enumeration menu.
        Args:
            enum_cat (Enum): An enumeration class containing menu options. Each enum member's value is expected to be a tuple, where the first element is a display string and the second is the return value.
        Returns:
            Any: The second element of the selected enum member's value tuple.
        Raises:
            AssertionError: If the user input is not a valid index within the range of enum_cat.
        """
        logging.info(f"\n\nCurrent Project: {get_conf().chosen_project}")
        logging.info("-----Chose From Menu-----")
        for idx, item in enumerate(enum_cat):
            logging.info(f"{idx}: {item.value[0]}")
            
        chs = int(input("Choise (for back= -1): "))
        assert -1 <= chs <=len(enum_cat)-1, logging.error( "Wrong Index to Choose Something")
        if chs == -1:
            return -1
        else:
            for idx, item in enumerate(enum_cat):
                if idx == chs:
                    return item.value[1]

        
            
            
