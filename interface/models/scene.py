"""
Scene - класс для управления сценой с несколькими 3D моделями

Этот класс управляет коллекцией моделей, позволяет выбирать активную модель,
применять к ней трансформации (перемещение, вращение, масштабирование) и
управлять их отображением.
"""

import sys
import os

# Добавляем путь к модулю math
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from math.math_module.vector3 import Vector3
from .model import Model


class Scene:
    """
    Класс для управления сценой с несколькими моделями
    
    Основные возможности:
    - Хранение нескольких моделей
    - Выбор активной модели
    - Применение трансформаций к выбранной модели
    - Добавление и удаление моделей
    - Получение информации о сцене
    """
    
    def __init__(self):
        """Инициализация сцены"""
        self.models = []  # Список всех моделей
        self.selected_model_index = -1  # Индекс выбранной модели (-1 = нет выбора)
    
    def add_model(self, model):
        """
        Добавляет модель в сцену
        
        Args:
            model (Model): Модель для добавления
            
        Returns:
            int: Индекс добавленной модели
        """
        if not isinstance(model, Model):
            raise TypeError("Модель должна быть экземпляром класса Model")
        
        self.models.append(model)
        # Автоматически выбираем новую модель, если ничего не выбрано
        if self.selected_model_index == -1:
            self.selected_model_index = len(self.models) - 1
        
        return len(self.models) - 1
    
    def remove_model(self, index):
        """
        Удаляет модель из сцены по индексу
        
        Args:
            index (int): Индекс модели для удаления
            
        Returns:
            bool: True если модель удалена, False если индекс неверен
        """
        if 0 <= index < len(self.models):
            self.models.pop(index)
            
            # Обновляем индекс выбранной модели
            if self.selected_model_index == index:
                # Если удалили выбранную модель
                if len(self.models) > 0:
                    # Выбираем предыдущую или первую
                    self.selected_model_index = min(index, len(self.models) - 1)
                else:
                    self.selected_model_index = -1
            elif self.selected_model_index > index:
                # Сдвигаем индекс, если удалили модель перед выбранной
                self.selected_model_index -= 1
            
            return True
        return False
    
    def get_model(self, index):
        """
        Получает модель по индексу
        
        Args:
            index (int): Индекс модели
            
        Returns:
            Model или None: Модель или None если индекс неверен
        """
        if 0 <= index < len(self.models):
            return self.models[index]
        return None
    
    def get_selected_model(self):
        """
        Получает выбранную модель
        
        Returns:
            Model или None: Выбранная модель или None если ничего не выбрано
        """
        if 0 <= self.selected_model_index < len(self.models):
            return self.models[self.selected_model_index]
        return None
    
    def select_model(self, index):
        """
        Выбирает модель по индексу
        
        Args:
            index (int): Индекс модели для выбора
            
        Returns:
            bool: True если модель выбрана, False если индекс неверен
        """
        if 0 <= index < len(self.models):
            self.selected_model_index = index
            return True
        return False
    
    def get_selected_index(self):
        """Возвращает индекс выбранной модели"""
        return self.selected_model_index
    
    def get_model_count(self):
        """Возвращает количество моделей в сцене"""
        return len(self.models)
    
    def clear(self):
        """Очищает сцену (удаляет все модели)"""
        self.models = []
        self.selected_model_index = -1
    
    def get_all_models(self):
        """Возвращает список всех моделей"""
        return list(self.models)
    
    def get_model_names(self):
        """Возвращает список имен всех моделей"""
        return [model.name for model in self.models]
    
    def move_selected_model(self, translation):
        """
        Перемещает выбранную модель
        
        Args:
            translation (Vector3): Вектор перемещения
        """
        model = self.get_selected_model()
        if model:
            if not isinstance(translation, Vector3):
                translation = Vector3(translation[0], translation[1], translation[2])
            model.transform.translation = model.transform.translation + translation
    
    def rotate_selected_model(self, rotation):
        """
        Вращает выбранную модель
        
        Args:
            rotation (Vector3): Углы вращения (в радианах или градусах)
        """
        model = self.get_selected_model()
        if model:
            if not isinstance(rotation, Vector3):
                rotation = Vector3(rotation[0], rotation[1], rotation[2])
            model.transform.rotation = model.transform.rotation + rotation
    
    def scale_selected_model(self, scale):
        """
        Масштабирует выбранную модель
        
        Args:
            scale (Vector3 или float): Масштаб (Vector3 для разных осей или float для равномерного)
        """
        model = self.get_selected_model()
        if model:
            if isinstance(scale, (int, float)):
                scale = Vector3(scale, scale, scale)
            elif not isinstance(scale, Vector3):
                scale = Vector3(scale[0], scale[1], scale[2])
            model.transform.scale = Vector3(
                model.transform.scale.x * scale.x,
                model.transform.scale.y * scale.y,
                model.transform.scale.z * scale.z
            )
    
    def reset_selected_model_transform(self):
        """Сбрасывает трансформации выбранной модели"""
        model = self.get_selected_model()
        if model:
            model.transform.reset()
    
    def get_bounding_box(self):
        """
        Вычисляет общий ограничивающий прямоугольник всех моделей
        
        Returns:
            tuple: ((min_x, min_y, min_z), (max_x, max_y, max_z))
        """
        if not self.models:
            return ((0, 0, 0), (0, 0, 0))
        
        all_mins = []
        all_maxs = []
        
        for model in self.models:
            bbox_min, bbox_max = model.get_bounding_box()
            all_mins.append(bbox_min)
            all_maxs.append(bbox_max)
        
        min_x = min(m[0] for m in all_mins)
        min_y = min(m[1] for m in all_mins)
        min_z = min(m[2] for m in all_mins)
        
        max_x = max(m[0] for m in all_maxs)
        max_y = max(m[1] for m in all_maxs)
        max_z = max(m[2] for m in all_maxs)
        
        return ((min_x, min_y, min_z), (max_x, max_y, max_z))
    
    def __str__(self):
        return f"Scene(models={len(self.models)}, selected={self.selected_model_index})"
    
    def __repr__(self):
        return self.__str__()
