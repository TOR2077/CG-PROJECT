import math

from .vector3 import Vector3
from .vector4 import Vector4


class Matrix4x4:
    def __init__(self, data = None, identity = False, zero = False):
        if identity == True:
            self.data = [[1.0, 0.0, 0.0, 0.0],
                         [0.0, 1.0, 0.0, 0.0],
                         [0.0, 0.0, 1.0, 0.0],
                         [0.0, 0.0, 0.0, 1.0]] 
        
        elif zero == True:
            self.data = [[0.0, 0.0, 0.0, 0.0],
                         [0.0, 0.0, 0.0, 0.0],
                         [0.0, 0.0, 0.0, 0.0],
                         [0.0, 0.0, 0.0, 0.0]]
        
        elif data is not None:
            if len(data) != 4:
                raise ValueError('В матрице должно быть 4 строки')
            for row in data:
                if len(row) != 4:
                    raise ValueError('В каждой строке должно быть 4 элемента')
            self.data = [[float(data[i][j]) for j in range(4)] for i in range(4)]

        else: self.data = [[1.0, 0.0, 0.0, 0.0],
                          [0.0, 1.0, 0.0, 0.0],
                          [0.0, 0.0, 1.0, 0.0],
                          [0.0, 0.0, 0.0, 1.0]] 
    
    def __str__(self):
        return "\n".join([str(row) for row in self.data])
    
    def __add__(self, other):
        if not isinstance(other, Matrix4x4):
            raise TypeError('Можно складывать только матрицы размерностью 4')
        result = Matrix4x4(zero = True)
        for i in range(4):
            for j in range(4):
                result.data[i][j] = self.data[i][j] + other.data[i][j]
        return result
    
    def __sub__(self, other):
        if not isinstance(other, Matrix4x4):
            raise TypeError('Можно вычитать только матрицы размерностью 4')
        result = Matrix4x4(zero = True)
        for i in range(4):
            for j in range(4):
                result.data[i][j] = self.data[i][j] - other.data[i][j]
        return result
    
    def __mul__(self, other):
        # Умножение матрицы на вектор-столбец Vector3
        if isinstance(other, Vector3):
            result = [0.0] * 4
            for i in range(4):
                result[i] = (self.data[i][0] * other.x +
                             self.data[i][1] * other.y +
                             self.data[i][2] * other.z +
                             self.data[i][3] * 1.0)
            if result[3] != 0:
                return Vector3(result[0] / result[3],
                               result[1] / result[3],
                               result[2] / result[3])
            return Vector3(result[0], result[1], result[2])

        # Умножение матрицы на вектор-столбец Vector4
        elif isinstance(other, Vector4):
            result = [0.0] * 4
            for i in range(4):
                result[i] = (self.data[i][0] * other.x +
                             self.data[i][1] * other.y +
                             self.data[i][2] * other.z +
                             self.data[i][3] * other.w)
            return Vector4(result[0], result[1], result[2], result[3])

        #Перемножение матриц
        elif isinstance(other, Matrix4x4):
            result = Matrix4x4(zero = True)
            for i in range(4):
                for j in range(4):
                    result.data[i][j] = 0.0
                    for k in range(4):
                        result.data[i][j] += self.data[i][k] * other.data[k][j]
            return result
        else: raise TypeError('Можно умножать только на Vector3, Vector4 или Matrix4x4')

    def transpose(self):
        result = Matrix4x4(zero = True)
        for i in range(4):
            for j in range(4):
                result.data[i][j] = self.data[j][i]
        return result
    
    @staticmethod
    def translation(tx, ty, tz):
        return Matrix4x4(data = 
                        [[1.0, 0.0, 0.0, float(tx)],
                         [0.0, 1.0, 0.0, float(ty)],
                         [0.0, 0.0, 1.0, float(tz)],
                         [0.0, 0.0, 0.0, 1.0]])
    
    @staticmethod 
    def rotation_x(angle):
        s = math.sin(angle)
        c = math.cos(angle)
        return Matrix4x4(data = 
                        [[1.0, 0.0, 0.0, 0.0],
                         [0.0, c, -s, 0.0],
                         [0.0, s, c, 0.0],
                         [0.0, 0.0, 0.0, 1.0]])
    
    @staticmethod
    def rotation_y(angle):
        s = math.sin(angle)
        c = math.cos(angle)
        return Matrix4x4(data = 
                        [[c, 0.0, s, 0.0],
                         [0.0, 1.0, 0.0, 0.0],
                         [-s, 0.0, c, 0.0],
                         [0.0, 0.0, 0.0, 1.0]])
    @staticmethod
    def rotation_z(angle):
        s = math.sin(angle)
        c = math.cos(angle)
        return Matrix4x4(data = 
                        [[c, -s, 0.0, 0.0],
                         [s, c, 0.0, 0.0],
                         [0.0, 0.0, 1.0, 0.0],
                         [0.0, 0.0, 0.0, 1.0]])
    
    @staticmethod 
    def scale(sx, sy, sz):  
        return Matrix4x4(data = 
                        [[float(sx), 0.0, 0.0, 0.0],
                         [0.0, float(sy), 0.0, 0.0],
                         [0.0, 0.0, float(sz), 0.0],
                         [0.0, 0.0, 0.0, 1.0]])