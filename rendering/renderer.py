"""
Главный модуль рендерера

Этот модуль объединяет все компоненты рендеринга:
- Триангуляцию
- Камеру
- Растеризацию
- Текстуры
- Освещение

Объяснение для начинающих:
Рендерер - это "художник", который рисует 3D модели на экране.
Он берет 3D координаты вершин, преобразует их в 2D координаты экрана,
и рисует треугольники пиксель за пикселем.
"""

import sys
import os
import math

# Добавляем путь к модулю math
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from math.math_module.vector3 import Vector3
from math.math_module.vector2 import Vector2
from math.math_module.vector4 import Vector4
from math.math_module.matrix4x4 import Matrix4x4

from .triangulation import prepare_model_for_rendering
from .camera import Camera
from .rasterizer import ZBuffer, rasterize_triangle, rasterize_triangle_wireframe
from .texture import Texture
from .lighting import Light, phong_lighting


class RenderSettings:
    """
    Настройки рендеринга
    
    Хранит флаги режимов отрисовки:
    - draw_wireframe: рисовать полигональную сетку
    - use_texture: использовать текстуру
    - use_lighting: использовать освещение
    - base_color: базовый цвет модели (если нет текстуры)
    """
    
    def __init__(self):
        self.draw_wireframe = False
        self.use_texture = False
        self.use_lighting = False
        self.base_color = (200, 200, 200)  # Светло-серый по умолчанию


