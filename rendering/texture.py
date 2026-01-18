"""
Модуль для работы с текстурами

Текстура - это изображение, которое накладывается на 3D модель,
чтобы придать ей детали и реалистичность.

Объяснение для начинающих:
- Текстура = картинка (например, фото дерева)
- Текстурные координаты (UV) = где на картинке брать цвет для каждой вершины
- UV координаты: U и V от 0 до 1 (0,0 = левый верхний угол, 1,1 = правый нижний)
"""

import sys
import os
import math
from PIL import Image

# Добавляем путь к модулю math
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from math.math_module.vector2 import Vector2


class Texture:
    """
    Класс для представления текстуры
    
    Текстура хранит изображение и предоставляет методы для получения
    цвета пикселя по текстурным координатам (UV).
    """
    
    def __init__(self, image_path=None, image_data=None):
        """
        Инициализация текстуры
        
        Args:
            image_path (str, optional): Путь к файлу изображения
            image_data (PIL.Image, optional): Объект изображения PIL
        """
        self.width = 0
        self.height = 0
        self.data = None  # Список списков RGB пикселей: data[y][x] = (r, g, b)
        
        if image_path:
            self.load_from_file(image_path)
        elif image_data:
            self.load_from_image(image_data)
    
    def load_from_file(self, image_path):
        """
        Загружает текстуру из файла
        
        Args:
            image_path (str): Путь к файлу изображения
            
        Raises:
            FileNotFoundError: Если файл не найден
            ValueError: Если файл не является изображением
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Текстура не найдена: {image_path}")
        
        try:
            image = Image.open(image_path)
            # Конвертируем в RGB (на случай если изображение в другом формате)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            self.load_from_image(image)
        except Exception as e:
            raise ValueError(f"Ошибка загрузки текстуры {image_path}: {str(e)}")
    
    def load_from_image(self, image):
        """
        Загружает текстуру из объекта PIL Image
        
        Args:
            image (PIL.Image): Объект изображения PIL
        """
        self.width = image.width
        self.height = image.height
        
        # Конвертируем изображение в список списков RGB
        self.data = []
        pixels = image.load()
        
        for y in range(self.height):
            row = []
            for x in range(self.width):
                r, g, b = pixels[x, y]
                row.append((r, g, b))
            self.data.append(row)
    
    def sample(self, u, v, wrap_mode='repeat'):
        """
        Получает цвет текстуры по текстурным координатам
        
        Args:
            u (float): U координата (0.0 - 1.0)
            v (float): V координата (0.0 - 1.0)
            wrap_mode (str): Режим оборачивания ('repeat' или 'clamp')
                - 'repeat': повторяет текстуру (0.0 и 1.0 = один и тот же пиксель)
                - 'clamp': ограничивает координаты [0, 1]
        
        Returns:
            tuple: Цвет пикселя (R, G, B) в диапазоне [0, 255]
            
        Объяснение:
            UV координаты (0.0, 0.0) = левый верхний угол текстуры
            UV координаты (1.0, 1.0) = правый нижний угол текстуры
        """
        if self.data is None or self.width == 0 or self.height == 0:
            return (128, 128, 128)  # Серый цвет по умолчанию
        
        # Обрабатываем режим оборачивания
        if wrap_mode == 'repeat':
            # Повторяем текстуру (tile)
            u = u - math.floor(u)
            v = v - math.floor(v)
        elif wrap_mode == 'clamp':
            # Ограничиваем координаты
            u = max(0.0, min(1.0, u))
            v = max(0.0, min(1.0, v))
        
        # Преобразуем UV в координаты пикселя
        x = int(u * (self.width - 1))
        y = int(v * (self.height - 1))
        
        # Ограничиваем координаты (на случай ошибок округления)
        x = max(0, min(self.width - 1, x))
        y = max(0, min(self.height - 1, y))
        
        return self.data[y][x]
    
    def sample_bilinear(self, u, v, wrap_mode='repeat'):
        """
        Получает цвет текстуры с билинейной фильтрацией
        
        Билинейная фильтрация делает текстуру более гладкой,
        усредняя цвета соседних пикселей.
        
        Args:
            u (float): U координата (0.0 - 1.0)
            v (float): V координата (0.0 - 1.0)
            wrap_mode (str): Режим оборачивания
            
        Returns:
            tuple: Цвет пикселя (R, G, B)
        """
        if self.data is None or self.width == 0 or self.height == 0:
            return (128, 128, 128)
        
        # Обрабатываем режим оборачивания
        if wrap_mode == 'repeat':
            u = u - math.floor(u)
            v = v - math.floor(v)
        elif wrap_mode == 'clamp':
            u = max(0.0, min(1.0, u))
            v = max(0.0, min(1.0, v))
        
        # Преобразуем UV в координаты пикселя (с дробной частью)
        x_float = u * (self.width - 1)
        y_float = v * (self.height - 1)
        
        # Получаем координаты четырех соседних пикселей
        x0 = int(x_float)
        y0 = int(y_float)
        x1 = min(x0 + 1, self.width - 1)
        y1 = min(y0 + 1, self.height - 1)
        
        # Дробные части для интерполяции
        fx = x_float - x0
        fy = y_float - y0
        
        # Получаем цвета четырех пикселей
        c00 = self.data[y0][x0]
        c10 = self.data[y0][x1]
        c01 = self.data[y1][x0]
        c11 = self.data[y1][x1]
        
        # Билинейная интерполяция
        # Сначала интерполируем по X
        c0 = (
            int(c00[0] * (1 - fx) + c10[0] * fx),
            int(c00[1] * (1 - fx) + c10[1] * fx),
            int(c00[2] * (1 - fx) + c10[2] * fx)
        )
        c1 = (
            int(c01[0] * (1 - fx) + c10[0] * fx),
            int(c01[1] * (1 - fx) + c10[1] * fx),
            int(c01[2] * (1 - fx) + c10[2] * fx)
        )
        
        # Затем интерполируем по Y
        result = (
            int(c0[0] * (1 - fy) + c1[0] * fy),
            int(c0[1] * (1 - fy) + c1[1] * fy),
            int(c0[2] * (1 - fy) + c1[2] * fy)
        )
        
        return result
    
    def get_size(self):
        """
        Возвращает размер текстуры
        
        Returns:
            tuple: (width, height)
        """
        return (self.width, self.height)
    
    def is_loaded(self):
        """Проверяет, загружена ли текстура"""
        return self.data is not None and self.width > 0 and self.height > 0
