import os
from pathlib import Path
import logging
from omegaconf import OmegaConf
from enum import Enum
import time
from glob import glob
import threading

from tools.project import Project
from tools.dataset import Dataset
from tools.enums import MainPaths, Category
from tools.utils import evalute_model, datetime_id, get_conf
from tools.image_filters import Filters
from tools.gui.constants import MainWinTexts
from typing import Tuple

MAINPATH = MainPaths.MAINPATH.value
PROJECTSPATH = MainPaths.PROJECTSPATH.value
CONFIG_PATH = MainPaths.CONFIG_PATH.value
LOGGING_PATH = MainPaths.LOGGING_PATH.value
MODELS_PATH = MainPaths.MODELSPATH.value


def _save_conf(newconf):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        OmegaConf.save(config=newconf, f=f.name)
   
def _get_current_project(conf) -> Project:
    return Project(conf.chosen_project)     
        
timer_threads = []

def _executer_async(message="PROCESS STARTED", level=10):
    def decorator(func):
        def inner(*args, **kwargs):
            def run_func():
                logging.info("#" * level + f" {message}")
                start = time.time()
                result = func(*args, **kwargs)
                end = time.time()
                logging.info("#" * level + f" {message} Process completed in {end - start:.2f} seconds")
                return result
            
            t = threading.Thread(target=run_func)
            t.start()
            timer_threads.append(t)
            return t  
        return inner
    return decorator

def _executer_sync(message="PROCESS STARTED", level=10):
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
    @_executer_async("Create Project")
    def create_project(name:str):
        conf = get_conf()
            
        # create project
        Project.create(PROJECTSPATH, name, labels=list(conf.default_classes))
        
        # switch chosen project on conf
        project_path = Path(PROJECTSPATH, name)
        conf.chosen_project = str(project_path)
        _save_conf(conf)
        
        logging.info("Chosen project changed to new project")
        
    @_executer_async("Create Dataset")
    def create_dataset(name:str):
        conf = get_conf()
        logging.info("Default Project Labels Will Use")
        chosen_project = _get_current_project(conf)
        chosen_project.create_dataset(name,conf.default_classes)

    @_executer_async("Merge Datasets")
    def merge_datasets():
        conf = get_conf()
        p = _get_current_project(conf)
        p.merge()
        
    @_executer_async("Copy Dataset")
    def copy_dataset(dataset:Dataset, dst_path:Path):
        logging.info(f"Chosen Dataset to Copy: {dataset}")
        dst_path = dst_path.replace("\\", "/")
        dst_path = Path(dst_path)
        dataset.copy(dst_path)
        
    @_executer_async("Copy Dataset to Same Folder")
    def copy_dataset_to_same_folder(dataset:Dataset, dst_path:Path):
        logging.info(f"Chosen Dataset to Copy: {dataset}")
        dst_path = dst_path.replace("\\", "/")
        dst_path = Path(dst_path)
        dataset.copy_to_same_folder(dst_path)
    
    @_executer_async("Import From Same Folder")  
    def import_from_same_folder(dataset:Dataset, src_path:Path):
        logging.info(f"Chosen Dataset to import: {dataset}")
        src_path = src_path.replace("\\", "/")
        src_path = src_path.replace("\"","")
        src_path = Path(src_path)
        dataset.import_from_same_folder(src_path)
    
    @_executer_async("Resize Images")
    def resize_images(dataset:Dataset, w:int, h:int):
        dataset.resize_images((w,h))
        logging.info(f"Resized to Width:{w} Height:{h}")
        
    @_executer_async("Standard Split")
    def standart_split(dataset:Dataset,train,val):
        test = float(1-train-val)
        dataset.split_standart(train,val,test)
        logging.info(f"Applied Train Test Split: Train:{train} Test:{test} Val:{val}")
    
    @_executer_async("Balanced Split")
    def balanced_split(dataset:Dataset,train,val):
        test = float(1-train-val)
        dataset.split_balanced(train,val,test)
        logging.info(f"Applied Balanced Train Test Split: Train:{train} Test:{test} Val:{val}")
    
    @_executer_async("Create Sub Dataset")
    def create_sub_dataset(dataset:Dataset, ratio):
        dataset.sub_dataset(ratio)

    @_executer_async("Rename Datas Consecutively")
    def rename_datas_consecutively(dataset:Dataset,prefix="",keep_current=True):
        dataset.rename_datas_consecutive(prefix,keep_current)

    @_executer_async("Remove Data")
    def remove_data():
        ## TODO 
        logging.error(f"This function temporily absent")

    @_executer_async("Export Unmatches")
    def export_unmatches(dataset:Dataset):
        dataset.export_unmatches()

    @_executer_async("Convert Annotations")
    def convert_annotations(dataset:Dataset, targets_dict:dict):
        dataset.convert_annotations(targets_dict)

    @_executer_async("Apply Filters")
    def apply_filters(dataset:Dataset):
        """
        TODO
        This function is broken currently
        """
        ################
        for idx, filter in enumerate(Filters):
           filter_name, func = filter.value
           logging.info(f"{idx}:{filter_name}")
        ################ TODO
        n = 0
        assert 0 <= n < len(Filters), "Wrong Index"
        c_filter_name, c_func = list(Filters)[n].value
        logging.info(f"Apply: {c_filter_name}")
        dataset.apply_filter(c_func)
        
    @_executer_async("Slice Images")
    def slice_images(dataset:Dataset, h:int, w:int):
        dataset.slice_images(target_shape=(w,h))
        
    ProjectCreateProject = ("Create Project", create_project)
    ProjectCreateDataset = ("Create Dataset", create_dataset)
    ProjectMergeDatasets = ("Merge Datasets", merge_datasets)
    DatasetCopyDataset = ("Copy Dataset", copy_dataset)
    DatasetCopyDatasetToSameFolder = ("Copy Dataset To Same Folder", copy_dataset_to_same_folder)
    DatasetImportFromSameFolder = ("Import From Same Folder to Dataset", import_from_same_folder)
    DatasetResizeImages = ("Resize Images", resize_images)
    DatasetStandartSplit = ("Standard Split", standart_split)
    DatasetBalancedSplit = ("Balanced Split", balanced_split)
    DatasetCreateSubDataset = ("Create Sub Dataset", create_sub_dataset)
    DatasetRenameDatasConsecutively = ("Rename Datas Consecutively", rename_datas_consecutively)
    DatasetRemoveData = ("Remove Data", remove_data)
    DatasetExportUnmatches = ("Export Unmatches", export_unmatches)
    DatasetConvertAnnotations = ("Convert Annotations", convert_annotations)
    DatasetApplyFilter = ("Apply Filter", apply_filters)
    DatasetSliceImages = ("Slice Images", slice_images)
    

