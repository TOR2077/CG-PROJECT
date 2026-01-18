"""
Виджет для отображения рендеринга 3D сцены

Этот виджет использует наш рендерер для отрисовки 3D моделей
и отображает результат на экране.
"""

import sys
import os

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QImage, QPixmap, QPainter

# Добавляем пути к модулям
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from rendering.renderer import Renderer, RenderSettings
from rendering.camera import Camera
from rendering.texture import Texture
from rendering.lighting import Light
from math.math_module.vector3 import Vector3


class RenderWidget(QWidget):
    """
    Виджет для отображения рендеринга 3D сцены
    
    Этот виджет:
    - Содержит рендерер
    - Управляет камерой
    - Отрисовывает сцену
    - Отображает результат
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Создаем рендерер
        self.renderer = Renderer(width=800, height=600)
        
        # Создаем камеру по умолчанию
        self.camera = Camera(
            position=Vector3(0, 0, 5),
            target=Vector3(0, 0, 0),
            up=Vector3(0, 1, 0)
        )
        
        # Сцена (будет установлена извне)
        self.scene = None
        
        # Устанавливаем минимальный размер
        self.setMinimumSize(400, 300)
        
        # Устанавливаем фокус для обработки клавиатуры
        self.setFocusPolicy(Qt.StrongFocus)
    
    def set_scene(self, scene):
        """
        Устанавливает сцену для рендеринга
        
        Args:
            scene: Объект Scene
        """
        self.scene = scene
        self.update_render()
    
    def set_camera(self, camera):
        """
        Устанавливает камеру для рендеринга
        
        Args:
            camera: Объект Camera
        """
        self.camera = camera
        self.update_render()
    
    def set_texture(self, texture):
        """
        Устанавливает текстуру
        
        Args:
            texture: Объект Texture или None
        """
        self.renderer.set_texture(texture)
        self.update_render()
    
    def set_light(self, light):
        """
        Устанавливает источник света
        
        Args:
            light: Объект Light
        """
        self.renderer.set_light(light)
        self.update_render()
    
    def get_render_settings(self):
        """
        Возвращает настройки рендеринга
        
        Returns:
            RenderSettings: Настройки рендеринга
        """
        return self.renderer.settings
    
    def update_render(self):
        """
        Обновляет рендеринг и перерисовывает виджет
        """
        if self.scene is None:
            return
        
        # Обновляем размер рендерера
        size = self.size()
        self.renderer.set_size(size.width(), size.height())
        self.camera.set_aspect_ratio(size.width(), size.height())
        
        # Очищаем экран
        self.renderer.clear(color=(20, 20, 30))  # Темно-синий фон
        
        # Рендерим все модели в сцене
        for model in self.scene.get_all_models():
            self.renderer.render_model(model, self.camera)
        
        # Перерисовываем виджет
        self.update()
    
    def paintEvent(self, event):
        """
        Обработчик события отрисовки
        
        Преобразует изображение из рендерера в QPixmap и отображает его
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Получаем изображение из рендерера
        image_data = self.renderer.get_image()
        
        if image_data:
            # Создаем QImage из данных
            height = len(image_data)
            width = len(image_data[0]) if height > 0 else 0
            
            if width > 0 and height > 0:
                # Создаем QImage
                qimage = QImage(width, height, QImage.Format_RGB888)
                
                # Копируем данные пикселей
                for y in range(height):
                    for x in range(width):
                        r, g, b = image_data[y][x]
                        qimage.setPixel(x, y, (r << 16) | (g << 8) | b)
                
                # Масштабируем изображение под размер виджета
                pixmap = QPixmap.fromImage(qimage)
                scaled_pixmap = pixmap.scaled(
                    self.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                
                # Рисуем в центре виджета
                x = (self.width() - scaled_pixmap.width()) // 2
                y = (self.height() - scaled_pixmap.height()) // 2
                painter.drawPixmap(x, y, scaled_pixmap)
        
        # Если нет данных, рисуем сообщение
        if not image_data or len(image_data) == 0:
            painter.drawText(
                self.rect(),
                Qt.AlignCenter,
                "Загрузите модель для просмотра"
            )
    
    def resizeEvent(self, event):
        """
        Обработчик изменения размера виджета
        """
        super().resizeEvent(event)
        self.update_render()
    
    def keyPressEvent(self, event):
        """
        Обработчик нажатий клавиш для управления камерой
        
        Стрелки: перемещение камеры
        WASD: перемещение камеры
        QE: приближение/отдаление
        """
        if self.camera is None:
            return
        
        move_speed = 0.1
        rotate_speed = 0.05
        
        key = event.key()
        
        # Перемещение камеры
        if key == Qt.Key_W or key == Qt.Key_Up:
            # Вперед
            direction = self.camera.target - self.camera.position
            direction = direction.normalize()
            self.camera.position = self.camera.position + direction * move_speed
            self.camera.target = self.camera.target + direction * move_speed
        elif key == Qt.Key_S or key == Qt.Key_Down:
            # Назад
            direction = self.camera.target - self.camera.position
            direction = direction.normalize()
            self.camera.position = self.camera.position - direction * move_speed
            self.camera.target = self.camera.target - direction * move_speed
        elif key == Qt.Key_A or key == Qt.Key_Left:
            # Влево
            forward = self.camera.target - self.camera.position
            forward = forward.normalize()
            right = forward.vectormul(self.camera.up)
            right = right.normalize()
            self.camera.position = self.camera.position - right * move_speed
            self.camera.target = self.camera.target - right * move_speed
        elif key == Qt.Key_D or key == Qt.Key_Right:
            # Вправо
            forward = self.camera.target - self.camera.position
            forward = forward.normalize()
            right = forward.vectormul(self.camera.up)
            right = right.normalize()
            self.camera.position = self.camera.position + right * move_speed
            self.camera.target = self.camera.target + right * move_speed
        elif key == Qt.Key_Q:
            # Приблизить
            self.camera.zoom(0.9)
        elif key == Qt.Key_E:
            # Отдалить
            self.camera.zoom(1.1)
        
        self.update_render()
        super().keyPressEvent(event)
    
    def mousePressEvent(self, event):
        """
        Обработчик нажатия мыши (для вращения камеры)
        """
        if event.button() == Qt.LeftButton:
            self.last_mouse_pos = event.pos()
            self.mouse_pressed = True
    
    def mouseReleaseEvent(self, event):
        """
        Обработчик отпускания мыши
        """
        if event.button() == Qt.LeftButton:
            self.mouse_pressed = False
    
    def mouseMoveEvent(self, event):
        """
        Обработчик движения мыши (для вращения камеры вокруг цели)
        """
        if hasattr(self, 'mouse_pressed') and self.mouse_pressed and self.camera:
            if hasattr(self, 'last_mouse_pos'):
                # Вычисляем смещение мыши
                dx = event.x() - self.last_mouse_pos.x()
                dy = event.y() - self.last_mouse_pos.y()
                
                # Преобразуем в углы вращения
                angle_x = dx * 0.01  # Горизонтальное вращение
                angle_y = dy * 0.01  # Вертикальное вращение
                
                # Вращаем камеру вокруг цели
                self.camera.rotate_around_target(angle_x, angle_y)
                
                self.last_mouse_pos = event.pos()
                self.update_render()
        
        super().mouseMoveEvent(event)
