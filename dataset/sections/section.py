from PyQt6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QMessageBox
from PyQt6.QtCore import Qt
class Section(QWidget):
    def __init__(self, children, scroll=False):
        super().__init__()
        self._scroll = scroll
        self._children = children  # Children listesini sakla
        self.setStyleSheet(f"""
                border: 2px solid black;  /* Tek çerçeve */
                padding: 1px;                    /* İç boşluk */
                background-color: white;
            """)
        
        self.layout_ = QVBoxLayout()  # Ana layout
        
        if self._scroll:
            self.scroll_area = QScrollArea()
            self.scroll_area.setWidgetResizable(True)
            
            self.content_widget = QWidget()  # Scroll alanı için içerik widget'ı
            self.layout2 = QVBoxLayout()  # İçerik için ayrı layout
            
            for chl in self._children:
                self.layout2.addWidget(chl)
            
            self.content_widget.setLayout(self.layout2)
            self.scroll_area.setWidget(self.content_widget)
            self.layout_.addWidget(self.scroll_area)
        
        else:
            for chl in self._children:
                self.layout_.addWidget(chl)
        
        self.setLayout(self.layout_)

    def remove(self, index):
        if 0 <= index < len(self._children):
            widget_to_remove = self._children[index]
            if self._scroll:
                self.layout2.removeWidget(widget_to_remove)
            else:
                self.layout_.removeWidget(widget_to_remove)

            #widget_to_remove.deleteLater()  # Bellek yönetimi için widget'ı sil
            self._children.pop(index) 

        else:
            QMessageBox.warning(self, "Uyarı", "Geçersiz index!")

    def update(self, new_children):
        # Mevcut öğeleri kaldır
        if self._scroll:
            # ScrollArea kullanılıyorsa content_widget içindeki layout'u temizle
            for widget in self._children:
                self.layout2.removeWidget(widget)
                widget.deleteLater()  # Bellekten sil

            self._children.clear()  # Mevcut children listesini temizle
            
            # Yeni öğeleri ekle
            for chl in new_children:
                self.layout2.addWidget(chl)
                self._children.append(chl)  # Yeni öğeleri listeye ekle
            
            # İçerik widget'ını yeniden ayarla
            self.content_widget.setLayout(self.layout2)
            self.scroll_area.setWidget(self.content_widget)
        
        else:
            # ScrollArea kullanılmıyorsa, doğrudan ana layout'a ekle
            for widget in self._children:
                self.layout_.removeWidget(widget)
                widget.deleteLater()
            
            self._children.clear()
            
            for chl in new_children:
                self.layout_.addWidget(chl)
                self._children.append(chl)
        
        self.updateGeometry()  # Yeni düzenlemeyi uygula
