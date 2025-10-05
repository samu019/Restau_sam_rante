# restaurant/middleware.py
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
import re

class SecurityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # URLs públicas que no requieren autenticación
        self.public_urls = [
            '/',
            '/registro/',
            '/login/',
            '/logout/',
            '/restaurantes/',
            '/categorias/',
            '/contacto/',
            '/menu/\d+/',  # Menús públicos
            '/categoria/\d+/',
            '/bienvenidos/',
        ]
        
        # URLs de administración que requieren staff
        self.admin_urls = [
            '/admin/',
            '/admin/dashboard/',
            '/admin/solicitudes/',
            '/admin/solicitud/',
            '/admin/aprobar-solicitud/',
            '/admin/rechazar-solicitud/',
        ]

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        path = request.path_info
        
        # Verificar si es una URL pública
        if self.is_public_url(path):
            return None
            
        # Verificar si el usuario está autenticado
        if not request.user.is_authenticated:
            messages.error(request, "Debes iniciar sesión para acceder a esta página.")
            return redirect(f'{reverse("login")}?next={path}')
            
        # Verificar URLs de administración
        if self.is_admin_url(path) and not request.user.is_staff:
            messages.error(request, "No tienes permisos de administrador.")
            return redirect('index')
            
        return None

    def is_public_url(self, path):
        """Verifica si la URL es pública"""
        for pattern in self.public_urls:
            if re.match(pattern.replace('\d+', '\\d+'), path):
                return True
        return False

    def is_admin_url(self, path):
        """Verifica si la URL es de administración"""
        for pattern in self.admin_urls:
            if re.match(pattern.replace('\d+', '\\d+'), path):
                return True
        return False