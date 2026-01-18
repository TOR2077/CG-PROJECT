"""
ObjReader - класс для чтения 3D моделей из файлов формата .obj

Этот класс предоставляет функциональность для загрузки геометрических данных
из файлов Wavefront OBJ. Он обрабатывает вершины (v), нормали (vn), текстуры (vt)
и грани (f), поддерживая различные форматы индексации.
"""

import sys
import os
from pathlib import Path

# Добавляем путь к модулю math
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from math.math_module.vector3 import Vector3


class ObjReader:
    """
    Класс для чтения файлов формата .obj
    
    Основные возможности:
    - Загрузка вершин (v)
    - Загрузка нормалей (vn)
    - Загрузка текстурных координат (vt)
    - Загрузка граней/полигонов (f)
    - Обработка различных форматов индексации (1-based, отрицательные индексы)
    - Валидация данных и выброс исключений при ошибках
    """
    
    def __init__(self):
        """Инициализация ObjReader"""
        self.vertices = []  # Список вершин (Vector3)
        self.normals = []   # Список нормалей (Vector3)
        self.tex_coords = []  # Список текстурных координат (Vector2 или Vector3)
        self.faces = []     # Список граней (списки индексов)
    
    def read(self, filepath):
        """
        Читает файл .obj и загружает данные модели
        
        Args:
            filepath (str): Путь к файлу .obj
            
        Returns:
            tuple: (vertices, faces, normals, tex_coords)
            
        Raises:
            FileNotFoundError: Если файл не найден
            ValueError: Если файл имеет неверный формат или поврежден
            IOError: Если произошла ошибка чтения файла
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Файл не найден: {filepath}")
        
        if not filepath.lower().endswith('.obj'):
            raise ValueError(f"Файл должен иметь расширение .obj: {filepath}")
        
        # Очищаем предыдущие данные
        self.vertices = []
        self.normals = []
        self.tex_coords = []
        self.faces = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                line_number = 0
                for line in file:
                    line_number += 1
                    line = line.strip()
                    
                    # Пропускаем пустые строки и комментарии
                    if not line or line.startswith('#'):
                        continue
                    
                    parts = line.split()
                    if not parts:
                        continue
                    
                    command = parts[0].lower()
                    
                    try:
                        if command == 'v':  # Вершина
                            self._parse_vertex(parts, line_number)
                        elif command == 'vn':  # Нормаль
                            self._parse_normal(parts, line_number)
                        elif command == 'vt':  # Текстурная координата
                            self._parse_tex_coord(parts, line_number)
                        elif command == 'f':  # Грань
                            self._parse_face(parts, line_number)
                    except Exception as e:
                        raise ValueError(
                            f"Ошибка на строке {line_number}: {str(e)}\n"
                            f"Строка: {line}"
                        )
        
        except UnicodeDecodeError:
            # Пробуем другие кодировки
            try:
                with open(filepath, 'r', encoding='cp1251') as file:
                    self._read_content(file)
            except Exception as e:
                raise IOError(f"Ошибка чтения файла {filepath}: {str(e)}")
        except Exception as e:
            if isinstance(e, (FileNotFoundError, ValueError)):
                raise
            raise IOError(f"Ошибка чтения файла {filepath}: {str(e)}")
        
        # Валидация данных
        if len(self.vertices) == 0:
            raise ValueError("Файл не содержит вершин")
        
        if len(self.faces) == 0:
            raise ValueError("Файл не содержит граней")
        
        return self.vertices, self.faces, self.normals, self.tex_coords
    
    def _read_content(self, file):
        """Вспомогательный метод для чтения содержимого файла"""
        line_number = 0
        for line in file:
            line_number += 1
            line = line.strip()
            
            if not line or line.startswith('#'):
                continue
            
            parts = line.split()
            if not parts:
                continue
            
            command = parts[0].lower()
            
            if command == 'v':
                self._parse_vertex(parts, line_number)
            elif command == 'vn':
                self._parse_normal(parts, line_number)
            elif command == 'vt':
                self._parse_tex_coord(parts, line_number)
            elif command == 'f':
                self._parse_face(parts, line_number)
    
    def _parse_vertex(self, parts, line_number):
        """Парсит строку вершины (v x y z [w])"""
        if len(parts) < 4:
            raise ValueError("Вершина должна содержать минимум 3 координаты (x y z)")
        
        try:
            x = float(parts[1])
            y = float(parts[2])
            z = float(parts[3])
            self.vertices.append(Vector3(x, y, z))
        except ValueError as e:
            raise ValueError(f"Неверный формат координат вершины: {str(e)}")
    
    def _parse_normal(self, parts, line_number):
        """Парсит строку нормали (vn x y z)"""
        if len(parts) < 4:
            raise ValueError("Нормаль должна содержать 3 координаты (x y z)")
        
        try:
            x = float(parts[1])
            y = float(parts[2])
            z = float(parts[3])
            self.normals.append(Vector3(x, y, z))
        except ValueError as e:
            raise ValueError(f"Неверный формат координат нормали: {str(e)}")
    
    def _parse_tex_coord(self, parts, line_number):
        """Парсит строку текстурной координаты (vt u [v] [w])"""
        if len(parts) < 2:
            raise ValueError("Текстурная координата должна содержать минимум 1 значение")
        
        try:
            u = float(parts[1])
            v = float(parts[2]) if len(parts) > 2 else 0.0
            w = float(parts[3]) if len(parts) > 3 else 0.0
            self.tex_coords.append((u, v, w))
        except ValueError as e:
            raise ValueError(f"Неверный формат текстурной координаты: {str(e)}")
    
    def _parse_face(self, parts, line_number):
        """Парсит строку грани (f v1/vt1/vn1 v2/vt2/vn2 ...)"""
        if len(parts) < 4:
            raise ValueError("Грань должна содержать минимум 3 вершины")
        
        face_indices = []
        
        for i in range(1, len(parts)):
            vertex_data = parts[i].split('/')
            
            # Получаем индекс вершины (обязательный)
            try:
                vertex_idx = int(vertex_data[0])
                # OBJ использует 1-based индексацию, конвертируем в 0-based
                if vertex_idx > 0:
                    vertex_idx -= 1
                elif vertex_idx < 0:
                    # Отрицательные индексы считаются с конца
                    vertex_idx = len(self.vertices) + vertex_idx
                else:
                    raise ValueError("Индекс вершины не может быть 0")
                
                # Проверяем валидность индекса
                if vertex_idx < 0 or vertex_idx >= len(self.vertices):
                    raise ValueError(
                        f"Индекс вершины {vertex_idx} вне диапазона "
                        f"[0, {len(self.vertices) - 1}]"
                    )
                
                face_indices.append(vertex_idx)
            
            except ValueError as e:
                raise ValueError(f"Неверный формат индекса вершины: {str(e)}")
        
        if len(face_indices) < 3:
            raise ValueError("Грань должна содержать минимум 3 вершины")
        
        self.faces.append(face_indices)
    
    def get_vertices(self):
        """Возвращает список вершин"""
        return self.vertices
    
    def get_faces(self):
        """Возвращает список граней"""
        return self.faces
    
    def get_normals(self):
        """Возвращает список нормалей"""
        return self.normals
    
    def get_tex_coords(self):
        """Возвращает список текстурных координат"""
        return self.tex_coords
