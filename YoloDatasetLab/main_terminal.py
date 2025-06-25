from operations_terminal import Menu
import logging

logging.basicConfig(
    level=logging.DEBUG
)          

def main():
    from tools.enums import MainPaths
    print(MainPaths.MAINPATH.value)
    Menu()
main()
    
# TODO EKLENECEKLER

# GUI
# REPORTS Obje içermeyen görsel sayısı (background görselleri) ve reports sistemini güncelle
## TODO: Object.fromXYWHF fonksiyonundaki daraltmalaraı kontrol edilecek görseller üzerinde görselleştirmeler ile