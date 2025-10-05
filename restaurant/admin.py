# restaurant/admin.py
from django.contrib import admin
from .models import Categoria, Restaurante, Plato

# Registra los modelos en el panel de administración
admin.site.register(Categoria)
admin.site.register(Restaurante)
admin.site.register(Plato)
