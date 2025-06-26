# YoloDatasetLab

YoloDatasetLab, YOLO tabanlı veri setleriyle çalışmayı kolaylaştıran, açık kaynaklı bir Python paketidir. Görüntü, video ve çerçeve (frame) tabanlı veri setlerinin toplanması, dönüştürülmesi, birleştirilmesi ve YOLO modelleriyle test edilmesi için kapsamlı araçlar sunar.

## 🚀 Özellikler

- Farklı formatlardaki veri setlerini kolayca dönüştürme ve birleştirme
- Video, görüntü ve çerçeve bazlı veri toplama ve işleme
- YOLO modelleriyle kolay test ve değerlendirme
- Komut satırı ve PyQt6 tabanlı GUI desteği
- Açık kaynak ve topluluğa açık katkı

## 📦 Kurulum

Projeyi klonlayarak kullanabilirsiniz:

```bash
git clone https://github.com/rag0nn/spiral_yolo_data_laboratory.git
cd spiral_yolo_data_laboratory
```

Alternatif olarak, `YoloDatasetLab` klasörünü projenize ekleyip modülleri doğrudan import edebilirsiniz.

## 📘 Kullanım
- **Manuel kullanım** için:  
  ```python
  from YoloDatasetLab.tools.dataset import Dataset
  from YoloDatasetLab.tools.project import Project

  ds = Dataset("/path/to/dataset")
  ds.resize_images((640, 480))
  ```
- **Terminal tabanlı menü** için (Önerilir):  
  ```bash
  python YoloDatasetLab/main_terminal.py
  ```
- **GUI** ile işlemleri görsel olarak gerçekleştirmek için (Geliştirmesi Devam Ediyor... 🚧):  
  ```bash
  python YoloDatasetLab/main_gui.py
  ```

## 🛠️ Terminal Operations Fonksiyonları

Aşağıda, `operations_terminal.py` içindeki ana fonksiyonlar ve kısa açıklamaları listelenmiştir:

### EditOperations (Veri Üzerinde Değişiklik Yapanlar)
- `create_project`: Yeni bir proje oluşturur.
- `create_dataset`: Seçili projeye yeni bir veri seti ekler.
- `merge_datasets`: Projedeki veri setlerini birleştirir.
- `copy_dataset`: Bir veri setini belirtilen dizine kopyalar.
- `copy_dataset_to_same_folder`: Bir veri setini aynı klasör altında kopyalar.
- `import_from_same_folder`: Aynı klasörden veri seti içe aktarır.
- `resize_images`: Veri setindeki tüm görselleri yeniden boyutlandırır.
- `standart_split`: Veri setini standart oranlarda train/val/test olarak böler.
- `balanced_split`: Sınıf dengesi gözeterek veri setini böler.
- `create_sub_dataset`: Veri setinin bir alt kümesini oluşturur.
- `rename_datas_consecutively`: Veri setindeki dosyaları ardışık olarak yeniden adlandırır.
- `remove_data`: Veri setinden veri siler (şu an pasif).
- `export_unmatches`: Eşleşmeyen görsel ve etiketleri dışa aktarır.
- `convert_annotations`: Etiketleri verilen eşleme ile dönüştürür.
- `apply_filters`: Görsellere filtre uygular.
- `slice_images`: Görselleri parçalara böler.

### ReviewOperations (Veri Üzerinde Değişiklik Yapmayanlar)
- `switch_project`: Aktif projeyi değiştirir.
- `project_analysis`: Proje genel istatistiklerini gösterir.
- `dataset_analysis`: Seçili veri setinin detaylı analizini yapar.

### ModelOperations (Model ile İlgili İşlemler)
- `model_evaluation`: Seçili model ile veri seti(leri) üzerinde değerlendirme yapar.

## 📂 Dosya ve Klasör Yapısı

```
YoloDatasetLab/
  ├── __init__.py
  ├── config.yaml
  ├── main_terminal.py (Terminalden kontrol için)
  ├── main_gui.py (Gui'den kontrol için, !!! Geliştiriliyor 🚧)
  ├── operations_terminal.py 
  ├── operations_gui.py 
  ├── tools/
  │     ├── __init__.py
  │     ├── project.py (Proje)
  │     ├── dataset.py (Veri Seti)
  │     ├── data.py (Veri, resim ve label'ı içerisinde tutar)
  │     ├── enums.py (Sabit Değişkenler)
  │     ├── image_filters.py (Görsel Efekt Filtereleri)
  │     ├── reports.py (Veri Raporlama Sınıfları)
  │     ├── object.py (YOLO Nesne Objeleri)
  │     ├── utils.py
  │     └── gui/
  │           ├── __init__.py
  │           ├── win_review.py
  │           ├── constants.py
  │           └── ... (diğer GUI dosyaları)
  ├── models/
  │     ├── ... (YOLO modelleri ve ağırlık dosyaları)
  ├── test/
  │     ├── data/
  │     └── apply.py
  ├── projects/
  │     ├── ... (oluşturulan projeler)
  │     └── project_example
  │           ├── archive.py (Projeye ait eski dosyalar burada saklanır)
  │           ├── output.py (İstatistikler, veri stlerini birleştirme gibi çıktılar burada)
  │           └── datasets (Projedeki veri setleri burada saklanır)
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

## 🤝 Katkıda Bulunma

Katkılarınızı memnuniyetle karşılıyoruz! Hataları bildirebilir, yeni özellikler ekleyebilir veya dokümantasyon geliştirebilirsiniz.

1. Fork'layın
2. Yeni bir dal (branch) oluşturun (`git checkout -b feature/yeniozellik`)
3. Değişikliklerinizi commitleyin (`git commit -am 'Açıklama'`)
4. Dalınızı push'layın (`git push origin feature/yeniozellik`)
5. Pull request açın

## 📝 Lisans

Bu proje [MIT Lisansı](LICENSE) ile lisanslanmıştır. Detaylar için LICENSE dosyasına bakınız.

---

Her türlü öneri, katkı ve geri bildiriminiz için teşekkürler!  
Daha fazla bilgi ve güncellemeler için [GitHub sayfamızı](https://github.com/rag0nn/spiral_yolo_data_laboratory) ziyaret edebilirsiniz.

---

## Desteklenen Veri Türleri
Nöral Networkler için : .pt
Görseller için : .jpg 
Etiketler için : .txt 