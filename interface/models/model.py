"""
Model - класс для представления 3D модели

Этот класс хранит геометрические данные модели (вершины, грани, нормали)
и предоставляет методы для их модификации, включая удаление вершин и полигонов.
"""

import sys
import os

# Добавляем путь к модулю math
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from math.math_module.vector3 import Vector3
from math.transforms.affinetransform import AffineTransform


class Model:
    """
    Класс для представления 3D модели
    
    Хранит:
    - vertices: список вершин (Vector3)
    - faces: список граней (списки индексов вершин)
    - normals: список нормалей (Vector3, опционально)
    - tex_coords: список текстурных координат (опционально)
    - transform: аффинные преобразования (AffineTransform)
    - name: имя модели
    
    Методы:
    - Удаление вершин и полигонов
    - Получение трансформированных вершин
    - Валидация данных
    """
    
    def __init__(self, vertices=None, faces=None, normals=None, tex_coords=None, name="Model"):
        """
        Инициализация модели
        
        Args:
            vertices (list): Список вершин (Vector3)
            faces (list): Список граней (списки индексов)
            normals (list): Список нормалей (Vector3, опционально)
            tex_coords (list): Список текстурных координат (опционально)
            name (str): Имя модели
        """
        self.vertices = vertices if vertices is not None else []
        self.faces = faces if faces is not None else []
        self.normals = normals if normals is not None else []
        self.tex_coords = tex_coords if tex_coords is not None else []
        self.name = name
        self.transform = AffineTransform()
        self._original_vertices = list(self.vertices)  # Сохраняем оригинальные вершины
    
    def get_transformed_vertices(self):
        """
        Возвращает вершины после применения трансформаций
        
        Returns:
            list: Список трансформированных вершин (Vector3)
        """
        return self.transform.transform_vertices(self.vertices)
    
    def get_original_vertices(self):
        """Возвращает оригинальные вершины без трансформаций"""
        return self._original_vertices
    
    def delete_vertices(self, vertex_indices):
        """
        Удаляет вершины по индексам и обновляет грани
        
        Args:
            vertex_indices (set или list): Индексы вершин для удаления
            
        Returns:
            int: Количество удаленных вершин
        """
        if not vertex_indices:
            return 0
        
        # Преобразуем в множество для быстрого поиска
        indices_to_delete = set(vertex_indices)
        
        # Проверяем валидность индексов
        valid_indices = {i for i in indices_to_delete if 0 <= i < len(self.vertices)}
        if not valid_indices:
            return 0
        
        # Создаем новую карту индексов (старый индекс -> новый индекс)
        new_index_map = {}
        new_vertex_index = 0
        
        for old_index in range(len(self.vertices)):
            if old_index not in valid_indices:
                new_index_map[old_index] = new_vertex_index
                new_vertex_index += 1
        
        # Удаляем вершины
        self.vertices = [
            v for i, v in enumerate(self.vertices) 
            if i not in valid_indices
        ]
        
        # Обновляем оригинальные вершины
        self._original_vertices = [
            v for i, v in enumerate(self._original_vertices) 
            if i not in valid_indices
        ]
        
        # Обновляем нормали, если они есть
        if self.normals and len(self.normals) == len(self._original_vertices) + len(valid_indices):
            self.normals = [
                n for i, n in enumerate(self.normals) 
                if i not in valid_indices
            ]
        
        # Обновляем текстурные координаты, если они есть
        if self.tex_coords and len(self.tex_coords) == len(self._original_vertices) + len(valid_indices):
            self.tex_coords = [
                t for i, t in enumerate(self.tex_coords) 
                if i not in valid_indices
            ]
        
        # Обновляем грани: переиндексируем и удаляем грани с удаленными вершинами
        new_faces = []
        for face in self.faces:
            new_face = []
            face_valid = True
            
            for vertex_idx in face:
                if vertex_idx in valid_indices:
                    # Грань содержит удаленную вершину - пропускаем её
                    face_valid = False
                    break
                elif vertex_idx in new_index_map:
                    # Обновляем индекс
                    new_face.append(new_index_map[vertex_idx])
                else:
                    # Индекс не найден (не должен случиться)
                    face_valid = False
                    break
            
            if face_valid and len(new_face) >= 3:
                new_faces.append(new_face)
        
        self.faces = new_faces
        
        return len(valid_indices)
    
    def delete_faces(self, face_indices):
        """
        Удаляет грани по индексам
        
        Args:
            face_indices (set или list): Индексы граней для удаления
            
        Returns:
            int: Количество удаленных граней
        """
        if not face_indices:
            return 0
        
        indices_to_delete = set(face_indices)
        valid_indices = {i for i in indices_to_delete if 0 <= i < len(self.faces)}
        
        if not valid_indices:
            return 0
        
        # Удаляем грани
        self.faces = [
            f for i, f in enumerate(self.faces) 
            if i not in valid_indices
        ]
        
        return len(valid_indices)
    
    def delete_polygons(self, face_indices):
        """
        Алиас для delete_faces (удобство использования)
        
        Args:
            face_indices (set или list): Индексы полигонов для удаления
            
        Returns:
            int: Количество удаленных полигонов
        """
        return self.delete_faces(face_indices)
    
    def get_vertex_count(self):
        """Возвращает количество вершин"""
        return len(self.vertices)
    
    def get_face_count(self):
        """Возвращает количество граней"""
        return len(self.faces)
    
    def get_bounding_box(self):
        """
        Вычисляет ограничивающий прямоугольник модели
        
        Returns:
            tuple: ((min_x, min_y, min_z), (max_x, max_y, max_z))
        """
        if not self.vertices:
            return ((0, 0, 0), (0, 0, 0))
        
        transformed_vertices = self.get_transformed_vertices()
        
        min_x = min(v.x for v in transformed_vertices)
        min_y = min(v.y for v in transformed_vertices)
        min_z = min(v.z for v in transformed_vertices)
        
        max_x = max(v.x for v in transformed_vertices)
        max_y = max(v.y for v in transformed_vertices)
        max_z = max(v.z for v in transformed_vertices)
        
        return ((min_x, min_y, min_z), (max_x, max_y, max_z))
    
    def center_model(self):
        """Центрирует модель в начале координат"""
        if not self.vertices:
            return
        
        bbox_min, bbox_max = self.get_bounding_box()
        center_x = (bbox_min[0] + bbox_max[0]) / 2
        center_y = (bbox_min[1] + bbox_max[1]) / 2
        center_z = (bbox_min[2] + bbox_max[2]) / 2
        
        # Смещаем все вершины
        offset = Vector3(-center_x, -center_y, -center_z)
        self.vertices = [Vector3(v.x + offset.x, v.y + offset.y, v.z + offset.z) 
                        for v in self.vertices]
        self._original_vertices = list(self.vertices)
    
    def validate(self):
        """
        Валидирует модель (проверяет корректность данных)
        
        Returns:
            tuple: (is_valid, error_message)
        """
        if not self.vertices:
            return False, "Модель не содержит вершин"
        
        if not self.faces:
            return False, "Модель не содержит граней"
        
        # Проверяем, что все индексы в гранях валидны
        max_vertex_idx = len(self.vertices) - 1
        for i, face in enumerate(self.faces):
            if not face:
                return False, f"Грань {i} пуста"
            if len(face) < 3:
                return False, f"Грань {i} содержит менее 3 вершин"
            for vertex_idx in face:
                if vertex_idx < 0 or vertex_idx > max_vertex_idx:
                    return False, f"Грань {i} содержит неверный индекс вершины: {vertex_idx}"
        
        return True, "Модель валидна"
    
    def __str__(self):
        return f"Model(name='{self.name}', vertices={len(self.vertices)}, faces={len(self.faces)})"
    
    def __repr__(self):
        return self.__str__()