class Renderer:
    """
    Главный класс рендерера
    
    Выполняет полный цикл рендеринга:
    1. Преобразование 3D координат в экранные (через камеру)
    2. Растеризация треугольников
    3. Применение текстур и освещения
    """
    
    def __init__(self, width=800, height=600):
        """
        Инициализация рендерера
        
        Args:
            width (int): Ширина экрана
            height (int): Высота экрана
        """
        self.width = width
        self.height = height
        
        # Создаем Z-буфер
        self.zbuffer = ZBuffer(width, height)
        
        # Создаем изображение для рисования (2D список RGB пикселей)
        self.image = [[(0, 0, 0) for _ in range(width)] for _ in range(height)]
        
        # Настройки рендеринга
        self.settings = RenderSettings()
        
        # Текстура (может быть None)
        self.texture = None
        
        # Источник света
        self.light = Light(position=Vector3(0, 0, 5), color=(1.0, 1.0, 1.0), intensity=1.0)
    
    def set_size(self, width, height):
        """
        Устанавливает размер экрана
        
        Args:
            width (int): Ширина
            height (int): Высота
        """
        self.width = width
        self.height = height
        self.zbuffer = ZBuffer(width, height)
        self.image = [[(0, 0, 0) for _ in range(width)] for _ in range(height)]
    
    def clear(self, color=(0, 0, 0)):
        """
        Очищает экран и Z-буфер
        
        Args:
            color (tuple): Цвет фона (R, G, B)
        """
        # Очищаем изображение
        for y in range(self.height):
            for x in range(self.width):
                self.image[y][x] = color
        
        # Очищаем Z-буфер
        self.zbuffer.clear()
    
    def set_texture(self, texture):
        """
        Устанавливает текстуру для рендеринга
        
        Args:
            texture (Texture): Текстура или None
        """
        self.texture = texture
    
    def set_light(self, light):
        """
        Устанавливает источник света
        
        Args:
            light (Light): Источник света
        """
        self.light = light
    
    def project_point(self, point, view_proj_matrix):
        """
        Проецирует 3D точку на экран
        
        Args:
            point (Vector3): 3D точка
            view_proj_matrix (Matrix4x4): Матрица вида-проекции
            
        Returns:
            tuple: (screen_x, screen_y, depth) или None если точка за камерой
        """
        # Преобразуем точку через матрицу вида-проекции
        transformed = view_proj_matrix * point
        
        # Если точка за камерой (w < 0 или z > far), не рисуем
        # В нашем случае проверяем z координату после проекции
        if abs(transformed.z) > 1.0:  # За пределами видимой области
            return None
        
        # Преобразуем из нормализованных координат устройства (-1..1) в экранные (0..width, 0..height)
        screen_x = (transformed.x + 1.0) * 0.5 * self.width
        screen_y = (1.0 - transformed.y) * 0.5 * self.height  # Инвертируем Y (экран Y идет сверху вниз)
        depth = transformed.z
        
        return (screen_x, screen_y, depth)
    
    def render_model(self, model, camera, triangles=None, vertex_normals=None):
        """
        Рендерит модель
        
        Args:
            model (Model): Модель для рендеринга
            camera (Camera): Камера
            triangles (list, optional): Предвычисленные треугольники
            vertex_normals (list, optional): Предвычисленные нормали вершин
        """
        if not model.vertices or not model.faces:
            return
        
        # Подготавливаем модель (триангуляция и нормали)
        if triangles is None or vertex_normals is None:
            triangles, vertex_normals = prepare_model_for_rendering(model, recalculate_normals=True)
        
        # Получаем матрицу вида-проекции
        view_proj = camera.get_view_projection_matrix()
        
        # Получаем трансформированные вершины
        transformed_vertices = model.get_transformed_vertices()
        
        # Рендерим каждый треугольник
        for triangle in triangles:
            if len(triangle) < 3:
                continue
            
            # Получаем индексы вершин треугольника
            idx0, idx1, idx2 = triangle[0], triangle[1], triangle[2]
            
            if not (0 <= idx0 < len(transformed_vertices) and
                    0 <= idx1 < len(transformed_vertices) and
                    0 <= idx2 < len(transformed_vertices)):
                continue
            
            # Получаем вершины
            v0_3d = transformed_vertices[idx0]
            v1_3d = transformed_vertices[idx1]
            v2_3d = transformed_vertices[idx2]
            
            # Проецируем на экран
            proj0 = self.project_point(v0_3d, view_proj)
            proj1 = self.project_point(v1_3d, view_proj)
            proj2 = self.project_point(v2_3d, view_proj)
            
            if proj0 is None or proj1 is None or proj2 is None:
                continue
            
            screen_x0, screen_y0, z0 = proj0
            screen_x1, screen_y1, z1 = proj1
            screen_x2, screen_y2, z2 = proj2
            
            # Создаем 2D векторы для растеризации
            v0_2d = Vector2(screen_x0, screen_y0)
            v1_2d = Vector2(screen_x1, screen_y1)
            v2_2d = Vector2(screen_x2, screen_y2)
            
            # Если режим полигональной сетки, рисуем только контур
            if self.settings.draw_wireframe:
                wireframe_color = (255, 255, 255)  # Белый цвет для сетки
                rasterize_triangle_wireframe(
                    v0_2d, v1_2d, v2_2d, wireframe_color,
                    self.width, self.height, self.image
                )
                continue
            
            # Получаем нормали вершин
            normal0 = vertex_normals[idx0] if idx0 < len(vertex_normals) else Vector3(0, 0, 1)
            normal1 = vertex_normals[idx1] if idx1 < len(vertex_normals) else Vector3(0, 0, 1)
            normal2 = vertex_normals[idx2] if idx2 < len(vertex_normals) else Vector3(0, 0, 1)
            
            # Вычисляем цвета вершин
            color0, color1, color2 = self.compute_vertex_colors(
                v0_3d, v1_3d, v2_3d,
                normal0, normal1, normal2,
                idx0, idx1, idx2,
                model, camera
            )
            
            # Растеризуем треугольник
            rasterize_triangle(
                v0_2d, v1_2d, v2_2d,
                color0, color1, color2,
                z0, z1, z2,
                None, None, None,  # Текстурные координаты (пока не используем)
                normal0, normal1, normal2,
                self.width, self.height,
                self.zbuffer, self.image
            )
    
    def compute_vertex_colors(self, v0, v1, v2, n0, n1, n2, idx0, idx1, idx2, model, camera):
        """
        Вычисляет цвета вершин треугольника
        
        Учитывает:
        - Базовый цвет
        - Текстуру (если включена)
        - Освещение (если включено)
        """
        colors = []
        
        for i, (vertex, normal, idx) in enumerate([(v0, n0, idx0), (v1, n1, idx1), (v2, n2, idx2)]):
            # Начинаем с базового цвета
            color = self.settings.base_color
            
            # Применяем текстуру, если включена
            if self.settings.use_texture and self.texture and self.texture.is_loaded():
                if model.tex_coords and idx < len(model.tex_coords):
                    tex_coord = model.tex_coords[idx]
                    if isinstance(tex_coord, (tuple, list)) and len(tex_coord) >= 2:
                        u, v = tex_coord[0], tex_coord[1]
                        tex_color = self.texture.sample_bilinear(u, v)
                        # Смешиваем базовый цвет с текстурой
                        color = (
                            int(color[0] * tex_color[0] / 255.0),
                            int(color[1] * tex_color[1] / 255.0),
                            int(color[2] * tex_color[2] / 255.0)
                        )
            
            # Применяем освещение, если включено
            if self.settings.use_lighting:
                # Направление от вершины к источнику света
                light_dir = self.light.position - vertex
                light_dir = light_dir.normalize()
                
                # Направление от вершины к камере
                view_dir = camera.position - vertex
                view_dir = view_dir.normalize()
                
                # Вычисляем освещение
                lit_color = phong_lighting(
                    normal, view_dir, light_dir, self.light.color,
                    ambient_color=(0.1, 0.1, 0.1),
                    diffuse_color=(0.8, 0.8, 0.8),
                    specular_color=(1.0, 1.0, 1.0),
                    shininess=32.0
                )
                
                # Смешиваем цвет с освещением
                if self.settings.use_texture and self.texture:
                    # Если есть текстура, умножаем освещение на цвет текстуры
                    color = (
                        int(lit_color[0] * color[0] / 255.0),
                        int(lit_color[1] * color[1] / 255.0),
                        int(lit_color[2] * color[2] / 255.0)
                    )
                else:
                    # Если нет текстуры, используем освещение напрямую
                    color = lit_color
            
            colors.append(color)
        
        return tuple(colors)
    
    def get_image(self):
        """
        Возвращает текущее изображение
        
        Returns:
            list: 2D список RGB пикселей (image[y][x] = (r, g, b))
        """
        return self.image
