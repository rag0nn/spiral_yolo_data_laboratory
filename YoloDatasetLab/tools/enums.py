from enum import Enum
from pathlib import Path
from datetime import datetime
import os

class Category(Enum):
    TRAIN = "train"
    TEST = "test"
    VALIDATION = "val"
    
class FileType(Enum):
    IMAGE = "image"
    ANNOTATION = "annotation"
    
class ProjectFiles(Enum):
    ARCHIVE = "archive"
    DATASETS = "datasets"
    OUTPUT = "output"
    OUTPUT_ANALYSIS = "output/analysis"
    OUTPUT_MERGED = "output/merged"
    
class DatasetFolders(Enum):
    IMAGES = ["images","*.jpg"]
    LABELS = ["labels","*.txt"]
    
class MainPaths(Enum):
    MAINPATH = Path(os.path.dirname(__file__),"..")
    PROJECTSPATH = Path(MAINPATH,"projects")
    CONFIG_PATH = Path(MAINPATH,"config.yaml")
    LOGGING_PATH = str(Path(MAINPATH,"logs",str(datetime.now().strftime("log_%d-%m_%H-%M-%S.log"))) )
    MODELSPATH = Path(MAINPATH,"models")
    