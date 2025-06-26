# YoloDatasetLab

YoloDatasetLab is an open-source Python package designed to simplify working with YOLO-based datasets. It provides comprehensive tools for collecting, converting, merging, and testing image, video, and frame-based datasets with YOLO models.

## 🚀 Features

- Easily convert and merge datasets in different formats
- Collect and process video, image, and frame-based data
- Easy testing and evaluation with YOLO models
- Command-line and PyQt6-based GUI support
- Open source and community-driven

## 📦 Installation

Clone the project:

```bash
git clone https://github.com/rag0nn/spiral_yolo_data_laboratory.git
cd spiral_yolo_data_laboratory
```

Alternatively, add the `YoloDatasetLab` folder to your project and import modules directly.

## 📘 Usage

- **Manual usage**:  
  ```python
  from YoloDatasetLab.tools.dataset import Dataset
  from YoloDatasetLab.tools.project import Project

  ds = Dataset("/path/to/dataset")
  ds.resize_images((640, 480))
  ```
- **Terminal menu** (Recommended):  
  ```bash
  python YoloDatasetLab/main_terminal.py
  ```
- **GUI** (Work in progress 🚧):  
  ```bash
  python YoloDatasetLab/main_gui.py
  ```

## 🛠️ Terminal Operations Functions

Below are the main functions in `operations_terminal.py` with brief descriptions:

### EditOperations (Modify Data)
- `create_project`: Create a new project.
- `create_dataset`: Add a new dataset to the selected project.
- `merge_datasets`: Merge datasets in the project.
- `copy_dataset`: Copy a dataset to a specified directory.
- `copy_dataset_to_same_folder`: Copy a dataset within the same folder.
- `import_from_same_folder`: Import a dataset from the same folder.
- `resize_images`: Resize all images in the dataset.
- `standart_split`: Split the dataset into train/val/test with standard ratios.
- `balanced_split`: Split the dataset with class balance.
- `create_sub_dataset`: Create a subset of the dataset.
- `rename_datas_consecutively`: Rename files in the dataset consecutively.
- `remove_data`: Remove data from the dataset (currently inactive).
- `export_unmatches`: Export unmatched images and labels.
- `convert_annotations`: Convert annotations using a given mapping.
- `apply_filters`: Apply filters to images.
- `slice_images`: Slice images into parts.

### ReviewOperations (Read-Only)
- `switch_project`: Change the active project.
- `project_analysis`: Show general project statistics.
- `dataset_analysis`: Detailed analysis of the selected dataset.

### ModelOperations (Model Related)
- `model_evaluation`: Evaluate the selected model on dataset(s).

## 📂 File and Folder Structure

```
YoloDatasetLab/
  ├── __init__.py
  ├── config.yaml
  ├── main_terminal.py (For terminal control)
  ├── main_gui.py (For GUI control, !!! In Development 🚧)
  ├── operations_terminal.py 
  ├── operations_gui.py 
  ├── tools/
  │     ├── __init__.py
  │     ├── project.py (Project)
  │     ├── dataset.py (Dataset)
  │     ├── data.py (Holds data, image, and label)
  │     ├── enums.py (Constant Variables)
  │     ├── image_filters.py (Image Effect Filters)
  │     ├── reports.py (Data Reporting Classes)
  │     ├── object.py (YOLO Object Classes)
  │     ├── utils.py
  │     └── gui/
  │           ├── __init__.py
  │           ├── win_review.py
  │           ├── constants.py
  │           └── ... (other GUI files)
  ├── models/
  │     ├── ... (YOLO models and weight files)
  ├── test/
  │     ├── data/
  │     └── apply.py
  ├── projects/
  │     ├── ... (created projects)
  │     └── project_example
  │           ├── archive.py (Old files related to the project are stored here)
  │           ├── output.py (Statistics, data merging outputs are here)
  │           └── datasets (Datasets in the project are stored here)
  │                   └── dataset_example (Datasets in the project are stored here)
  │                         └── output
  │                         └── detect
  │                               └── images
  │                                   └── train
  │                                   └── test
  │                                   └── val
  │                               └── labels
  │                                   └── train
  │                                   └── test
  │                                   └── val
  │                               └── detect.yaml
  ├── LICENSE
  └── README.md
```

## 🤝 Contributing

We welcome your contributions! You can report bugs, add new features, or improve documentation.

1. Fork the repository
2. Create a new branch (`git checkout -b feature/newfeature`)
3. Commit your changes (`git commit -am 'Description'`)
4. Push your branch (`git push origin feature/newfeature`)
5. Open a pull request

## 📝 License

This project is licensed under the [MIT License](LICENSE). See the LICENSE file for details.

---

Thank you for your suggestions, contributions, and feedback!  
For more information and updates, visit our [GitHub page](https://github.com/rag0nn/spiral_yolo_data_laboratory).

---

## Supported Files
.pt for nn models
.jpg for image data
.txt for annotation data




