from enum import Enum

class MainWinStyles(Enum):
    style = """
        QWidget {
            background-color: #23272f;
            color: #f8f9fa;
        }
        QLineEdit {
            background-color: #343a40;
            color: #f8f9fa;
            border: 1px solid #495057;
            padding: 4px;
        }
        QLabel {
            color: #f8f9fa;
        }
        QPushButton {
            background-color: #495057;
            color: #f8f9fa;
            border: 1px solid #6c757d;
            border-radius: 6px;
            padding: 8px;
        }
        QPushButton:hover {
            background-color: #343a40;
        }
        QTextEdit {
            background-color: #343a40;
            color: #f8f9fa;
            border: 1px solid #495057;
        }
    """

    conjugation_bar_style = "background: #393d3c; border: 1px solid #aaa; font-size: 12px; min-width: 80px; min-height: 20px; max-height: 16px; qproperty-alignment: AlignCenter;"