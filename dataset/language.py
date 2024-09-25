class Language:
    
    def __init__(self) -> None:
        self.language = 'en'
        self.switch(self.language)

    def switch(self,language):
        if language == 'tr':
            self.language = 'tr'
            self.sectionB = TR().sectionB
            self.sectionD = TR().sectionD
            self.sectionE = TR().sectionE
        elif language == 'en':
            self.language = 'en'
            self.sectionB = EN().sectionB
            self.sectionD = EN().sectionD
            self.sectionE = EN().sectionE



class TR:
    sectionB = {
        "title" : "Organizasyon",
        "btn_create_ds" : "Yeni veri seti oluştur",
        "btn_merge_ds" : "Veri setlerini birleştir",
        "btn_analysis" : "Toplam Analizler",
        
        "cd_1":"Oluştur ",
        "cd_2":"Oluşturuldu ",

        "md_1":"Birleştir ",
        "md_2":"Oluşturuldu ",
    }

    sectionD = {
        "title" : "Veri seti analizleri",
        "btn_convert_labels":"Etiketleri dönüştür",
        "btn_train_test_split":"Eğitim Test Ayırımı Uygula",
        "btn_resize_frames":"Görselleri Yeniden Boyutlandır",
        "btn_btn_augment":"Verileri Çoğalt",

        "convert_labels_1" :"Örnek kullanım (şimdiki:hedef): 1:2,2:1,3:5,5:6",
        "convert_labels_2" :"Dönüştür",
        "convert_labels_3": "Dönüşüm Başarılı",
        "convert_labels_4": "Seçili veri seti yok",

        "tts_1" : "Örnek kullanım train: 0.5 val:0.3", 
        "tts_2" : "Dönüştür", 
        "tts_3" : "Ayırma işlemi başarılı", 
        "tts_4" : "Seçili veri seti yok", 

        "rf_1" : "Framelerin boyutunu en boy oranı değişmeden dönüştürme işlemi\nistenen uzun kenarın değeri girilmelidir",
        "rf_2" : "Dönüştür",
        "rf_3" : "Dönüşüm başarılı",
        "rf_4" : "Seçili veri seti yok",

        "aug_1":"Verilen açı aralığında rastgele açılar ile verilere döndürme işlemi uygulayarak çoğaltır\n Örnek kullım: 10,20",
        "aug_2":"Dönüştür",
        "aug_3":"Çoğaltma işlemi başarılı",
        "aug_4":"Seçili veri seti yok",    
    }

    sectionE = {
        "title":"Veri",
        "btn_remove":"Veriyi Sil",
        "btn_resize":"Görseli Yeniden Boyutlandır",
        "btn_convert":"Etiketleri Dönüştür",
        "lbl_po":"Objeleri Çizdir",
        "btn_switch":"Dili değiştir",

        "rf_1":"Framelerin boyutunu en boy oranı değişmeden dönüştürme işlemi\nistenen uzun kenarın değeri girilmelidir",
        "rf_2":"Dönüştür",
        "rf_3":"Dönüşüm başarılı ",
        "rf_4":"Seçili veri yok",

        "cl_1":"Örnek kullanım (şimdiki:hedef): 1:2,2:1,3:5,5:6",
        "cl_2":"Dönüştür",
        "cl_3":"Dönüşüm başarılı ",
        "cl_4":"Seçili veri yok",

        "re_1":"Bu veri kalıcı olarak silinsin mi?",
        "re_2":"Sil",
        "re_3":"Silme işlemi başarılı ",
        "re_4":"Seçili veri yok",
    }





class EN:
    sectionB = {
        "title" : "Organization",
        "btn_create_ds" : "Create Dataset",
        "btn_merge_ds" : "Merge Dataset",
        "btn_analysis" : "Total Analysis",

        "cd_1":"Create",
        "cd_2":"Created ",

        "md_1":"Merged",
        "md_2":"Merged ",
    }

    sectionD = {
        "title": "Dataset Analyses",
        "btn_convert_labels": "Convert Labels",
        "btn_train_test_split": "Apply Train-Test Split",
        "btn_resize_frames": "Resize Images",
        "btn_btn_augment": "Augment Data",

        "convert_labels_1": "Example usage (current:target): 1:2,2:1,3:5,5:6",
        "convert_labels_2": "Convert",
        "convert_labels_3": "Conversion Successful",
        "convert_labels_4": "No selected dataset",

        "tts_1": "Example usage train: 0.5 val:0.3",
        "tts_2": "Convert",
        "tts_3": "Splitting operation successful",
        "tts_4": "No selected dataset",

        "rf_1": "To resize frames without changing the aspect ratio,\nthe value of the desired long side must be entered",
        "rf_2": "Convert",
        "rf_3": "Conversion successful",
        "rf_4": "No selected dataset",

        "aug_1": "Augments data by applying random rotations within the given angle range\nExample usage: 10,20",
        "aug_2": "Convert",
        "aug_3": "Augmentation operation successful",
        "aug_4": "No selected dataset",
    }

    sectionE = {
        "title": "Data",
        "btn_remove": "Remove Data",
        "btn_resize": "Resize Image",
        "btn_convert": "Convert Labels",
        "lbl_po": "Draw Objects",
        "btn_switch": "Change Language",

        "rf_1": "To resize frames without changing the aspect ratio,\nthe value of the desired long side must be entered",
        "rf_2": "Convert",
        "rf_3": "Conversion successful",
        "rf_4": "No data selected",

        "cl_1": "Example usage (current:target): 1:2,2:1,3:5,5:6",
        "cl_2": "Convert",
        "cl_3": "Conversion successful",
        "cl_4": "No data selected",

        "re_1": "Should this data be permanently deleted?",
        "re_2": "Delete",
        "re_3": "Deletion successful",
        "re_4": "No data selected",
    }





