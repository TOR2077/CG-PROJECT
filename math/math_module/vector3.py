import math 

e = 1e-9

class Vector3:
    def __init__(self, x = 0.0, y = 0.0, z = 0.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def __str__(self):
        return f'Vector3({self.x}, {self.y}, {self.z})'
    
    def __add__(self, other):
        if not isinstance(other, Vector3):
            raise TypeError('Можно складывать только векторы размерностью 3')
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        if not isinstance(other, Vector3):
            raise TypeError('Можно вычитать только векторы размерностью 3')
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)
        
    def __mul__(self, scalar):
        return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)
    
    def __rmul__(self, scalar):
        return self.__mul__(scalar)
    
    def __truediv__(self, scalar):
        if scalar == 0:
            raise ZeroDivisionError('На ноль делить нельзя')
        return Vector3(self.x / scalar, self.y / scalar, self.z / scalar)

    def length(self):
        return math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)
    
    def normalize(self):
        l = self.length()
        if abs(l) < e: 
            return Vector3(0, 0, 0)
        return Vector3(self.x / l, self.y / l, self.z / l)

    def scalarmul(self, other):
        if not isinstance(other, Vector3):
            raise TypeError('Можно умножать только скаляры размерностью 3')
        return(self.x * other.x + self.y * other.y + self.z * other.z)

    def vectormul(self, other): 
        if not isinstance(other, Vector3):
            raise TypeError('Можно умножать только векторы размерностью 3')
        return Vector3(self.y * other.z - self.z * other.y, 
                       self.z * other.x - self.x * other.z,
                       self.x * other.y - self.y * other.x) 
    

                  
