import os
import logging
from pathlib import Path
from .dataset import Dataset
from .enums import ProjectFiles, Category
from .reports import create_statistic_yaml,create_statistic_excel, ProjectReports
from .utils import datetime_id, build_detect_yaml
from omegaconf import OmegaConf

from tqdm import tqdm
class Project:
    
    def __init__(self,path):
        self.path = path
        self.name = Path(path).stem
        
    @property
    def detect_yaml_path(self):
        return Path(self.path,"detect.yaml")
    
    @property
    def dataset_list(self):
        return os.listdir(Path(self.path,"datasets"))
    
    def analysis(self,annotation_stats=True,image_stats= True,excel=True):
        """
        Generates and returns a statistical analysis report for all datasets in the project.
        This method compiles annotation and image statistics for each dataset in the project,
        aggregates the results, and outputs the report in either Excel or YAML format.
        Args:
            annotation_stats (bool, optional): Whether to include annotation statistics in the report. Defaults to True.
            image_stats (bool, optional): Whether to include image statistics in the report. Defaults to True.
            excel (bool, optional): If True, outputs the report as an Excel file; if False, outputs as a YAML file. Defaults to True.
        Returns:
            dict: A dictionary containing the aggregated statistical reports for all datasets.
        """
        logging.info(f"Project Report {self.name} preparing... ")
        ds_reports = list(Dataset(Path(self.path,"datasets",name)).get_report(anno_stats=annotation_stats,image_stats=image_stats) for name in self.dataset_list)
        output_dict = ProjectReports(self.dataset_list,ds_reports).results
        
        if excel:
            create_statistic_excel(output_dict,str(Path(self.path,ProjectFiles.OUTPUT_ANALYSIS.value)))
        else:
            create_statistic_yaml(output_dict,str(Path(self.path,ProjectFiles.OUTPUT_ANALYSIS.value)))
        return output_dict

    def create_dataset(self,name:str,labels:list[str])->Dataset:
        """
        Creates a new dataset configuration and initializes it using the Dataset.create method.
        Args:
            name (str): The name of the dataset to be created.
            labels (list): A list of label names for the dataset.
            path (str): The file system path where the dataset will be stored.
        Description:
            This method constructs a dictionary mapping label indices to label names,
            prepares a configuration dictionary for dataset detection tasks (including
            paths for training, validation, and test images), and calls the Dataset.create
            method to initialize the dataset at the specified path.
        """
        detect_yaml = build_detect_yaml(labels)
        dataset = Dataset.create(name,Path(self.path,"datasets"),detect_yaml)
        return dataset

    def merge(self):
        
        logging.info("Merging Process Started")
        output_ds_name = f"{self.name}_{datetime_id()}"
        output_ds_path = Path(self.path,ProjectFiles.OUTPUT_MERGED.value)
        detect_yaml_dict= OmegaConf.load(self.detect_yaml_path)
        Dataset.create(output_ds_name,str(output_ds_path),detect_yaml_dict)
        
        for ds_name in tqdm(self.dataset_list):
            ds = Dataset(Path(self.path,ProjectFiles.DATASETS.value,ds_name))
            ds.copy(str(Path(output_ds_path,output_ds_name)))
            
    def check_object_errors(self):
        has_error = []
        for ds_name in tqdm(self.dataset_list):
            ds = Dataset(Path(self.path,ProjectFiles.DATASETS.value,ds_name))
            errs = ds.check_object_errors()
            if errs:
                has_error.append(Path(ds.path).stem)
        logging.info(f"List of faults: {has_error}")
        
    @staticmethod
    def create(path,name,labels:list):
        """
        Creates a new project directory structure at the specified path with the given name.
        Args:
            path (str or Path): The base directory where the project folder will be created.
            name (str): The name of the project folder to create.
        Returns:
            Path: The path to the newly created project directory.
        Side Effects:
            - Creates a new directory at the specified location.
            - Creates subdirectories as defined in ProjectFiles.
            - Logs the creation of each directory.
        Raises:
            FileExistsError: If the project directory or any subdirectory already exists.
            OSError: If the directory cannot be created due to permission issues or invalid path.
        """
        project_path = Path(path,name)
        os.mkdir(project_path)
        for folder in ProjectFiles:
            pth = Path(project_path,folder.value)
            os.mkdir(pth)
            logging.info(f"Created {pth}")
            
        logging.info("Project Created")
        
        detect_yaml = build_detect_yaml(labels)
        logging.info(f"Project Labels: ",detect_yaml)
        
        detect_conf = OmegaConf.create(detect_yaml)
        OmegaConf.save(config=detect_conf, f=Path(project_path, "detect.yaml"))
        return project_path