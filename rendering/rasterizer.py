"""
Модуль растеризации треугольников

Растеризация - это процесс преобразования 3D треугольников в пиксели на экране.

Этот модуль реализует:
1. Алгоритм заполнения треугольников (triangle rasterization)
2. Z-буфер (depth buffer) для правильного отображения глубины
3. Интерполяцию цветов и текстурных координат

Объяснение для начинающих:
- Растеризация = рисование треугольников пиксель за пикселем
- Z-буфер хранит глубину каждого пикселя, чтобы задние объекты
  не рисовались поверх передних
"""

import sys
import os
import math

# Добавляем путь к модулю math
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from math.math_module.vector3 import Vector3
from math.math_module.vector2 import Vector2


class ZBuffer:
    """
    Z-буфер для хранения глубины пикселей
    
    Z-буфер решает проблему: какой пиксель должен быть виден,
    если несколько объектов находятся на одной позиции экрана?
    Ответ: тот, который ближе к камере (меньше Z).
    """
    
    def __init__(self, width, height):
        """
        Инициализация Z-буфера
        
        Args:
            width (int): Ширина буфера
            height (int): Высота буфера
        """
        self.width = width
        self.height = height
        # Инициализируем все значения максимальной глубиной (очень далеко)
        self.buffer = [[float('inf') for _ in range(width)] for _ in range(height)]
    
    def clear(self):
        """Очищает Z-буфер (устанавливает все значения в бесконечность)"""
        for y in range(self.height):
            for x in range(self.width):
                self.buffer[y][x] = float('inf')
    
    def test_and_set(self, x, y, z):
        """
        Проверяет, должен ли пиксель быть нарисован, и обновляет Z-буфер
        
        Args:
            x (int): X координата пикселя
            y (int): Y координата пикселя
            z (float): Глубина пикселя
            
        Returns:
            bool: True если пиксель должен быть нарисован (он ближе), False иначе
        """
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        
        # Если новый пиксель ближе (меньше Z), обновляем буфер
        if z < self.buffer[y][x]:
            self.buffer[y][x] = z
            return True
        return False


def edge_function(v0, v1, p):
    """
    Вычисляет функцию ребра (edge function) для точки
    
    Edge function используется для определения, находится ли точка
    внутри треугольника. Если все три edge function имеют одинаковый знак,
    точка внутри треугольника.
    
    Args:
        v0, v1 (Vector2): Две вершины ребра
        p (Vector2): Точка для проверки
        
    Returns:
        float: Значение edge function
        
    Объяснение:
        Edge function = (p.x - v0.x) * (v1.y - v0.y) - (p.y - v0.y) * (v1.x - v0.x)
        Это векторное произведение в 2D.
    """
    return (p.x - v0.x) * (v1.y - v0.y) - (p.y - v0.y) * (v1.x - v0.x)


