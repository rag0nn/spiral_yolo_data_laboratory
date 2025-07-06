import yaml
from enum import Enum
import os
from pathlib import Path
from datetime import datetime
import logging
from omegaconf import OmegaConf
    
def save_dict_to_yaml(output_dict, output_path):
    def convert_sets_and_tuples(obj):
        """
        Recursively converts all sets and tuples within a nested data structure (composed of dictionaries, lists, sets, and tuples) into lists.

        Args:
            obj: The input object, which can be a set, tuple, list, dict, or any other type.

        Returns:
            The input object with all sets and tuples converted to lists, preserving the original structure for lists and dictionaries.
        """
        if isinstance(obj, (set, tuple)):
            return [convert_sets_and_tuples(i) for i in obj]
        elif isinstance(obj, dict):
            return {k: convert_sets_and_tuples(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_sets_and_tuples(i) for i in obj]
        else:
            return obj

    output_dict = convert_sets_and_tuples(output_dict)
    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump(output_dict, f, allow_unicode=True, sort_keys=False)

def datetime_id(with_line=True) -> str:
    """
    Verilen datetime objesini 'YYYY-MM-DD_HH-MM-SS' formatında string id'ye çevirir.
    """
    dt= datetime.now()
    if with_line:
        return dt.strftime("%Y-%m-%d_%H-%M-%S")
    else:
        return dt.strftime("%Y%m%d_%H%M%S")

def build_detect_yaml(labels:list[str]):
    names = {}
    
    for i,lbl in enumerate(labels):
        names.update({i:lbl})

    detect_yaml = {
        'names': names,
        'train': 'images/train',
        'val': 'images/val',
        'test': 'images/test'
    }
    
    return detect_yaml

def evalute_model(model,detect_yaml_path,results_save_path,):
    import torch.multiprocessing
    torch.multiprocessing.set_start_method('spawn', force=True)
    results = model.val(
        data=detect_yaml_path,
        workers=0,
        batch=1,
        save_json=True,           # Sonuçları JSON olarak kaydetmek için
        project=results_save_path,        # Kayıtların ana klasörü (istediğiniz path ile değiştirin)
        exist_ok=True,            # Klasör varsa üzerine yazmak için
        save_txt=True,             # Sonuçları txt olarak da kaydetmek için (isteğe bağlı)
        split="test"
    )
    logging.info(f"Average precision for all classes: {results.box.all_ap}")
    logging.info(f"Average precision: {results.box.ap}")
    logging.info(f"Average precision at IoU=0.50: {results.box.ap50}")
    logging.info(f"Class indices for average precision: {results.box.ap_class_index}")
    logging.info(f"F1 score: {results.box.f1}")
    logging.info(f"Mean average precision: {results.box.map}")
    logging.info(f"Mean average precision at IoU=0.50: {results.box.map50}")
    logging.info(f"Mean average precision at IoU=0.75: {results.box.map75}")
    logging.info(f"Mean average precision for different IoU thresholds: {results.box.maps}")
    logging.info(f"Mean precision: {results.box.mp}")
    logging.info(f"Mean recall: {results.box.mr}")
    return results

def get_conf():
    path = Path(__file__).parent.parent / "config.yaml"
    return OmegaConf.load(path)