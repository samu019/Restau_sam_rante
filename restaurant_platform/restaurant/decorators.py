# restaurant/decorators.py
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def login_required_redirect(view_func):
    """Decorador que redirige al login si no está autenticado"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Debes iniciar sesión para acceder a esta página.")
            return redirect(f'login?next={request.path}')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def staff_required(view_func):
    """Decorador que verifica si el usuario es staff"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Debes iniciar sesión para acceder a esta página.")
            return redirect(f'login?next={request.path}')
        
        if not request.user.is_staff:
            messages.error(request, "No tienes permisos de administrador.")
            return redirect('index')
            
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def propietario_required(view_func):
    """Decorador que verifica si el usuario es propietario del restaurante"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Debes iniciar sesión para acceder a esta página.")
            return redirect(f'login?next={request.path}')
        
        # Verificar si tiene restaurante
        if not hasattr(request.user, 'restaurante'):
            messages.error(request, "No tienes un restaurante asociado.")
            return redirect('dashboard')
            
        return view_func(request, *args, **kwargs)
    return _wrapped_view