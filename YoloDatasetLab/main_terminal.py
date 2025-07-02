from operations_terminal import Menu
import logging
import os
from pathlib import Path

log_file =  Path(os.path.dirname(__file__),"logs","main_terminal.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler()
    ]
)          

def main():
    from tools.enums import MainPaths
    print(MainPaths.MAINPATH.value)
    Menu()
main()
# TODO EKLENECEKLER
# GUI
# REPORTS Obje içermeyen görsel sayısı (background görselleri) ve reports sistemini güncelle