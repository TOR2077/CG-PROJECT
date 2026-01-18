"""
Модуль для управления камерой в 3D сцене

Камера определяет, как мы смотрим на 3D объекты:
- Позиция камеры (где она находится)
- Направление взгляда (куда смотрит)
- Вверх (какая сторона "верх")
- Угол обзора (FOV - field of view)
- Ближняя и дальняя плоскости отсечения

Объяснение для начинающих:
Камера - это как ваши глаза в 3D мире. Она определяет:
- Где вы стоите (position)
- Куда смотрите (target или direction)
- Какой угол обзора (как широко видите)
"""

import sys
import os
# ВАЖНО: Импортируем стандартный math ПЕРЕД импортом нашего модуля math
import math as math_std  # Импортируем стандартный math под другим именем

# Добавляем путь к модулю math
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Импортируем наш модуль math (это перезапишет имя math, но у нас уже есть math_std)
import math  # Это наш модуль math из проекта
from math.math_module.vector3 import Vector3
from math.math_module.matrix4x4 import Matrix4x4


class Camera:
    """
    Класс для представления камеры в 3D сцене
    
    Камера использует систему "look-at" (смотреть на точку):
    - position: позиция камеры
    - target: точка, на которую смотрит камера
    - up: вектор "вверх" для камеры
    """
    
    def __init__(self, position=None, target=None, up=None, name="Camera"):
        """
        Инициализация камеры
        
        Args:
            position (Vector3): Позиция камеры (по умолчанию (0, 0, 5))
            target (Vector3): Точка, на которую смотрит камера (по умолчанию (0, 0, 0))
            up (Vector3): Вектор "вверх" (по умолчанию (0, 1, 0))
            name (str): Имя камеры
        """
        self.name = name
        
        # Позиция камеры в пространстве
        self.position = position if position is not None else Vector3(0, 0, 5)
        
        # Точка, на которую смотрит камера
        self.target = target if target is not None else Vector3(0, 0, 0)
        
        # Вектор "вверх" для камеры
        self.up = up if up is not None else Vector3(0, 1, 0)
        
        # Параметры проекции
        self.fov = math_std.radians(45.0)  # Угол обзора (field of view) в радианах
        self.aspect_ratio = 1.0  # Соотношение сторон (ширина/высота)
        self.near_plane = 0.1  # Ближняя плоскость отсечения
        self.far_plane = 1000.0  # Дальняя плоскость отсечения
    
    def get_view_matrix(self):
        """
        Вычисляет матрицу вида (view matrix)
        
        Матрица вида преобразует координаты из мирового пространства
        в пространство камеры (где камера находится в начале координат).
        
        Returns:
            Matrix4x4: Матрица вида
            
        Объяснение:
            Матрица вида "перемещает" весь мир так, чтобы камера была
            в начале координат и смотрела по оси -Z.
        """
        # Вычисляем направление взгляда (от камеры к цели)
        forward = self.target - self.position
        forward = forward.normalize()
        
        # Вычисляем правый вектор (перпендикулярно forward и up)
        right = forward.vectormul(self.up)
        right = right.normalize()
        
        # Пересчитываем up вектор (чтобы он был перпендикулярен forward и right)
        up = right.vectormul(forward)
        up = up.normalize()
        
        # Создаем матрицу вида
        # Это обратная матрица преобразования, которое перемещает камеру в начало координат
        view_data = [
            [right.x, up.x, -forward.x, 0],
            [right.y, up.y, -forward.y, 0],
            [right.z, up.z, -forward.z, 0],
            [
                -(right.x * self.position.x + right.y * self.position.y + right.z * self.position.z),
                -(up.x * self.position.x + up.y * self.position.y + up.z * self.position.z),
                (forward.x * self.position.x + forward.y * self.position.y + forward.z * self.position.z),
                1
            ]
        ]
        
        return Matrix4x4(data=view_data)
    
    def get_projection_matrix(self):
        """
        Вычисляет матрицу проекции (projection matrix)
        
        Матрица проекции преобразует координаты из пространства камеры
        в экранные координаты (с учетом перспективы).
        
        Returns:
            Matrix4x4: Матрица проекции
            
        Объяснение:
            Матрица проекции создает эффект перспективы - объекты, 
            которые дальше, выглядят меньше.
        """
        # Вычисляем параметры перспективной проекции
        f = 1.0 / math_std.tan(self.fov / 2.0)  # Фокусное расстояние
        
        # Создаем матрицу перспективной проекции
        projection_data = [
            [f / self.aspect_ratio, 0, 0, 0],
            [0, f, 0, 0],
            [0, 0, (self.far_plane + self.near_plane) / (self.near_plane - self.far_plane), -1],
            [0, 0, (2 * self.far_plane * self.near_plane) / (self.near_plane - self.far_plane), 0]
        ]
        
        return Matrix4x4(data=projection_data)
    
    def get_view_projection_matrix(self):
        """
        Вычисляет комбинированную матрицу вида-проекции
        
        Returns:
            Matrix4x4: Матрица вида-проекции
        """
        view = self.get_view_matrix()
        projection = self.get_projection_matrix()
        return projection * view
    
    def move(self, delta):
        """
        Перемещает камеру
        
        Args:
            delta (Vector3): Вектор перемещения
        """
        self.position = self.position + delta
        self.target = self.target + delta
    
    def rotate_around_target(self, angle_x, angle_y):
        """
        Вращает камеру вокруг цели (target)
        
        Args:
            angle_x (float): Угол вращения вокруг оси Y (в радианах)
            angle_y (float): Угол вращения вокруг оси X (в радианах)
        """
        # Вычисляем вектор от цели к камере
        direction = self.position - self.target
        
        # Вращаем вокруг оси Y (горизонтальное вращение)
        cos_x = math_std.cos(angle_x)
        sin_x = math_std.sin(angle_x)
        new_x = direction.x * cos_x - direction.z * sin_x
        new_z = direction.x * sin_x + direction.z * cos_x
        direction = Vector3(new_x, direction.y, new_z)
        
        # Вращаем вокруг оси X (вертикальное вращение)
        cos_y = math_std.cos(angle_y)
        sin_y = math_std.sin(angle_y)
        new_y = direction.y * cos_y - direction.z * sin_y
        new_z = direction.y * sin_y + direction.z * cos_y
        direction = Vector3(direction.x, new_y, new_z)
        
        # Обновляем позицию камеры
        self.position = self.target + direction
    
    def zoom(self, factor):
        """
        Приближает/отдаляет камеру (изменяет расстояние до цели)
        
        Args:
            factor (float): Множитель (1.0 = без изменений, >1 = приблизить, <1 = отдалить)
        """
        direction = self.position - self.target
        direction = direction * factor
        self.position = self.target + direction
    
    def set_aspect_ratio(self, width, height):
        """
        Устанавливает соотношение сторон экрана
        
        Args:
            width (float): Ширина экрана
            height (float): Высота экрана
        """
        if height > 0:
            self.aspect_ratio = width / height
    
    def look_at(self, target):
        """
        Направляет камеру на указанную точку
        
        Args:
            target (Vector3): Точка, на которую смотрит камера
        """
        self.target = target
    
    def __str__(self):
        return f"Camera(name='{self.name}', position={self.position}, target={self.target})"
    
    def __repr__(self):
        return self.__str__()
