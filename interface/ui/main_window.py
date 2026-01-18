"""
MainWindow - главное окно приложения для работы с 3D моделями

Этот класс реализует полный пользовательский интерфейс для:
- Загрузки и сохранения моделей
- Управления сценой с несколькими моделями
- Редактирования моделей (удаление вершин и полигонов)
- Применения трансформаций к моделям
- Переключения тем
- Обработки ошибок
"""

import sys
import os
from pathlib import Path

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QListWidget, QLabel, QFileDialog, QMessageBox, QGroupBox,
    QDoubleSpinBox, QSpinBox, QMenuBar, QMenu, QStatusBar, QSplitter
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon

# Добавляем пути к модулям
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from loaders.obj_reader import ObjReader
from loaders.obj_writer import ObjWriter
from models.model import Model
from models.scene import Scene
from ui.theme_manager import ThemeManager
from math.math_module.vector3 import Vector3


class ModelViewerWidget(QWidget):
    """
    Виджет для отображения 3D модели
    
    В реальном приложении здесь был бы OpenGL виджет для рендеринга.
    Для демонстрации это простой виджет с информацией о модели.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = None
        layout = QVBoxLayout()
        self.info_label = QLabel("Загрузите модель для просмотра")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet("font-size: 14px; padding: 20px;")
        layout.addWidget(self.info_label)
        self.setLayout(layout)
    
    def set_scene(self, scene):
        """Устанавливает сцену для отображения"""
        self.scene = scene
        self.update_display()
    
    def update_display(self):
        """Обновляет отображение информации о модели"""
        if not self.scene or self.scene.get_model_count() == 0:
            self.info_label.setText("Загрузите модель для просмотра")
            return
        
        selected_model = self.scene.get_selected_model()
        if selected_model:
            info = f"Модель: {selected_model.name}\n"
            info += f"Вершин: {selected_model.get_vertex_count()}\n"
            info += f"Граней: {selected_model.get_face_count()}\n"
            info += f"\nТрансформации:\n"
            info += f"Перемещение: ({selected_model.transform.translation.x:.2f}, "
            info += f"{selected_model.transform.translation.y:.2f}, "
            info += f"{selected_model.transform.translation.z:.2f})\n"
            info += f"Вращение: ({selected_model.transform.rotation.x:.2f}, "
            info += f"{selected_model.transform.rotation.y:.2f}, "
            info += f"{selected_model.transform.rotation.z:.2f})\n"
            info += f"Масштаб: ({selected_model.transform.scale.x:.2f}, "
            info += f"{selected_model.transform.scale.y:.2f}, "
            info += f"{selected_model.transform.scale.z:.2f})"
            self.info_label.setText(info)
        else:
            self.info_label.setText("Выберите модель из списка")


class MainWindow(QMainWindow):
    """
    Главное окно приложения
    
    Управляет всеми компонентами интерфейса и координирует работу
    между загрузчиками моделей, сценой и пользовательским интерфейсом.
    """
    
    def __init__(self):
        super().__init__()
        self.scene = Scene()
        self.theme_manager = ThemeManager()
        self.obj_reader = ObjReader()
        self.obj_writer = ObjWriter()
        
        self.init_ui()
        self.apply_theme()
    
    def init_ui(self):
        """Инициализация пользовательского интерфейса"""
        self.setWindowTitle("3D Model Viewer")
        self.setGeometry(100, 100, 1200, 800)
        
        # Создаем центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Главный layout
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Создаем сплиттер для разделения панелей
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Левая панель - список моделей и управление
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # Центральная панель - просмотр модели
        center_panel = self.create_center_panel()
        splitter.addWidget(center_panel)
        
        # Правая панель - трансформации и редактирование
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        # Устанавливаем пропорции
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        splitter.setStretchFactor(2, 1)
        
        # Создаем меню
        self.create_menu_bar()
        
        # Создаем статус бар
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Готово")
    
    def create_left_panel(self):
        """Создает левую панель со списком моделей"""
        panel = QWidget()
        layout = QVBoxLayout()
        panel.setLayout(layout)
        
        # Заголовок
        title = QLabel("Модели в сцене")
        title.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        # Кнопки управления моделями
        buttons_layout = QHBoxLayout()
        
        self.load_btn = QPushButton("Загрузить")
        self.load_btn.clicked.connect(self.load_model)
        buttons_layout.addWidget(self.load_btn)
        
        self.save_btn = QPushButton("Сохранить")
        self.save_btn.clicked.connect(self.save_model)
        self.save_btn.setEnabled(False)
        buttons_layout.addWidget(self.save_btn)
        
        self.remove_btn = QPushButton("Удалить")
        self.remove_btn.clicked.connect(self.remove_model)
        self.remove_btn.setEnabled(False)
        buttons_layout.addWidget(self.remove_btn)
        
        layout.addLayout(buttons_layout)
        
        # Список моделей
        self.models_list = QListWidget()
        self.models_list.itemSelectionChanged.connect(self.on_model_selected)
        layout.addWidget(self.models_list)
        
        return panel
    
    def create_center_panel(self):
        """Создает центральную панель для просмотра модели"""
        panel = QWidget()
        layout = QVBoxLayout()
        panel.setLayout(layout)
        
        # Виджет просмотра модели
        self.model_viewer = ModelViewerWidget()
        self.model_viewer.set_scene(self.scene)
        layout.addWidget(self.model_viewer)
        
        return panel
    
    def create_right_panel(self):
        """Создает правую панель с трансформациями и редактированием"""
        panel = QWidget()
        layout = QVBoxLayout()
        panel.setLayout(layout)
        
        # Группа трансформаций
        transform_group = QGroupBox("Трансформации")
        transform_layout = QVBoxLayout()
        
        # Перемещение
        move_layout = QHBoxLayout()
        move_layout.addWidget(QLabel("Перемещение:"))
        self.move_x = QDoubleSpinBox()
        self.move_x.setRange(-1000, 1000)
        self.move_x.setSingleStep(0.1)
        self.move_x.valueChanged.connect(self.update_translation)
        move_layout.addWidget(QLabel("X:"))
        move_layout.addWidget(self.move_x)
        
        self.move_y = QDoubleSpinBox()
        self.move_y.setRange(-1000, 1000)
        self.move_y.setSingleStep(0.1)
        self.move_y.valueChanged.connect(self.update_translation)
        move_layout.addWidget(QLabel("Y:"))
        move_layout.addWidget(self.move_y)
        
        self.move_z = QDoubleSpinBox()
        self.move_z.setRange(-1000, 1000)
        self.move_z.setSingleStep(0.1)
        self.move_z.valueChanged.connect(self.update_translation)
        move_layout.addWidget(QLabel("Z:"))
        move_layout.addWidget(self.move_z)
        
        transform_layout.addLayout(move_layout)
        
        # Вращение
        rotate_layout = QHBoxLayout()
        rotate_layout.addWidget(QLabel("Вращение:"))
        self.rotate_x = QDoubleSpinBox()
        self.rotate_x.setRange(-360, 360)
        self.rotate_x.setSingleStep(1)
        self.rotate_x.setSuffix("°")
        self.rotate_x.valueChanged.connect(self.update_rotation)
        rotate_layout.addWidget(QLabel("X:"))
        rotate_layout.addWidget(self.rotate_x)
        
        self.rotate_y = QDoubleSpinBox()
        self.rotate_y.setRange(-360, 360)
        self.rotate_y.setSingleStep(1)
        self.rotate_y.setSuffix("°")
        self.rotate_y.valueChanged.connect(self.update_rotation)
        rotate_layout.addWidget(QLabel("Y:"))
        rotate_layout.addWidget(self.rotate_y)
        
        self.rotate_z = QDoubleSpinBox()
        self.rotate_z.setRange(-360, 360)
        self.rotate_z.setSingleStep(1)
        self.rotate_z.setSuffix("°")
        self.rotate_z.valueChanged.connect(self.update_rotation)
        rotate_layout.addWidget(QLabel("Z:"))
        rotate_layout.addWidget(self.rotate_z)
        
        transform_layout.addLayout(rotate_layout)
        
        # Масштаб
        scale_layout = QHBoxLayout()
        scale_layout.addWidget(QLabel("Масштаб:"))
        self.scale_x = QDoubleSpinBox()
        self.scale_x.setRange(0.01, 100)
        self.scale_x.setValue(1.0)
        self.scale_x.setSingleStep(0.1)
        self.scale_x.valueChanged.connect(self.update_scale)
        scale_layout.addWidget(QLabel("X:"))
        scale_layout.addWidget(self.scale_x)
        
        self.scale_y = QDoubleSpinBox()
        self.scale_y.setRange(0.01, 100)
        self.scale_y.setValue(1.0)
        self.scale_y.setSingleStep(0.1)
        self.scale_y.valueChanged.connect(self.update_scale)
        scale_layout.addWidget(QLabel("Y:"))
        scale_layout.addWidget(self.scale_y)
        
        self.scale_z = QDoubleSpinBox()
        self.scale_z.setRange(0.01, 100)
        self.scale_z.setValue(1.0)
        self.scale_z.setSingleStep(0.1)
        self.scale_z.valueChanged.connect(self.update_scale)
        scale_layout.addWidget(QLabel("Z:"))
        scale_layout.addWidget(self.scale_z)
        
        transform_layout.addLayout(scale_layout)
        
        # Кнопка сброса
        reset_btn = QPushButton("Сбросить трансформации")
        reset_btn.clicked.connect(self.reset_transform)
        transform_layout.addWidget(reset_btn)
        
        transform_group.setLayout(transform_layout)
        layout.addWidget(transform_group)
        
        # Группа редактирования
        edit_group = QGroupBox("Редактирование модели")
        edit_layout = QVBoxLayout()
        
        # Удаление вершин
        delete_vertex_layout = QHBoxLayout()
        delete_vertex_layout.addWidget(QLabel("Удалить вершину:"))
        self.delete_vertex_spin = QSpinBox()
        self.delete_vertex_spin.setMinimum(0)
        self.delete_vertex_spin.setMaximum(0)
        delete_vertex_layout.addWidget(self.delete_vertex_spin)
        
        delete_vertex_btn = QPushButton("Удалить")
        delete_vertex_btn.clicked.connect(self.delete_vertex)
        delete_vertex_layout.addWidget(delete_vertex_btn)
        edit_layout.addLayout(delete_vertex_layout)
        
        # Удаление полигонов
        delete_face_layout = QHBoxLayout()
        delete_face_layout.addWidget(QLabel("Удалить полигон:"))
        self.delete_face_spin = QSpinBox()
        self.delete_face_spin.setMinimum(0)
        self.delete_face_spin.setMaximum(0)
        delete_face_layout.addWidget(self.delete_face_spin)
        
        delete_face_btn = QPushButton("Удалить")
        delete_face_btn.clicked.connect(self.delete_face)
        delete_face_layout.addWidget(delete_face_btn)
        edit_layout.addLayout(delete_face_layout)
        
        edit_group.setLayout(edit_layout)
        layout.addWidget(edit_group)
        
        layout.addStretch()
        
        return panel
    
    def create_menu_bar(self):
        """Создает меню бар"""
        menubar = self.menuBar()
        
        # Файл
        file_menu = menubar.addMenu('Файл')
        
        load_action = file_menu.addAction('Загрузить модель...')
        load_action.setShortcut('Ctrl+O')
        load_action.triggered.connect(self.load_model)
        
        save_action = file_menu.addAction('Сохранить модель...')
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_model)
        
        file_menu.addSeparator()
        
        exit_action = file_menu.addAction('Выход')
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        
        # Вид
        view_menu = menubar.addMenu('Вид')
        
        theme_action = view_menu.addAction('Переключить тему')
        theme_action.setShortcut('Ctrl+T')
        theme_action.triggered.connect(self.toggle_theme)
        
        # Справка
        help_menu = menubar.addMenu('Справка')
        
        about_action = help_menu.addAction('О программе')
        about_action.triggered.connect(self.show_about)
    
    def apply_theme(self):
        """Применяет текущую тему к интерфейсу"""
        stylesheet = self.theme_manager.get_stylesheet()
        self.setStyleSheet(stylesheet)
    
    def toggle_theme(self):
        """Переключает тему"""
        self.theme_manager.toggle_theme()
        self.apply_theme()
        theme_name = "темная" if self.theme_manager.get_theme() == "dark" else "светлая"
        self.status_bar.showMessage(f"Тема изменена на {theme_name}", 2000)
    
    def load_model(self):
        """Загружает модель из файла"""
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Загрузить модель",
            "",
            "OBJ Files (*.obj);;All Files (*)"
        )
        
        if not filepath:
            return
        
        try:
            # Читаем модель
            vertices, faces, normals, tex_coords = self.obj_reader.read(filepath)
            
            # Создаем объект модели
            model_name = Path(filepath).stem
            model = Model(vertices, faces, normals, tex_coords, model_name)
            
            # Валидируем модель
            is_valid, error_msg = model.validate()
            if not is_valid:
                self.show_error("Ошибка валидации модели", error_msg)
                return
            
            # Добавляем в сцену
            index = self.scene.add_model(model)
            
            # Обновляем интерфейс
            self.update_models_list()
            self.scene.select_model(index)
            self.on_model_selected()
            
            self.status_bar.showMessage(f"Модель '{model_name}' загружена успешно", 3000)
        
        except FileNotFoundError as e:
            self.show_error("Файл не найден", str(e))
        except ValueError as e:
            self.show_error("Ошибка чтения файла", str(e))
        except Exception as e:
            self.show_error("Неожиданная ошибка", f"Произошла ошибка при загрузке модели:\n{str(e)}")
    
    def save_model(self):
        """Сохраняет выбранную модель в файл"""
        model = self.scene.get_selected_model()
        if not model:
            self.show_error("Нет выбранной модели", "Выберите модель для сохранения")
            return
        
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить модель",
            f"{model.name}.obj",
            "OBJ Files (*.obj);;All Files (*)"
        )
        
        if not filepath:
            return
        
        try:
            self.obj_writer.write_model(filepath, model)
            self.status_bar.showMessage(f"Модель '{model.name}' сохранена успешно", 3000)
        
        except ValueError as e:
            self.show_error("Ошибка сохранения", str(e))
        except Exception as e:
            self.show_error("Неожиданная ошибка", f"Произошла ошибка при сохранении модели:\n{str(e)}")
    
    def remove_model(self):
        """Удаляет выбранную модель из сцены"""
        current_row = self.models_list.currentRow()
        if current_row < 0:
            return
        
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            "Вы уверены, что хотите удалить эту модель?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.scene.remove_model(current_row)
            self.update_models_list()
            self.on_model_selected()
            self.status_bar.showMessage("Модель удалена", 2000)
    
    def update_models_list(self):
        """Обновляет список моделей"""
        self.models_list.clear()
        for i, model in enumerate(self.scene.get_all_models()):
            self.models_list.addItem(f"{i + 1}. {model.name} ({model.get_vertex_count()} вершин, {model.get_face_count()} граней)")
        
        # Обновляем состояние кнопок
        has_models = self.scene.get_model_count() > 0
        self.save_btn.setEnabled(has_models)
        self.remove_btn.setEnabled(has_models)
    
    def on_model_selected(self):
        """Обработчик выбора модели"""
        current_row = self.models_list.currentRow()
        if current_row >= 0:
            self.scene.select_model(current_row)
            model = self.scene.get_selected_model()
            
            # Обновляем значения трансформаций
            self.move_x.setValue(model.transform.translation.x)
            self.move_y.setValue(model.transform.translation.y)
            self.move_z.setValue(model.transform.translation.z)
            
            # Конвертируем радианы в градусы
            import math
            self.rotate_x.setValue(math.degrees(model.transform.rotation.x))
            self.rotate_y.setValue(math.degrees(model.transform.rotation.y))
            self.rotate_z.setValue(math.degrees(model.transform.rotation.z))
            
            self.scale_x.setValue(model.transform.scale.x)
            self.scale_y.setValue(model.transform.scale.y)
            self.scale_z.setValue(model.transform.scale.z)
            
            # Обновляем спинбоксы для удаления
            max_vertex = max(0, model.get_vertex_count() - 1)
            max_face = max(0, model.get_face_count() - 1)
            self.delete_vertex_spin.setMaximum(max_vertex)
            self.delete_face_spin.setMaximum(max_face)
            
            # Обновляем отображение
            self.model_viewer.update_display()
        else:
            # Сбрасываем значения
            self.move_x.setValue(0)
            self.move_y.setValue(0)
            self.move_z.setValue(0)
            self.rotate_x.setValue(0)
            self.rotate_y.setValue(0)
            self.rotate_z.setValue(0)
            self.scale_x.setValue(1)
            self.scale_y.setValue(1)
            self.scale_z.setValue(1)
            self.model_viewer.update_display()
    
    def update_translation(self):
        """Обновляет перемещение модели"""
        model = self.scene.get_selected_model()
        if model:
            model.transform.translation = Vector3(
                self.move_x.value(),
                self.move_y.value(),
                self.move_z.value()
            )
            self.model_viewer.update_display()
    
    def update_rotation(self):
        """Обновляет вращение модели"""
        model = self.scene.get_selected_model()
        if model:
            import math
            model.transform.rotation = Vector3(
                math.radians(self.rotate_x.value()),
                math.radians(self.rotate_y.value()),
                math.radians(self.rotate_z.value())
            )
            self.model_viewer.update_display()
    
    def update_scale(self):
        """Обновляет масштаб модели"""
        model = self.scene.get_selected_model()
        if model:
            model.transform.scale = Vector3(
                self.scale_x.value(),
                self.scale_y.value(),
                self.scale_z.value()
            )
            self.model_viewer.update_display()
    
    def reset_transform(self):
        """Сбрасывает трансформации модели"""
        model = self.scene.get_selected_model()
        if model:
            model.transform.reset()
            self.on_model_selected()
            self.status_bar.showMessage("Трансформации сброшены", 2000)
    
    def delete_vertex(self):
        """Удаляет выбранную вершину"""
        model = self.scene.get_selected_model()
        if not model:
            self.show_error("Нет выбранной модели", "Выберите модель для редактирования")
            return
        
        vertex_idx = self.delete_vertex_spin.value()
        
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            f"Удалить вершину {vertex_idx}? Это также удалит все грани, содержащие эту вершину.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            deleted_count = model.delete_vertices([vertex_idx])
            if deleted_count > 0:
                self.update_models_list()
                self.on_model_selected()
                self.status_bar.showMessage(f"Удалена вершина {vertex_idx}", 2000)
            else:
                self.show_error("Ошибка", "Не удалось удалить вершину")
    
    def delete_face(self):
        """Удаляет выбранный полигон"""
        model = self.scene.get_selected_model()
        if not model:
            self.show_error("Нет выбранной модели", "Выберите модель для редактирования")
            return
        
        face_idx = self.delete_face_spin.value()
        
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            f"Удалить полигон {face_idx}?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            deleted_count = model.delete_faces([face_idx])
            if deleted_count > 0:
                self.update_models_list()
                self.on_model_selected()
                self.status_bar.showMessage(f"Удален полигон {face_idx}", 2000)
            else:
                self.show_error("Ошибка", "Не удалось удалить полигон")
    
    def show_error(self, title, message):
        """Показывает диалог с ошибкой"""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec_()
    
    def show_about(self):
        """Показывает диалог 'О программе'"""
        QMessageBox.about(
            self,
            "О программе",
            "3D Model Viewer\n\n"
            "Приложение для просмотра и редактирования 3D моделей в формате OBJ.\n\n"
            "Возможности:\n"
            "- Загрузка и сохранение моделей\n"
            "- Работа с несколькими моделями\n"
            "- Трансформации (перемещение, вращение, масштабирование)\n"
            "- Редактирование (удаление вершин и полигонов)\n"
            "- Светлая и темная темы\n"
            "- Обработка ошибок"
        )
