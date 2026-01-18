"""
ObjWriter - класс для сохранения 3D моделей в файлы формата .obj

Этот класс предоставляет функциональность для записи геометрических данных
в файлы Wavefront OBJ. Он сохраняет вершины, нормали, текстурные координаты
и грани в стандартном формате OBJ.
"""

import os
import sys

# Добавляем путь к модулю math
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from math.math_module.vector3 import Vector3


class ObjWriter:
    """
    Класс для записи файлов формата .obj
    
    Основные возможности:
    - Сохранение вершин (v)
    - Сохранение нормалей (vn)
    - Сохранение текстурных координат (vt)
    - Сохранение граней/полигонов (f)
    - Автоматическая конвертация индексов в 1-based формат
    """
    
    def __init__(self):
        """Инициализация ObjWriter"""
        pass
    
    def write(self, filepath, vertices, faces, normals=None, tex_coords=None, model_name="Model"):
        """
        Записывает модель в файл .obj
        
        Args:
            filepath (str): Путь к выходному файлу .obj
            vertices (list): Список вершин (Vector3 или кортежи (x, y, z))
            faces (list): Список граней (списки индексов вершин, 0-based)
            normals (list, optional): Список нормалей (Vector3 или кортежи)
            tex_coords (list, optional): Список текстурных координат
            model_name (str): Имя модели для комментария в файле
            
        Raises:
            ValueError: Если данные неверны
            IOError: Если произошла ошибка записи файла
        """
        if not filepath.lower().endswith('.obj'):
            raise ValueError(f"Файл должен иметь расширение .obj: {filepath}")
        
        if not vertices:
            raise ValueError("Список вершин не может быть пустым")
        
        if not faces:
            raise ValueError("Список граней не может быть пустым")
        
        # Создаем директорию, если её нет
        directory = os.path.dirname(filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as file:
                # Записываем заголовок
                file.write(f"# OBJ файл: {model_name}\n")
                file.write(f"# Вершин: {len(vertices)}\n")
                file.write(f"# Граней: {len(faces)}\n")
                file.write("\n")
                
                # Записываем вершины
                file.write("# Вершины\n")
                for vertex in vertices:
                    if isinstance(vertex, Vector3):
                        file.write(f"v {vertex.x} {vertex.y} {vertex.z}\n")
                    else:
                        # Предполагаем кортеж или список
                        file.write(f"v {vertex[0]} {vertex[1]} {vertex[2]}\n")
                
                file.write("\n")
                
                # Записываем текстурные координаты, если есть
                if tex_coords:
                    file.write("# Текстурные координаты\n")
                    for tex_coord in tex_coords:
                        if isinstance(tex_coord, (tuple, list)):
                            if len(tex_coord) >= 2:
                                file.write(f"vt {tex_coord[0]} {tex_coord[1]}")
                                if len(tex_coord) >= 3:
                                    file.write(f" {tex_coord[2]}")
                                file.write("\n")
                    file.write("\n")
                
                # Записываем нормали, если есть
                if normals:
                    file.write("# Нормали\n")
                    for normal in normals:
                        if isinstance(normal, Vector3):
                            file.write(f"vn {normal.x} {normal.y} {normal.z}\n")
                        else:
                            # Предполагаем кортеж или список
                            file.write(f"vn {normal[0]} {normal[1]} {normal[2]}\n")
                    file.write("\n")
                
                # Записываем грани
                file.write("# Грани\n")
                for face in faces:
                    if not face:
                        continue
                    
                    # Конвертируем 0-based индексы в 1-based для OBJ формата
                    face_str = "f"
                    for idx in face:
                        if idx < 0 or idx >= len(vertices):
                            raise ValueError(
                                f"Индекс вершины {idx} вне диапазона "
                                f"[0, {len(vertices) - 1}]"
                            )
                        # OBJ использует 1-based индексацию
                        face_str += f" {idx + 1}"
                    
                    file.write(face_str + "\n")
        
        except Exception as e:
            if isinstance(e, ValueError):
                raise
            raise IOError(f"Ошибка записи файла {filepath}: {str(e)}")
    
    def write_model(self, filepath, model):
        """
        Записывает объект Model в файл .obj
        
        Args:
            filepath (str): Путь к выходному файлу .obj
            model: Объект Model с атрибутами vertices, faces, normals, tex_coords
            
        Raises:
            ValueError: Если модель неверна
            IOError: Если произошла ошибка записи файла
        """
        if not hasattr(model, 'vertices') or not hasattr(model, 'faces'):
            raise ValueError("Модель должна иметь атрибуты vertices и faces")
        
        model_name = getattr(model, 'name', 'Model')
        normals = getattr(model, 'normals', None)
        tex_coords = getattr(model, 'tex_coords', None)
        
        self.write(filepath, model.vertices, model.faces, normals, tex_coords, model_name)