def rasterize_triangle(v0, v1, v2, color0, color1, color2, 
                       z0, z1, z2, tex_coord0=None, tex_coord1=None, tex_coord2=None,
                       normal0=None, normal1=None, normal2=None,
                       width=800, height=600, zbuffer=None, image=None):
    """
    Растеризует треугольник (рисует его пиксель за пикселем)
    
    Использует алгоритм на основе edge function для определения,
    какие пиксели принадлежат треугольнику.
    
    Args:
        v0, v1, v2 (Vector2): Вершины треугольника в экранных координатах
        color0, color1, color2: Цвета вершин (RGB tuple или Vector3)
        z0, z1, z2 (float): Глубины вершин (для Z-буфера)
        tex_coord0, tex_coord1, tex_coord2 (Vector2, optional): Текстурные координаты
        normal0, normal1, normal2 (Vector3, optional): Нормали вершин
        width, height (int): Размеры экрана
        zbuffer (ZBuffer, optional): Z-буфер для проверки глубины
        image (list, optional): Изображение для рисования (2D список RGB пикселей)
        
    Returns:
        int: Количество нарисованных пикселей
        
    Объяснение алгоритма:
        1. Находим ограничивающий прямоугольник треугольника
        2. Для каждого пикселя в прямоугольнике:
           - Проверяем, находится ли он внутри треугольника (edge function)
           - Если да, вычисляем интерполированные значения (цвет, глубина, текстура)
           - Проверяем Z-буфер
           - Рисуем пиксель
    """
    if image is None:
        return 0
    
    # Находим ограничивающий прямоугольник (bounding box)
    min_x = max(0, int(min(v0.x, v1.x, v2.x)))
    max_x = min(width - 1, int(max(v0.x, v1.x, v2.x)))
    min_y = max(0, int(min(v0.y, v1.y, v2.y)))
    max_y = min(height - 1, int(max(v0.y, v1.y, v2.y)))
    
    if min_x > max_x or min_y > max_y:
        return 0
    
    # Вычисляем площадь треугольника (для барицентрических координат)
    area = edge_function(v0, v1, v2)
    if abs(area) < 1e-6:
        return 0  # Вырожденный треугольник
    
    pixels_drawn = 0
    
    # Проходим по всем пикселям в bounding box
    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            p = Vector2(x + 0.5, y + 0.5)  # Центр пикселя
            
            # Вычисляем edge functions для всех трех ребер
            w0 = edge_function(v1, v2, p)  # Против вершины v0
            w1 = edge_function(v2, v0, p)   # Против вершины v1
            w2 = edge_function(v0, v1, p)   # Против вершины v2
            
            # Проверяем, находится ли точка внутри треугольника
            # Все edge functions должны иметь одинаковый знак
            if (w0 >= 0 and w1 >= 0 and w2 >= 0) or (w0 <= 0 and w1 <= 0 and w2 <= 0):
                # Вычисляем барицентрические координаты
                inv_area = 1.0 / area
                b0 = w0 * inv_area
                b1 = w1 * inv_area
                b2 = w2 * inv_area
                
                # Интерполируем глубину
                z = b0 * z0 + b1 * z1 + b2 * z2
                
                # Проверяем Z-буфер
                if zbuffer is None or zbuffer.test_and_set(x, y, z):
                    # Интерполируем цвет
                    if isinstance(color0, (tuple, list)) and len(color0) >= 3:
                        r = b0 * color0[0] + b1 * color1[0] + b2 * color2[0]
                        g = b0 * color0[1] + b1 * color1[1] + b2 * color2[1]
                        b = b0 * color0[2] + b1 * color1[2] + b2 * color2[2]
                    else:
                        # Если цвет - Vector3
                        r = b0 * color0.x + b1 * color1.x + b2 * color2.x
                        g = b0 * color0.y + b1 * color1.y + b2 * color2.y
                        b = b0 * color0.z + b1 * color1.z + b2 * color2.z
                    
                    # Ограничиваем значения цвета [0, 255]
                    r = max(0, min(255, int(r)))
                    g = max(0, min(255, int(g)))
                    b = max(0, min(255, int(b)))
                    
                    # Рисуем пиксель
                    image[y][x] = (r, g, b)
                    pixels_drawn += 1
    
    return pixels_drawn


def rasterize_triangle_wireframe(v0, v1, v2, color, width=800, height=600, image=None):
    """
    Рисует контур треугольника (полигональную сетку)
    
    Args:
        v0, v1, v2 (Vector2): Вершины треугольника
        color (tuple): Цвет линий (R, G, B)
        width, height (int): Размеры экрана
        image (list): Изображение для рисования
        
    Returns:
        int: Количество нарисованных пикселей
    """
    if image is None:
        return 0
    
    pixels_drawn = 0
    
    # Рисуем три ребра треугольника
    edges = [(v0, v1), (v1, v2), (v2, v0)]
    
    for v_start, v_end in edges:
        # Используем алгоритм Брезенхема для рисования линии
        x0, y0 = int(v_start.x), int(v_start.y)
        x1, y1 = int(v_end.x), int(v_end.y)
        
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        
        x, y = x0, y0
        
        while True:
            if 0 <= x < width and 0 <= y < height:
                image[y][x] = color
                pixels_drawn += 1
            
            if x == x1 and y == y1:
                break
            
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy
    
    return pixels_drawn
