import sys
import shutil
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QPushButton, QFileDialog, QLabel, QStyle)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

class FileCopier(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Копирование файлов")
        self.setMinimumSize(400, 200)
        
        # Создаем центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Создаем вертикальное расположение
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignCenter)
        
        # Создаем и настраиваем метку
        self.status_label = QLabel("Выберите целевую директорию")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #2c3e50;
                margin: 10px;
            }
        """)
        
        # Создаем и настраиваем кнопку
        self.copy_button = QPushButton("Копировать файлы")
        self.copy_button.setIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton))
        self.copy_button.setMinimumSize(200, 50)
        self.copy_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 5px;
                font-size: 14px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #2574a9;
            }
        """)
        self.copy_button.clicked.connect(self.copy_files)
        
        # Добавляем виджеты в layout
        layout.addWidget(self.status_label)
        layout.addWidget(self.copy_button)
        
        # Устанавливаем стиль окна
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
        """)

    def copy_files(self):
        # Открываем диалог выбора директории
        target_dir = QFileDialog.getExistingDirectory(
            self,
            "Выберите целевую директорию",
            "",
            QFileDialog.ShowDirsOnly
        )
        
        if target_dir:
            try:
                # Получаем список файлов в текущей директории
                current_dir = os.getcwd()
                files = [f for f in os.listdir(current_dir) 
                        if os.path.isfile(os.path.join(current_dir, f))]
                
                # Копируем каждый файл
                for file in files:
                    if file != os.path.basename(__file__):  # Пропускаем копирование самого скрипта
                        source = os.path.join(current_dir, file)
                        destination = os.path.join(target_dir, file)
                        shutil.copy2(source, destination)
                
                self.status_label.setText("Файлы успешно скопированы!")
                self.status_label.setStyleSheet("QLabel { color: #27ae60; font-size: 14px; }")
                
            except Exception as e:
                self.status_label.setText(f"Ошибка: {str(e)}")
                self.status_label.setStyleSheet("QLabel { color: #c0392b; font-size: 14px; }")
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileCopier()
    window.show()
    sys.exit(app.exec()) 