"""
ThemeManager - класс для управления темами интерфейса

Управляет переключением между светлой и темной темами,
применяя соответствующие стили к элементам интерфейса.
"""


class ThemeManager:
    """
    Класс для управления темами приложения
    
    Поддерживает:
    - Светлую тему (light)
    - Темную тему (dark)
    - Применение стилей к элементам интерфейса
    """
    
    LIGHT_THEME = "light"
    DARK_THEME = "dark"
    
    def __init__(self):
        """Инициализация ThemeManager"""
        self.current_theme = self.LIGHT_THEME
    
    def get_theme(self):
        """Возвращает текущую тему"""
        return self.current_theme
    
    def set_theme(self, theme):
        """
        Устанавливает тему
        
        Args:
            theme (str): 'light' или 'dark'
        """
        if theme in [self.LIGHT_THEME, self.DARK_THEME]:
            self.current_theme = theme
    
    def toggle_theme(self):
        """Переключает тему"""
        if self.current_theme == self.LIGHT_THEME:
            self.current_theme = self.DARK_THEME
        else:
            self.current_theme = self.LIGHT_THEME
        return self.current_theme
    
    def get_stylesheet(self):
        """
        Возвращает CSS стили для текущей темы
        
        Returns:
            str: CSS стили
        """
        if self.current_theme == self.DARK_THEME:
            return self._get_dark_stylesheet()
        else:
            return self._get_light_stylesheet()
    
    def _get_light_stylesheet(self):
        """Возвращает стили для светлой темы"""
        return """
        QMainWindow {
            background-color: #f5f5f5;
        }
        QWidget {
            background-color: #ffffff;
            color: #212121;
        }
        QPushButton {
            background-color: #2196F3;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #1976D2;
        }
        QPushButton:pressed {
            background-color: #0D47A1;
        }
        QPushButton:disabled {
            background-color: #cccccc;
            color: #666666;
        }
        QListWidget {
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
        }
        QListWidget::item {
            padding: 8px;
            border-bottom: 1px solid #f0f0f0;
        }
        QListWidget::item:selected {
            background-color: #E3F2FD;
            color: #1976D2;
        }
        QListWidget::item:hover {
            background-color: #F5F5F5;
        }
        QLineEdit, QSpinBox, QDoubleSpinBox {
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            padding: 6px;
        }
        QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
            border: 2px solid #2196F3;
        }
        QLabel {
            color: #212121;
        }
        QGroupBox {
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            margin-top: 10px;
            font-weight: bold;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }
        QMenuBar {
            background-color: #ffffff;
            color: #212121;
        }
        QMenuBar::item:selected {
            background-color: #E3F2FD;
        }
        QMenu {
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
        }
        QMenu::item:selected {
            background-color: #E3F2FD;
        }
        QStatusBar {
            background-color: #f5f5f5;
            color: #212121;
        }
        """
    
    def _get_dark_stylesheet(self):
        """Возвращает стили для темной темы"""
        return """
        QMainWindow {
            background-color: #121212;
        }
        QWidget {
            background-color: #1e1e1e;
            color: #e0e0e0;
        }
        QPushButton {
            background-color: #2196F3;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #1976D2;
        }
        QPushButton:pressed {
            background-color: #0D47A1;
        }
        QPushButton:disabled {
            background-color: #424242;
            color: #757575;
        }
        QListWidget {
            background-color: #2d2d2d;
            border: 1px solid #424242;
            border-radius: 4px;
            color: #e0e0e0;
        }
        QListWidget::item {
            padding: 8px;
            border-bottom: 1px solid #424242;
        }
        QListWidget::item:selected {
            background-color: #1976D2;
            color: white;
        }
        QListWidget::item:hover {
            background-color: #424242;
        }
        QLineEdit, QSpinBox, QDoubleSpinBox {
            background-color: #2d2d2d;
            border: 1px solid #424242;
            border-radius: 4px;
            padding: 6px;
            color: #e0e0e0;
        }
        QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
            border: 2px solid #2196F3;
        }
        QLabel {
            color: #e0e0e0;
        }
        QGroupBox {
            border: 1px solid #424242;
            border-radius: 4px;
            margin-top: 10px;
            font-weight: bold;
            color: #e0e0e0;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }
        QMenuBar {
            background-color: #1e1e1e;
            color: #e0e0e0;
        }
        QMenuBar::item:selected {
            background-color: #424242;
        }
        QMenu {
            background-color: #2d2d2d;
            border: 1px solid #424242;
            color: #e0e0e0;
        }
        QMenu::item:selected {
            background-color: #1976D2;
        }
        QStatusBar {
            background-color: #121212;
            color: #e0e0e0;
        }
        """
