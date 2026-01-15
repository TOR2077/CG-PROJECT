import math 

class Vector2:
    def __init__(self, x = 0.0, y = 0.0):
        self.x = float(x)
        self.y = float(y)

    def __str__(self):
        return f'Vector2({self.x}, {self.y})'
    
    def __add__(self, other):
        if not isinstance(Vector2, other):
            raise TypeError('Можно складывать только векторы размерностью 2')
        else: Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        if not isinstance(Vector2, other):
            raise TypeError('Можно вычитать только векторы размерностью 2')
    
    def __mul__(self, scalar):
        return Vector2(self.x * scalar, self.y * scalar)
    
    def __rmul__(self, scalar):
        return self.__mul__(scalar)
    
    def __truediv__(self, scalar):
        if scalar == 0:
            raise ZeroDivisionError('На ноль делить нельзя')
        else: return(self.x / scalar, self.y / scalar)

    def length(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)
    
    def normalize(self):
        l = self.length()
        if l == 0: 
            return Vector2(0, 0)
        else: return Vector2(self.x / l, self.y / l)

    def scalarmul(self, other):
        if not isinstance(Vector2, other):
            raise TypeError('Можно умножать только скаляры размерностью 2')
        else: return(self.x * other.x + self.y * other.y)

    

                  
