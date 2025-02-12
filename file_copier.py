import sys
import shutil
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QPushButton, QFileDialog, QLabel, QStyle, QProgressDialog)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon
import time

def format_size(size):
    for unit in ['Б', 'КБ', 'МБ', 'ГБ']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} ТБ"

def format_speed(speed):
    return f"{format_size(speed)}/сек"

class FileCopier(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Копирование файлов")
        self.setMinimumSize(400, 300)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignCenter)
        
        # Добавляем кнопку выбора файлов
        self.select_files_button = QPushButton("Выбрать файлы")
        self.select_files_button.setIcon(self.style().standardIcon(QStyle.SP_FileDialogStart))
        self.select_files_button.setMinimumSize(200, 50)
        self.select_files_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border-radius: 5px;
                font-size: 14px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #219a52;
            }
        """)
        self.select_files_button.clicked.connect(self.select_files)
        
        self.status_label = QLabel("Выберите файлы для копирования")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #2c3e50;
                margin: 10px;
            }
        """)
        
        # Добавляем метку для отображения выбранных файлов
        self.selected_files_label = QLabel("Файлы не выбраны")
        self.selected_files_label.setAlignment(Qt.AlignCenter)
        self.selected_files_label.setWordWrap(True)
        self.selected_files_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #7f8c8d;
                margin: 5px;
            }
        """)
        
        # Добавляем метку для отображения прогресса
        self.progress_label = QLabel("")
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #34495e;
                margin: 5px;
            }
        """)
        
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
        self.copy_button.setEnabled(False)
        
        # Добавляем виджеты в layout
        layout.addWidget(self.status_label)
        layout.addWidget(self.select_files_button)
        layout.addWidget(self.selected_files_label)
        layout.addWidget(self.progress_label)
        layout.addWidget(self.copy_button)
        
        self.selected_files = []
        self.total_size = 0
        self.copied_size = 0
        self.start_time = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
        """)

    def select_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Выберите файлы для копирования",
            "",
            "Все файлы (*.*)"
        )
        
        if files:
            self.selected_files = files
            # Вычисляем общий размер файлов
            self.total_size = sum(os.path.getsize(f) for f in files)
            size_text = format_size(self.total_size)
            
            # Показываем только имена файлов, не полный путь
            file_names = [os.path.basename(f) for f in files]
            display_text = ", ".join(file_names[:3])
            if len(file_names) > 3:
                display_text += f" и еще {len(file_names) - 3} файл(ов)"
            display_text += f" (Общий размер: {size_text})"
            self.selected_files_label.setText(display_text)
            self.copy_button.setEnabled(True)
            self.status_label.setText("Выберите целевую директорию")
        else:
            self.selected_files = []
            self.selected_files_label.setText("Файлы не выбраны")
            self.copy_button.setEnabled(False)
            self.status_label.setText("Выберите файлы для копирования")

    def update_progress(self):
        if self.total_size == 0:
            return
            
        elapsed_time = time.time() - self.start_time
        if elapsed_time > 0:
            speed = self.copied_size / elapsed_time
            remaining_size = self.total_size - self.copied_size
            
            if speed > 0:
                eta = remaining_size / speed
                progress_text = (
                    f"Скорость: {format_speed(speed)}\n"
                    f"Прошло времени: {int(elapsed_time)} сек\n"
                    f"Осталось примерно: {int(eta)} сек"
                )
                self.progress_label.setText(progress_text)

    def copy_files(self):
        if not self.selected_files:
            return
            
        target_dir = QFileDialog.getExistingDirectory(
            self,
            "Выберите целевую директорию",
            "",
            QFileDialog.ShowDirsOnly
        )
        
        if target_dir:
            try:
                # Создаем прогресс-диалог
                progress = QProgressDialog("Подготовка к копированию...", "Отмена", 0, self.total_size, self)
                progress.setWindowModality(Qt.WindowModal)
                
                self.copied_size = 0
                self.start_time = time.time()
                self.timer.start(1000)  # Обновляем каждую секунду
                
                for source in self.selected_files:
                    if progress.wasCanceled():
                        break
                        
                    file_name = os.path.basename(source)
                    destination = os.path.join(target_dir, file_name)
                    
                    # Копируем файл с обновлением прогресса
                    with open(source, 'rb') as src, open(destination, 'wb') as dst:
                        while True:
                            if progress.wasCanceled():
                                break
                                
                            chunk = src.read(1024 * 1024)  # Читаем по 1 МБ
                            if not chunk:
                                break
                                
                            dst.write(chunk)
                            self.copied_size += len(chunk)
                            progress.setValue(self.copied_size)
                            
                self.timer.stop()
                
                if not progress.wasCanceled():
                    total_time = time.time() - self.start_time
                    avg_speed = self.total_size / total_time if total_time > 0 else 0
                    final_text = (
                        f"Файлы успешно скопированы!\n"
                        f"Общее время: {int(total_time)} сек\n"
                        f"Средняя скорость: {format_speed(avg_speed)}"
                    )
                    self.status_label.setText(final_text)
                    self.status_label.setStyleSheet("QLabel { color: #27ae60; font-size: 14px; }")
                else:
                    self.status_label.setText("Копирование отменено")
                    self.status_label.setStyleSheet("QLabel { color: #e74c3c; font-size: 14px; }")
                
                self.progress_label.setText("")
                
            except Exception as e:
                self.timer.stop()
                self.status_label.setText(f"Ошибка: {str(e)}")
                self.status_label.setStyleSheet("QLabel { color: #c0392b; font-size: 14px; }")
                self.progress_label.setText("")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileCopier()
    window.show()
    sys.exit(app.exec()) 