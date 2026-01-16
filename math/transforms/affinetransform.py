import math
from ..math_module.vector3 import Vector3
from ..math_module.matrix4x4 import Matrix4x4 

class AffineTransform:
    def __init__(self):
        self.translation = Vector3(0.0, 0.0, 0.0)
        self.rotation = Vector3(0.0, 0.0, 0.0)
        self.scale = Vector3(1.0, 1.0, 1.0)

    def __str__(self):
        return (f'Transform(\n' f' translation = {self.translation},\n 'f' rotation = {self.rotation},\n'
                f'  scale = {self.scale}\n' f')')

    def transform_matrix(self):
        T = Matrix4x4.translation(self.translation.x, self.translation.y, self.translation.z)

        Rx = Matrix4x4.rotation_x(self.rotation.x)
        Ry = Matrix4x4.rotation_y(self.rotation.y)
        Rz = Matrix4x4.rotation_z(self.rotation.z)
        R = Rz * Ry * Rx

        S = Matrix4x4.scale(self.scale.x, self.scale.y, self.scale.z)

        M = T * R * S

        return M
    
    def transform_point(self, point):
        if not isinstance(point, Vector3):
            raise TypeError('Точка должна быть Vector3')
        return self.transform_matrix() * point
    
    def transform_vector(self, vector):
        if not isinstance(vector, Vector3):
            raise TypeError('Вектор должен быть Vector3')
        
        Rx = Matrix4x4.rotation_x(self.rotation.x)
        Ry = Matrix4x4.rotation_y(self.rotation.y)
        Rz = Matrix4x4.rotation_z(self.rotation.z)
        R = Rz * Ry * Rx 

        S = Matrix4x4.scale(self.scale.x, self.scale.y, self.scale.z)

        V = R * S * vector

        return V
    
    def transform_vertices(self, vertices):
        matrix = self.transform_matrix()
        transform_v = []
        for v in vertices:
            new_v = matrix * v
            transform_v.append(new_v)
        return transform_v

    def reset(self):
        self.translation = Vector3(0.0, 0.0, 0.0)
        self.rotation = Vector3(0.0, 0.0, 0.0)
        self.scale = Vector3(1.0, 1.0, 1.0)

    