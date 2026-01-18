"""
Модуль для освещения 3D моделей

Освещение делает 3D объекты объемными и реалистичными.
Этот модуль реализует простую модель освещения Фонга.

Объяснение для начинающих:
Освещение состоит из трех компонентов:
1. Ambient (окружающее) - базовый свет везде
2. Diffuse (рассеянное) - свет, отраженный от поверхности
3. Specular (зеркальное) - блики на блестящих поверхностях

Вектор нормали показывает, в какую сторону "смотрит" поверхность.
Чем больше угол между нормалью и направлением света, тем темнее поверхность.
"""

import sys
import os
import math as math_std

# Добавляем путь к модулю math
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from math.math_module.vector3 import Vector3


class Light:
    """
    Класс для представления источника света
    
    Источник света имеет:
    - Позицию (или направление)
    - Цвет
    - Интенсивность
    """
    
    def __init__(self, position=None, color=None, intensity=1.0):
        """
        Инициализация источника света
        
        Args:
            position (Vector3): Позиция источника света
            color (Vector3 или tuple): Цвет света (RGB, 0-1 или 0-255)
            intensity (float): Интенсивность света
        """
        self.position = position if position is not None else Vector3(0, 0, 0)
        
        if color is None:
            self.color = Vector3(1.0, 1.0, 1.0)  # Белый свет
        elif isinstance(color, (tuple, list)):
            # Если цвет в диапазоне [0, 255], нормализуем до [0, 1]
            if len(color) >= 3 and color[0] > 1.0:
                self.color = Vector3(color[0] / 255.0, color[1] / 255.0, color[2] / 255.0)
            else:
                self.color = Vector3(color[0], color[1], color[2])
        else:
            self.color = color
        
        self.intensity = intensity


def phong_lighting(normal, view_dir, light_dir, light_color, 
                   ambient_color=(0.1, 0.1, 0.1),
                   diffuse_color=(0.8, 0.8, 0.8),
                   specular_color=(1.0, 1.0, 1.0),
                   shininess=32.0):
    """
    Вычисляет освещение по модели Фонга
    
    Модель Фонга комбинирует три типа освещения:
    - Ambient: базовый свет (везде одинаковый)
    - Diffuse: зависит от угла между нормалью и светом
    - Specular: блики (зависит от угла отражения)
    
    Args:
        normal (Vector3): Нормаль поверхности (должна быть нормализована)
        view_dir (Vector3): Направление от точки к камере (должно быть нормализовано)
        light_dir (Vector3): Направление от точки к источнику света (должно быть нормализовано)
        light_color (Vector3 или tuple): Цвет света
        ambient_color (tuple): Цвет окружающего освещения (RGB, 0-1)
        diffuse_color (tuple): Цвет рассеянного отражения (RGB, 0-1)
        specular_color (tuple): Цвет зеркального отражения (RGB, 0-1)
        shininess (float): Блеск поверхности (чем больше, тем более резкие блики)
        
    Returns:
        tuple: Итоговый цвет (R, G, B) в диапазоне [0, 255]
        
    Объяснение:
        1. Ambient = базовый цвет * ambient_color
        2. Diffuse = max(0, dot(normal, light_dir)) * diffuse_color * light_color
        3. Specular = max(0, dot(reflect_dir, view_dir))^shininess * specular_color * light_color
        4. Итоговый цвет = Ambient + Diffuse + Specular
    """
    # Нормализуем векторы (на случай если они не нормализованы)
    normal = normal.normalize()
    view_dir = view_dir.normalize()
    light_dir = light_dir.normalize()
    
    # Преобразуем light_color в Vector3 если нужно
    if isinstance(light_color, (tuple, list)):
        if len(light_color) >= 3 and light_color[0] > 1.0:
            light_color_vec = Vector3(light_color[0] / 255.0, light_color[1] / 255.0, light_color[2] / 255.0)
        else:
            light_color_vec = Vector3(light_color[0], light_color[1], light_color[2])
    else:
        light_color_vec = light_color
    
    # 1. Ambient освещение (окружающее)
    ambient = (
        ambient_color[0] * light_color_vec.x,
        ambient_color[1] * light_color_vec.y,
        ambient_color[2] * light_color_vec.z
    )
    
    # 2. Diffuse освещение (рассеянное)
    # Вычисляем косинус угла между нормалью и направлением света
    ndotl = normal.scalarmul(light_dir)
    ndotl = max(0.0, ndotl)  # Не может быть отрицательным
    
    diffuse = (
        ndotl * diffuse_color[0] * light_color_vec.x,
        ndotl * diffuse_color[1] * light_color_vec.y,
        ndotl * diffuse_color[2] * light_color_vec.z
    )
    
    # 3. Specular освещение (зеркальное)
    # Вычисляем направление отражения света
    # reflect = 2 * (normal · light_dir) * normal - light_dir
    reflect_dir = normal * (2.0 * ndotl) - light_dir
    reflect_dir = reflect_dir.normalize()
    
    # Вычисляем косинус угла между отраженным лучом и направлением взгляда
    rdotv = reflect_dir.scalarmul(view_dir)
    rdotv = max(0.0, rdotv)
    
    # Степень блеска
    specular_factor = math_std.pow(rdotv, shininess)
    
    specular = (
        specular_factor * specular_color[0] * light_color_vec.x,
        specular_factor * specular_color[1] * light_color_vec.y,
        specular_factor * specular_color[2] * light_color_vec.z
    )
    
    # Комбинируем все компоненты
    final_color = (
        ambient[0] + diffuse[0] + specular[0],
        ambient[1] + diffuse[1] + specular[1],
        ambient[2] + diffuse[2] + specular[2]
    )
    
    # Ограничиваем значения [0, 1] и преобразуем в [0, 255]
    result = (
        max(0, min(255, int(final_color[0] * 255))),
        max(0, min(255, int(final_color[1] * 255))),
        max(0, min(255, int(final_color[2] * 255)))
    )
    
    return result


def compute_lighting_at_point(point, normal, camera_position, light, 
                               ambient_color=(0.1, 0.1, 0.1),
                               diffuse_color=(0.8, 0.8, 0.8),
                               specular_color=(1.0, 1.0, 1.0),
                               shininess=32.0):
    """
    Вычисляет освещение в конкретной точке поверхности
    
    Args:
        point (Vector3): Точка на поверхности
        normal (Vector3): Нормаль поверхности
        camera_position (Vector3): Позиция камеры
        light (Light): Источник света
        ambient_color, diffuse_color, specular_color (tuple): Цвета материала
        shininess (float): Блеск поверхности
        
    Returns:
        tuple: Итоговый цвет (R, G, B) в диапазоне [0, 255]
    """
    # Направление от точки к камере
    view_dir = camera_position - point
    view_dir = view_dir.normalize()
    
    # Направление от точки к источнику света
    light_dir = light.position - point
    light_dir = light_dir.normalize()
    
    return phong_lighting(
        normal, view_dir, light_dir, light.color,
        ambient_color, diffuse_color, specular_color, shininess
    )
