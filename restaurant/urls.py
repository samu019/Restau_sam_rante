# restaurant_platform/urls.py
from django.contrib import admin
from django.urls import path, include  # Asegúrate de importar include para las rutas de la app

urlpatterns = [
    path('admin/', admin.site.urls),  # Ruta para el panel de administración de Django
    path('', include('restaurant.urls')),  # Incluye las rutas de la app restaurant
]
