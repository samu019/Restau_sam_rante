# restaurant/tests.py
from django.test import TestCase
from .models import Categoria, Restaurante

class CategoriaRestauranteTestCase(TestCase):
    
    def setUp(self):
        self.categoria = Categoria.objects.create(nombre="Comida Rápida", imagen="path/to/image.jpg")
        self.restaurante = Restaurante.objects.create(
            nombre="Restaurante Rápido", 
            direccion="Calle Falsa 123", 
            logo="path/to/logo.jpg", 
            categoria=self.categoria
        )
    
    def test_categoria_creation(self):
        categoria = self.categoria
        self.assertEqual(categoria.nombre, 'Comida Rápida')
    
    def test_restaurante_creation(self):
        restaurante = self.restaurante
        self.assertEqual(restaurante.nombre, 'Restaurante Rápido')
        self.assertEqual(restaurante.categoria.nombre, 'Comida Rápida')
