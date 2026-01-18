"""
Главный файл приложения 3D Model Viewer

Точка входа в приложение. Инициализирует и запускает GUI.
"""

import sys
import os

from PyQt5.QtWidgets import QApplication

# Добавляем пути к модулям
sys.path.insert(0, os.path.dirname(__file__))

from ui.main_window import MainWindow


def main():
    """
    Главная функция приложения
    
    Создает QApplication, инициализирует главное окно и запускает цикл событий.
    """
    app = QApplication(sys.argv)
    app.setApplicationName("3D Model Viewer")
    app.setOrganizationName("CG Project")
    
    # Создаем и показываем главное окно
    window = MainWindow()
    window.show()
    
    # Запускаем цикл событий
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
