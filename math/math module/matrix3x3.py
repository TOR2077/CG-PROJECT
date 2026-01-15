from .vector3 import Vector3

class Matrix3x3:
    def __init__(self, data = None, identity = False, zero = False):
        if identity == True:
            self.data = [[1.0, 0.0, 0.0],
                         [0.0, 1.0, 0.0],
                         [0.0, 0.0, 1.0]] 
        
        elif zero == True:
            self.data = [[0.0, 0.0, 0.0],
                         [0.0, 0.0, 0.0],
                         [0.0, 0.0, 0.0]]
        
        elif data is not None:
            if len(data) != 3:
                raise ValueError('В матрице должно быть 3 строки')
            for row in data:
                if len(row) != 3:
                    raise ValueError('В каждой строке должно быть 3 строки')
            self.data = [[float(data[i][j]) for j in range(3)] for i in range(3)]

        else: self.data =[[1.0, 0.0, 0.0],
                          [0.0, 1.0, 0.0],
                          [0.0, 0.0, 1.0]] 
    
    def __str__(self):
        return "\n".join([str(row) for row in self.data])
    
    def __add__(self, other):
        if not isinstance(other, Matrix3x3):
            raise TypeError('Можно складывать только матрицы размерностью 3')
        result = Matrix3x3(zero = True)
        for i in range(3):
            for j in range(3):
                result.data[i][j] = self.data[i][j] + other.data[i][j]
        return result
    
    def __sub__(self, other):
        if not isinstance(other, Matrix3x3):
            raise TypeError('Можно вычитать только матрицы размерностью 3')
        result = Matrix3x3(zero = True)
        for i in range(3):
            for j in range(3):
                result.data[i][j] = self.data[i][j] - other.data[i][j]
        return result
    
    def __mul__(self, other):
        # Умножение матрицы на вектор-столбец
        if isinstance(other, Vector3):
            result = [0.0] * 3
            for i in range(3):
                result[i] = (self.data[i][0] * other.x +
                             self.data[i][1] * other.y +
                             self.data[i][2] * other.z)
            return Vector3(result[0], result[1], result[2])
        #Перемножение матриц
        if isinstance(other, Matrix3x3):
            result = Matrix3x3(zero = True)
            for i in range(3):
                for j in range(3):
                    result.data[i][j] = 0.0
                    for k in range(3):
                        result.data[i][j] += self.data[i][k] * other.data[k][j]
            return result
        else: raise TypeError('Можно умножать только на Vector3 или Matrix3x3')

    def transpose(self):
        result = Matrix3x3(zero = True)
        for i in range(3):
            for j in range(3):
                result.data[i][j] = self.data[j][i]
        return result