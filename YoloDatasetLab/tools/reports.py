from .utils import save_dict_to_yaml, datetime_id
from pathlib import Path
import logging
from .data import Data
from .enums import FileType, Category
from tqdm import tqdm
import xlsxwriter

def create_statistic_yaml(stats_dict,output_path):
    current_id = datetime_id()
    report_name = "stats_" + current_id + ".yaml"
    save_dict_to_yaml(stats_dict,str(Path(output_path,report_name)))
    logging.info(f"{report_name} report saved to {output_path}")
    
def create_statistic_excel(stats_dict, output_path):
    """
    stats_dict: ProjectReports.results gibi bir dict
    output_path: klasör yolu (str veya Path)
    """
    output_path = Path(output_path)
    output_path.mkdir(exist_ok=True)
    # Dosya adı
    current_id = datetime_id()
    report_name = f"stats_{current_id}.xlsx"
    file_path = output_path / report_name

    # Tüm label anahtarlarını ve shape'leri topla
    all_labels = set()
    for ds_name, ds_val in stats_dict.items():
        if ds_name == "total":
            continue
        for cat, cat_val in ds_val.items():
            if cat == "total":
                continue
            anno = cat_val[0].get("annotation", {})
            all_labels.update(anno.keys())
    all_labels = sorted(all_labels)

    # Excel başlıkları
    headers = ["dataset", "category"] + [f"label_{lbl}" for lbl in all_labels] + ["image_count", "image_shape"]

    workbook = xlsxwriter.Workbook(str(file_path))
    worksheet = workbook.add_worksheet("Statistics")
    # Header
    for col, header in enumerate(headers):
        worksheet.write(0, col, header)
    row_idx = 1
    # Her dataset ve kategori için yaz
    for ds_name, ds_val in stats_dict.items():
        if ds_name == "total":
            continue
        for cat, cat_val in ds_val.items():
            if cat == "total":
                continue
            anno = cat_val[0].get("annotation", {})
            image = cat_val[1].get("image", {})
            row = [ds_name, cat]
            for lbl in all_labels:
                row.append(anno.get(lbl, 0))
            row.append(image.get("count", 0))
            shapes = image.get("shape", [])
            if isinstance(shapes, list):
                shape_str = ", ".join(["x".join(map(str, s)) for s in shapes])
            else:
                shape_str = str(shapes)
            row.append(shape_str)
            for col, val in enumerate(row):
                worksheet.write(row_idx, col, val)
            row_idx += 1
    # Total satırı
    total = stats_dict.get("total", {})
    anno = total.get("annotation", {})
    image = total.get("image", {})
    row = ["total", "total"]
    for lbl in all_labels:
        row.append(anno.get(lbl, 0))
    row.append(image.get("count", 0))
    shapes = image.get("shape", [])
    if isinstance(shapes, list):
        shape_str = ", ".join(["x".join(map(str, s)) for s in shapes])
    else:
        shape_str = str(shapes)
    row.append(shape_str)
    for col, val in enumerate(row):
        worksheet.write(row_idx, col, val)
    workbook.close()
    logging.info(f"{report_name} Excel report saved to {output_path}")
    
class DataReports:
    def __init__(self,data:Data,anno=True,image=True):
        self.image_counts_dict = {}
        self.label_counts_dict = {}
        if anno:
            self.label_counts_dict = data.annotation_data.get_stats()
        if image:
            self.image_counts_dict = data.image_data.get_stats()
        
    def __str__(self):
        return f"{self.label_counts_dict} {self.image_counts_dict}"

class CategoryReports:
    def __init__(self, reports: list[DataReports]):
        self.anno_results = {}
        self.image_results = {}
        shape_set = set()
        for rep in tqdm(reports):
            for key in rep.label_counts_dict.keys():
                if key in self.anno_results:
                    self.anno_results[key] += rep.label_counts_dict[key]
                else:
                    self.anno_results[key] = rep.label_counts_dict[key]

            for key in rep.image_counts_dict.keys():   
                if key == "shape":
                    # shape değerini tuple olarak ekle
                    val = rep.image_counts_dict[key]
                    if isinstance(val, (list, tuple)):
                        shape_set.add(tuple(val))
                elif key in self.image_results:
                    self.image_results[key] += rep.image_counts_dict[key]
                else:
                    self.image_results[key] = rep.image_counts_dict[key]
        # Tekrarsız shape'leri liste olarak ekle
        if shape_set:
            self.image_results["shape"] = [list(s) for s in shape_set]
        self.anno_results = {
            FileType.ANNOTATION.value : self.anno_results 
        }
        self.image_results = {
            FileType.IMAGE.value : self.image_results
        }
        
    def __str__(self):
        return f"{self.anno_results} {self.image_results}"
    
class DatasetReports:
    def __init__(self,category_list:list[Category],reports:list[CategoryReports]):
        self.results = {}
        for cat,rep in zip(category_list,reports):
            self.results.update({
                cat.value : [
                    rep.anno_results,
                    rep.image_results
                ]
            })
        total = self._get_total(reports)
        # Tekrarsız shape'leri total için de uygula
        if "shape" in total[FileType.IMAGE.value]:
            shape_set = set(tuple(s) for s in total[FileType.IMAGE.value]["shape"])
            total[FileType.IMAGE.value]["shape"] = [list(s) for s in shape_set]
        self.results.update({
            "total" : total
        })
            
    def __str__(self):
        return f"{self.results}"
        
    def _get_total(self, reports: list[CategoryReports]):
        total_anno = {}
        total_image = {}
        for rep in reports:
            labels_counts = rep.anno_results[FileType.ANNOTATION.value]
            for key in labels_counts.keys():
                if key in total_anno.keys():
                    total_anno[key] += labels_counts[key]
                else:
                    total_anno[key] = labels_counts[key]
            image_counts = rep.image_results[FileType.IMAGE.value]
            for key in image_counts.keys():
                print("->",total_image)
                if key in total_image.keys():
                    total_image[key] += image_counts[key]
                else:
                    total_image[key] = image_counts[key]
        return {
            FileType.ANNOTATION.value: total_anno,
            FileType.IMAGE.value: total_image
        }

class ProjectReports:
    def __init__(self, ds_names: list[str], ds_reports: list[DatasetReports]):
        self.results = {}
        for name, ds_report in zip(ds_names, ds_reports):
            self.results[name] = ds_report.results
        self.results["total"] = self._get_total(ds_reports)

    def _get_total(self, ds_reports: list[DatasetReports]):
        total_anno = {}
        total_image = {}
        total_shapes = set()
        total_count = 0
        for ds_report in ds_reports:
            # Her dataset'in total'ı
            ds_total = ds_report.results.get("total", {})
            anno = ds_total.get("annotation", {})
            image = ds_total.get("image", {})
            # Annotation toplama
            for key, val in anno.items():
                if key in total_anno:
                    total_anno[key] += val
                else:
                    total_anno[key] = val
            # Image toplama
            for key, val in image.items():
                if key == "shape":
                    for s in val:
                        total_shapes.add(tuple(s))
                elif key == "count":
                    total_count += val
                else:
                    if key in total_image:
                        total_image[key] += val
                    else:
                        total_image[key] = val
        if total_shapes:
            total_image["shape"] = [list(s) for s in total_shapes]
        total_image["count"] = total_count
        return {"annotation": total_anno, "image": total_image}