class ReviewOperations(Enum):
    """
    Operations which not change anything about data
    """
    @_executer_sync("Project Analysis")
    def project_analysis():
        output_dict = selected_project.analysis()
        result_text = f"Results--\n{output_dict}"
        logging.info(result_text)
        return result_text
    
    @_executer_sync("Dataset Analysis")
    def dataset_analysis():
        report = selected_dataset.get_report()
        result_text = f"Results {report}"
        logging.info(result_text)
        return result_text
        
    ProjectAnalysis = ("Project Statistics", project_analysis)
    DatasetAnalysis = ("Dataset Analysis", dataset_analysis)

class ModelOperations(Enum):
    
    @_executer_async("Evaluate Model")
    def model_evaluation(project:Project,dataset:Dataset,model,evaluate_all_datasets):
        conf = get_conf()
        project = Project(conf.chosen_project)
        detect_paths = []
        evaluate_all_datasets = True         
        if evaluate_all_datasets:
            for name in project.dataset_list:
                detect_paths.append(Path(project.path,"datasets",name,"detect","detect.yaml")) 
        else:
            detect_paths.append(Path(dataset.path,"detect","detect.yaml"))
        
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
        
    ModelEvaluation = ("Model Evaluation", model_evaluation)
  
class Operations(Enum):
    REVIEW = ("Review Operations",ReviewOperations)
    EDIT = ("Editing Operations",EditOperations)
    MODEL = ("Model Operations",ModelOperations)
    
global selected_project
global selected_dataset
global selected_operation
global operation_names
global conjugation_results
global dataset_paths
global project_paths    


selected_dataset:Dataset = None
selected_project:Project = None
selected_operation = list(Operations)[0].value[1]
operation_names:list[str] = list(o.value[0] for o in Operations)
conjugation_results:dict = {p : 0 for p in Category}
dataset_paths:list[str] = None
project_paths:list[str] = None

class MainAttributes:
    def __init__(self):
        self.cfg = get_conf()
        self.set_project(-1) # -1 for chosen_project from config.yaml
        self.list_dataset_paths()
        self.list_project_paths()
        self.set_dataset(0)
         
    def list_dataset_paths(self) -> list[Tuple]:
        global selected_project, dataset_paths
        paths = []
        for i, name in enumerate(selected_project.dataset_list):
            paths.append(Path(selected_project.path, "datasets", name))
            logging.info(f"{i}:{name}")
        dataset_paths = paths
    
    def list_project_paths(self):
        global project_paths
        paths = [] 
        project_names = os.listdir(MainPaths.PROJECTSPATH.value)
        for i, name in enumerate(project_names):
            logging.info(f"{i}:{name}")     
            paths.append(Path(MainPaths.PROJECTSPATH.value,name))  
        project_paths = paths
    
    def get_selected_dataset(self):
        global selected_dataset
        return selected_dataset
    
    def get_selected_prject(self):
        global selected_project
        return selected_project
    
    def get_selected_operation(self):
        global selected_operation
        return selected_operation
    
    def get_operation_names(self):
        global operation_names
        return operation_names
    
    def get_conjugation_results(self):
        global conjugation_results
        return conjugation_results
    
    def get_dataset_paths(self):
        global dataset_paths
        return dataset_paths
    
    def get_project_paths(self):
        global project_paths
        return project_paths
    
    def set_dataset(self,index:int):
        global selected_dataset, dataset_paths
        selected_dataset = Dataset(dataset_paths[index])
        for cat in Category:
            unmch_anno_count = len(selected_dataset.unmatched_annotations[cat])
            unmch_image_count = len(selected_dataset.unmatched_images[cat])
            conjugation_results[cat] = unmch_anno_count + unmch_image_count
            
    def set_project(self,index):
        global selected_project, project_paths
        if index == -1:
            selected_project = Project(self.cfg.chosen_project)
        else:
            selected_project = Project(project_paths[index])
            self.cfg.chosen_project = project_paths[index]
            _save_conf(self.cfg)
            
    def set_operations(self, operation: Operations):
        global selected_operation
        selected_operation = operation
