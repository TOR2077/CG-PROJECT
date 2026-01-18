"""
Модуль для триангуляции полигонов и вычисления нормалей

Этот модуль предоставляет функции для:
1. Триангуляции многоугольников (разбиение на треугольники)
2. Вычисления нормалей для вершин и граней
3. Сглаживания нормалей (smooth normals)

Объяснение для начинающих:
- Триангуляция - это разбиение многоугольника на треугольники, 
  потому что графические карты умеют рисовать только треугольники
- Нормаль - это вектор, перпендикулярный поверхности, 
  нужен для правильного освещения
- Сглаживание нормалей - усреднение нормалей соседних граней 
  для плавного перехода света
"""

import sys
import os

# Добавляем путь к модулю math
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from math.math_module.vector3 import Vector3


def triangulate_face(face_vertices):
    """
    Триангулирует многоугольник (разбивает на треугольники)
    
    Использует простой метод "веер" (fan triangulation):
    - Берем первую вершину как центр
    - Создаем треугольники: (0, i, i+1) для всех i
    
    Args:
        face_vertices (list): Список индексов вершин грани
        
    Returns:
        list: Список треугольников, каждый треугольник - список из 3 индексов
        
    Пример:
        >>> triangulate_face([0, 1, 2, 3])
        [[0, 1, 2], [0, 2, 3]]
    """
    if len(face_vertices) < 3:
        return []
    
    # Если уже треугольник, возвращаем как есть
    if len(face_vertices) == 3:
        return [face_vertices]
    
    # Триангуляция методом "веер"
    triangles = []
    first_vertex = face_vertices[0]
    
    # Создаем треугольники: (первая_вершина, i, i+1)
    for i in range(1, len(face_vertices) - 1):
        triangle = [first_vertex, face_vertices[i], face_vertices[i + 1]]
        triangles.append(triangle)
    
    return triangles


def compute_face_normal(vertex1, vertex2, vertex3):
    """
    Вычисляет нормаль грани (треугольника)
    
    Нормаль вычисляется как векторное произведение двух сторон треугольника.
    Векторное произведение дает вектор, перпендикулярный плоскости треугольника.
    
    Args:
        vertex1, vertex2, vertex3 (Vector3): Вершины треугольника
        
    Returns:
        Vector3: Нормализованная нормаль грани
        
    Объяснение:
        - Берем две стороны треугольника: v2-v1 и v3-v1
        - Вычисляем векторное произведение этих сторон
        - Нормализуем результат (делаем длину = 1)
    """
    # Вычисляем две стороны треугольника
    edge1 = vertex2 - vertex1
    edge2 = vertex3 - vertex1
    
    # Векторное произведение дает нормаль
    normal = edge1.vectormul(edge2)
    
    # Нормализуем (делаем длину = 1)
    normalized = normal.normalize()
    
    return normalized


def compute_vertex_normals(vertices, faces, face_normals=None):
    """
    Вычисляет нормали для вершин модели
    
    Для каждой вершины усредняет нормали всех граней, которые её содержат.
    Это называется "сглаживание нормалей" (smooth normals).
    
    Args:
        vertices (list): Список вершин (Vector3)
        faces (list): Список граней (списки индексов вершин)
        face_normals (list, optional): Предвычисленные нормали граней
        
    Returns:
        list: Список нормалей вершин (Vector3)
        
    Объяснение:
        1. Для каждой грани вычисляем нормаль
        2. Для каждой вершины находим все грани, которые её содержат
        3. Усредняем нормали этих граней
        4. Нормализуем результат
    """
    if not vertices or not faces:
        return []
    
    # Вычисляем нормали граней, если не предоставлены
    if face_normals is None:
        face_normals = []
        for face in faces:
            if len(face) >= 3:
                # Триангулируем грань
                triangles = triangulate_face(face)
                for triangle in triangles:
                    if len(triangle) == 3:
                        v1 = vertices[triangle[0]]
                        v2 = vertices[triangle[1]]
                        v3 = vertices[triangle[2]]
                        normal = compute_face_normal(v1, v2, v3)
                        face_normals.append(normal)
    
    # Инициализируем нормали вершин нулевыми векторами
    vertex_normals = [Vector3(0, 0, 0) for _ in vertices]
    
    # Для каждой грани добавляем её нормаль к нормалям её вершин
    face_idx = 0
    for face in faces:
        triangles = triangulate_face(face)
        for triangle in triangles:
            if len(triangle) == 3 and face_idx < len(face_normals):
                normal = face_normals[face_idx]
                # Добавляем нормаль грани к нормалям всех вершин треугольника
                for vertex_idx in triangle:
                    if 0 <= vertex_idx < len(vertex_normals):
                        vertex_normals[vertex_idx] = vertex_normals[vertex_idx] + normal
                face_idx += 1
    
    # Нормализуем все нормали вершин
    normalized_normals = []
    for normal in vertex_normals:
        normalized = normal.normalize()
        # Если нормаль нулевая (вершина не используется), используем (0, 0, 1)
        if normalized.length() < 1e-6:
            normalized = Vector3(0, 0, 1)
        normalized_normals.append(normalized)
    
    return normalized_normals


def triangulate_model(model):
    """
    Триангулирует всю модель (разбивает все грани на треугольники)
    
    Args:
        model (Model): Модель для триангуляции
        
    Returns:
        list: Список треугольников, каждый треугольник - список из 3 индексов вершин
    """
    triangles = []
    
    for face in model.faces:
        # Триангулируем каждую грань
        face_triangles = triangulate_face(face)
        triangles.extend(face_triangles)
    
    return triangles


def prepare_model_for_rendering(model, recalculate_normals=True):
    """
    Подготавливает модель для рендеринга
    
    Выполняет:
    1. Триангуляцию всех граней
    2. Вычисление нормалей (если нужно пересчитать)
    
    Args:
        model (Model): Модель для подготовки
        recalculate_normals (bool): Пересчитывать ли нормали (даже если они есть в файле)
        
    Returns:
        tuple: (triangles, vertex_normals)
            - triangles: список треугольников (списки из 3 индексов)
            - vertex_normals: список нормалей вершин (Vector3)
            
    Объяснение:
        Эта функция вызывается после загрузки модели, чтобы подготовить
        её данные для быстрого рендеринга. Все грани разбиваются на треугольники,
        и вычисляются нормали для правильного освещения.
    """
    # Триангулируем модель
    triangles = triangulate_model(model)
    
    # Вычисляем нормали
    vertex_normals = []
    if recalculate_normals or not model.normals or len(model.normals) != len(model.vertices):
        # Пересчитываем нормали
        vertex_normals = compute_vertex_normals(model.vertices, model.faces)
    else:
        # Используем существующие нормали, но проверяем их
        vertex_normals = []
        for i, normal in enumerate(model.normals):
            if isinstance(normal, Vector3):
                normalized = normal.normalize()
                if normalized.length() < 1e-6:
                    normalized = Vector3(0, 0, 1)
                vertex_normals.append(normalized)
            else:
                # Если нормаль не Vector3, создаем дефолтную
                vertex_normals.append(Vector3(0, 0, 1))
        
        # Если нормалей меньше чем вершин, дополняем
        while len(vertex_normals) < len(model.vertices):
            vertex_normals.append(Vector3(0, 0, 1))
    
    return triangles, vertex_normals
