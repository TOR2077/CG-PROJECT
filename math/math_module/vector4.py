import math 

e = 1e-9

class Vector4:
    def __init__(self, x = 0.0, y = 0.0, z = 0.0, w = 0.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.w = float(w)

    def __str__(self):
        return f'Vector4({self.x}, {self.y}, {self.z}, {self.w})'
    
    def __add__(self, other):
        if not isinstance(other, Vector4):
            raise TypeError('Можно складывать только векторы размерностью 4')
        return Vector4(self.x + other.x, self.y + other.y, self.z + other.z, self.w + other.w)

    def __sub__(self, other):
        if not isinstance(other, Vector4):
            raise TypeError('Можно вычитать только векторы размерностью 4')
        return Vector4(self.x - other.x, self.y - other.y, self.z - other.z, self.w - other.w)

    def __mul__(self, scalar):
        return Vector4(self.x * scalar, self.y * scalar, self.z * scalar, self.w * scalar)
    
    def __rmul__(self, scalar):
        return self.__mul__(scalar)
    
    def __truediv__(self, scalar):
        if scalar == 0:
            raise ZeroDivisionError('На ноль делить нельзя')
        return Vector4(self.x / scalar, self.y / scalar, self.z / scalar, self.w / scalar)

    def length(self):
        return math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2 + self.w ** 2)
    
    def normalize(self):
        l = self.length()
        if abs(l) < e: 
            return Vector4(0, 0, 0, 0)
        return Vector4(self.x / l, self.y / l, self.z / l, self.w / l)

    def scalarmul(self, other):
        if not isinstance(other, Vector4):
            raise TypeError('Можно умножать только скаляры размерностью 4')
        return(self.x * other.x + self.y * other.y + self.z * other.z + self.w * other.w)


                  
