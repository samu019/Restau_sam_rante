from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Count, Sum
from django.utils import timezone
import re
# AGREGAR ESTAS IMPORTACIONES AL INICIO
from django.db.models import Count, Sum, Avg, Q  # Agregar Avg
from .models import Resena  # Agregar el nuevo modelo
from .forms import ResenaForm, CheckoutForm, BusquedaRestaurantesForm  # Agregar los nuevos forms
# AGREGAR ESTAS IMPORTACIONES AL INICIO DEL ARCHIVO
from django.db.models import Count, Sum, Avg, Q  # Q ya está, agregar Avg
from .decorators import login_required_redirect, staff_required, propietario_required
from .models import PlanRestaurante, SolicitudRestaurante, CuentaPago, Restaurante
from .models import Categoria, Restaurante, Plato, Pedido, PlatoPedido, Anuncio, PerfilUsuario
from .forms import RegisterForm, CustomLoginForm, RestauranteForm, CategoriaForm, PlatoForm, AnuncioForm, PerfilUsuarioForm, PedidoForm
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
import json
from django.shortcuts import render, get_object_or_404, redirect
from .models import Pedido, Restaurante, Plato, Categoria, PlatoPedido
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db.models import Q, Count
from django.contrib.auth.models import User
from .models import Restaurante, Plato, Pedido, Anuncio, Categoria, PlanRestaurante, SolicitudRestaurante, CuentaPago
from .emails import *

# ==================== VISTAS PÚBLICAS ====================

# ==================== HANDLERS DE ERROR ====================
def handler403(request, exception):
    """Manejo de error 403 - Acceso denegado"""
    return render(request, 'restaurant/403.html', status=403)

def handler404(request, exception):
    """Manejo de error 404 - Página no encontrada"""
    return render(request, 'restaurant/404.html', status=404)

def handler500(request):
    """Manejo de error 500 - Error del servidor"""
    return render(request, 'restaurant/500.html', status=500)

# ==================== VISTAS PÚBLICAS ====================
def index(request):
    """
    Vista principal - Landing page pública
    """
    # Verificar si el usuario está autenticado y tiene restaurantes
    if request.user.is_authenticated:
        try:
            # Verificar si el usuario tiene restaurantes usando el related_name correcto
            if hasattr(request.user, 'restaurantes') and request.user.restaurantes.exists():
                return redirect('dashboard')
        except:
            # Si hay algún error, continuar con la página pública
            pass
    
    # Para usuarios normales o no autenticados, mostrar landing page
    restaurantes_destacados = Restaurante.objects.filter(activo=True)[:6]
    
    # Obtener categorías con número de restaurantes
    categorias = Categoria.objects.filter(activa=True).annotate(
        num_restaurantes=Count('restaurante')
    )[:8]
    
    return render(request, 'restaurant/index.html', {
        'restaurantes': restaurantes_destacados,
        'categorias': categorias
    })

def bienvenidos(request):
    """
    Vista de bienvenida - Pública
    """
    return render(request, 'restaurant/bienvenidos.html')

def categorias(request):
    """
    Vista que muestra todas las categorías - Pública
    """
    categorias = Categoria.objects.filter(activa=True).annotate(
        num_platos=Count('platos')
    )
    return render(request, 'restaurant/categorias.html', {'categorias': categorias})

def restaurantes_list(request):
    """
    Vista que muestra todos los restaurantes activos - Pública
    """
    restaurantes = Restaurante.objects.filter(activo=True).annotate(
        num_platos=Count('platos')
    )
    return render(request, 'restaurant/restaurantes.html', {'restaurantes': restaurantes})

def contacto(request):
    """
    Vista de contacto - Pública
    """
    return render(request, 'restaurant/contacto.html')

# restaurant/views.py - REEMPLAZA COMPLETAMENTE la función menu_publico

def menu_publico(request, restaurante_id):
    """
    Menú público del restaurante para clientes - VERSIÓN CORREGIDA
    """
    print(f"=== 🚨 DEBUG menu_publico INICIADO ===")
    print(f"📥 ID recibido: {restaurante_id}")
    
    try:
        # 1. BUSCAR RESTAURANTE
        restaurante = Restaurante.objects.get(id=restaurante_id, activo=True)
        print(f"✅ Restaurante encontrado: '{restaurante.nombre}' (ID: {restaurante.id})")
        
        # 2. BUSCAR CATEGORÍAS ACTIVAS
        categorias = Categoria.objects.filter(restaurante=restaurante, activa=True).order_by('orden')
        print(f"📂 Categorías activas encontradas: {categorias.count()}")
        
        # 3. CONSTRUIR ESTRUCTURA DE DATOS PARA TEMPLATE
        categorias_con_platos = []
        platos_totales = 0
        
        for categoria in categorias:
            # Buscar platos activos en esta categoría
            platos = Plato.objects.filter(
                categoria=categoria, 
                activo=True
            ).order_by('nombre')
            
            print(f"🍽️ Categoría '{categoria.nombre}': {platos.count()} platos")
            
            # DEBUG DETALLADO DE CADA PLATO
            for plato in platos:
                # CALCULAR SI TIENE STOCK (CORREGIDO)
                tiene_stock = plato.stock_ilimitado or plato.stock > 0
                print(f"   ✅ PLATO: '{plato.nombre}' - Stock: {plato.stock} - Ilimitado: {plato.stock_ilimitado} - Disponible: {tiene_stock}")
            
            if platos.exists():
                # Agregar propiedad temporal para stock
                platos_con_stock = []
                for plato in platos:
                    # Crear una copia del objeto con propiedad temporal
                    plato.tiene_stock = plato.stock_ilimitado or plato.stock > 0
                    platos_con_stock.append(plato)
                
                categorias_con_platos.append({
                    'categoria': categoria,
                    'platos': platos_con_stock
                })
                platos_totales += platos.count()
        
        print(f"🎯 RESUMEN FINAL:")
        print(f"   - Categorías con platos: {len(categorias_con_platos)}")
        print(f"   - Platos totales: {platos_totales}")
        
        # PREPARAR CONTEXTO PARA TEMPLATE
        context = {
            'restaurante': restaurante,
            'categorias': categorias,
            'categorias_con_platos': categorias_con_platos,
            'total_platos': platos_totales,  # ✅ Total calculado
        }
        
        print("=== ✅ DEBUG: Contexto preparado correctamente ===")
        return render(request, 'restaurant/menu_publico.html', context)
        
    except Restaurante.DoesNotExist:
        print("❌ ERROR: Restaurante no encontrado o inactivo")
        messages.error(request, "Restaurante no encontrado o inactivo.")
        return redirect('restaurantes')
        
    except Exception as e:
        print(f"❌ ERROR CRÍTICO: {str(e)}")
        import traceback
        print(f"📋 Traceback: {traceback.format_exc()}")
        messages.error(request, "Error al cargar el menú del restaurante.")
        return redirect('restaurantes')
    
# ==================== SISTEMA DE CARRITO (Público/Autenticado) ====================
# ==================== SISTEMA DE CARRITO ====================

def ver_carrito(request, restaurante_id):
    """
    Ver carrito de compras - Público/Autenticado
    """
    try:
        restaurante = Restaurante.objects.get(id=restaurante_id, activo=True)
        carrito_data = request.session.get('carrito', {}).get(str(restaurante_id), {})
        
        print(f"=== 🛒 DEBUG ver_carrito ===")
        print(f"🏪 Restaurante: {restaurante.nombre}")
        print(f"📦 Carrito data: {carrito_data}")
        
        context = {
            'restaurante': restaurante,
            'carrito': carrito_data,
        }
        return render(request, 'restaurant/carrito.html', context)
        
    except Restaurante.DoesNotExist:
        messages.error(request, "Restaurante no encontrado.")
        return redirect('restaurantes')

def agregar_al_carrito(request, restaurante_id):
    """
    Agregar plato al carrito - Público/Autenticado
    """
    print(f"=== 🚨 DEBUG agregar_al_carrito ===")
    print(f"📨 Método: {request.method}")
    print(f"🏪 Restaurante ID: {restaurante_id}")
    
    if request.method == 'POST':
        try:
            plato_id = request.POST.get('plato_id')
            cantidad = int(request.POST.get('cantidad', 1))
            
            print(f"🍽️ Plato ID: {plato_id}")
            print(f"🔢 Cantidad: {cantidad}")
            
            if not plato_id:
                return JsonResponse({
                    'success': False,
                    'message': 'ID de plato no proporcionado'
                })
            
            plato = Plato.objects.get(id=plato_id, activo=True)
            print(f"✅ Plato encontrado: {plato.nombre}")
            
            # Inicializar carrito en session
            if 'carrito' not in request.session:
                request.session['carrito'] = {}
            
            carrito = request.session['carrito']
            restaurante_key = str(restaurante_id)
            
            # Inicializar carrito para este restaurante
            if restaurante_key not in carrito:
                carrito[restaurante_key] = {
                    'restaurante_id': restaurante_id,
                    'restaurante_nombre': plato.categoria.restaurante.nombre,
                    'items': {}
                }
            
            # Agregar o actualizar item
            items = carrito[restaurante_key]['items']
            plato_key = str(plato_id)
            
            if plato_key in items:
                items[plato_key]['cantidad'] += cantidad
            else:
                items[plato_key] = {
                    'plato_id': plato_id,
                    'nombre': plato.nombre,
                    'precio': float(plato.precio),
                    'cantidad': cantidad,
                    'imagen': plato.imagen.url if plato.imagen else None
                }
            
            request.session.modified = True
            
            # Calcular total de items
            total_items = sum(item['cantidad'] for item in items.values())
            
            return JsonResponse({
                'success': True,
                'message': f'{plato.nombre} agregado al carrito',
                'total_items': total_items
            })
            
        except Plato.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Plato no encontrado'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'})

def actualizar_carrito(request, restaurante_id):
    """
    Actualizar cantidad o eliminar items del carrito - Público/Autenticado
    """
    print(f"=== 🔄 DEBUG actualizar_carrito ===")
    print(f"📨 Método: {request.method}")
    print(f"🏪 Restaurante ID: {restaurante_id}")
    
    if request.method == 'POST':
        try:
            plato_id = request.POST.get('plato_id')
            cantidad = int(request.POST.get('cantidad', 1))
            
            print(f"🍽️ Plato ID: {plato_id}")
            print(f"🔢 Cantidad: {cantidad}")
            
            if not plato_id:
                return JsonResponse({
                    'success': False,
                    'message': 'ID de plato no proporcionado'
                })
            
            carrito = request.session.get('carrito', {})
            restaurante_key = str(restaurante_id)
            
            if restaurante_key in carrito:
                items = carrito[restaurante_key]['items']
                plato_key = str(plato_id)
                
                # Si cantidad es 0, eliminar el item
                if cantidad <= 0 and plato_key in items:
                    del items[plato_key]
                    mensaje = 'Producto eliminado del carrito'
                
                # Si cantidad es positiva y el item existe, actualizar
                elif cantidad > 0 and plato_key in items:
                    items[plato_key]['cantidad'] = cantidad
                    mensaje = 'Cantidad actualizada'
                
                else:
                    return JsonResponse({
                        'success': False, 
                        'message': 'Producto no encontrado en el carrito'
                    })
                
                request.session.modified = True
                
                # Calcular totales
                total = sum(item['precio'] * item['cantidad'] for item in items.values())
                total_items = sum(item['cantidad'] for item in items.values())
                
                return JsonResponse({
                    'success': True,
                    'message': mensaje,
                    'total': total,
                    'total_items': total_items
                })
            
            return JsonResponse({
                'success': False, 
                'message': 'Carrito no encontrado'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'message': f'Error: {str(e)}'
            })
    
    return JsonResponse({
        'success': False, 
        'message': 'Método no permitido'
    })

# ==================== AUTENTICACIÓN ====================
def register(request):
    """
    Registro de usuarios con formulario personalizado - Pública
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Crear perfil de usuario
            PerfilUsuario.objects.create(usuario=user)
            
            # Autenticar y loguear al usuario
            login(request, user)
            messages.success(request, f'¡Bienvenido {user.username}! Tu cuenta ha sido creada exitosamente.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario.')
    else:
        form = RegisterForm()
    
    return render(request, 'restaurant/register.html', {'form': form})

def login_view(request):
    """
    Inicio de sesión con formulario personalizado - Pública
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'¡Bienvenido de nuevo, {username}!')
                
                # Redirigir según el tipo de usuario
                if hasattr(user, 'restaurantes') and user.restaurantes.exists():
                    return redirect('dashboard')
                else:
                    return redirect('index')
        else:
            messages.error(request, 'Nombre de usuario o contraseña incorrectos.')
    else:
        form = CustomLoginForm()
    
    return render(request, 'restaurant/login.html', {'form': form})

def logout_view(request):
    """
    Cerrar sesión - Pública
    """
    logout(request)
    messages.info(request, 'Has cerrado sesión exitosamente.')
    return redirect('index')

# ==================== DASHBOARD & PANEL DE PROPIETARIO ====================
@login_required_redirect
def dashboard(request):
    """
    Dashboard principal para propietarios de restaurantes - Requiere autenticación
    """
    # Obtener planes para mostrar
    planes = PlanRestaurante.objects.filter(activo=True)
    
    try:
        restaurante = Restaurante.objects.get(propietario=request.user)
        
        # Estadísticas para el dashboard
        total_platos = Plato.objects.filter(
            categoria__restaurante=restaurante, 
            activo=True
        ).count()
        
        total_categorias = Categoria.objects.filter(
            restaurante=restaurante,
            activa=True
        ).count()
        
        pedidos_hoy = Pedido.objects.filter(
            restaurante=restaurante,
            fecha_creacion__date=timezone.now().date()
        ).count()
        
        pedidos_pendientes = Pedido.objects.filter(
            restaurante=restaurante,
            estado__in=['PENDIENTE', 'CONFIRMADO', 'PREPARACION']
        ).count()
        
        anuncios_activos = Anuncio.objects.filter(
            restaurante=restaurante,
            activo=True,
            fecha_inicio__lte=timezone.now(),
            fecha_fin__gte=timezone.now()
        ).count()
        
        # Calcular ingresos del mes
        pedidos_mes = Pedido.objects.filter(
            restaurante=restaurante,
            fecha_creacion__month=timezone.now().month,
            fecha_creacion__year=timezone.now().year,
            estado__in=['ENTREGADO', 'LISTO', 'EN_CAMINO']
        )
        ingresos_mes = sum(pedido.total for pedido in pedidos_mes) if pedidos_mes else 0
        
        # Últimos pedidos
        ultimos_pedidos = Pedido.objects.filter(
            restaurante=restaurante
        ).order_by('-fecha_creacion')[:5]
        
        # Platos más populares
        platos_populares = Plato.objects.filter(
            categoria__restaurante=restaurante
        ).order_by('?')[:3]  # Temporal: 3 platos aleatorios
        
    except Restaurante.DoesNotExist:
        restaurante = None
        total_platos = 0
        total_categorias = 0
        pedidos_hoy = 0
        pedidos_pendientes = 0
        anuncios_activos = 0
        ingresos_mes = 0
        ultimos_pedidos = []
        platos_populares = []
    
    context = {
        'restaurante': restaurante,
        'planes': planes,
        'total_platos': total_platos,
        'total_categorias': total_categorias,
        'pedidos_hoy': pedidos_hoy,
        'pedidos_pendientes': pedidos_pendientes,
        'anuncios_activos': anuncios_activos,
        'ingresos_mes': ingresos_mes,
        'ultimos_pedidos': ultimos_pedidos,
        'platos_populares': platos_populares,
        'es_propietario': restaurante is not None,
    }
    
    return render(request, 'restaurant/dashboard.html', context)

@login_required_redirect
def crear_restaurante(request):
    """
    Redirige al sistema de pagos para crear restaurante - Requiere autenticación
    """
    messages.info(request, "Para crear un restaurante, necesitas elegir un plan y realizar el pago.")
    return redirect('solicitar_restaurante')

# ==================== GESTIÓN DE CATEGORÍAS ====================
@login_required_redirect
def administrar_categorias(request):
    """
    Vista para gestionar categorías - Requiere ser propietario
    """
    print(f"=== DEBUG administrar_categorias ===")
    print(f"Usuario: {request.user.username} (ID: {request.user.id})")
    
    try:
        restaurante = Restaurante.objects.get(propietario=request.user, activo=True)
        print(f"✅ MÉTODO 1 EXITOSO: {restaurante.nombre}")
        
    except Restaurante.DoesNotExist:
        print("❌ MÉTODO 1 FALLÓ: Restaurante.DoesNotExist")
        
        # Métodos alternativos
        restaurante = Restaurante.objects.filter(propietario=request.user, activo=True).first()
        if not restaurante and hasattr(request.user, 'restaurantes'):
            restaurante = request.user.restaurantes.filter(activo=True).first()
        
        if not restaurante:
            messages.error(request, "No tienes un restaurante activo.")
            return redirect('dashboard')
    
    print(f"✅ RESTAURANTE FINAL: {restaurante.nombre}")
    print("=======================")
    
    categorias = Categoria.objects.filter(restaurante=restaurante)
    
    if request.method == 'POST':
        # DEBUG: Ver qué datos llegan del formulario
        print(f"📋 DATOS DEL FORMULARIO:")
        for key, value in request.POST.items():
            print(f"  {key}: {value}")
        print(f"📁 FILES: {request.FILES}")
        
        nombre = request.POST.get('nombre', '').strip()
        emoji = request.POST.get('emoji', '🍽️').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        
        # VALIDACIÓN ROBUSTA
        if not nombre:
            messages.error(request, "El nombre de la categoría es obligatorio.")
            return redirect('administrar_categorias')
        
        # Validar que no exista una categoría con el mismo nombre en este restaurante
        if Categoria.objects.filter(restaurante=restaurante, nombre__iexact=nombre).exists():
            messages.error(request, f"Ya existe una categoría con el nombre '{nombre}'.")
            return redirect('administrar_categorias')
        
        try:
            # CREAR CATEGORÍA CON LOS CAMPOS CORRECTOS
            categoria = Categoria.objects.create(
                restaurante=restaurante,
                nombre=nombre,
                emoji=emoji,
                descripcion=descripcion
            )
            print(f"✅ CATEGORÍA CREADA: {categoria.nombre}")
            messages.success(request, f"Categoría '{nombre}' creada exitosamente.")
            
        except Exception as e:
            print(f"❌ ERROR al crear categoría: {e}")
            messages.error(request, f"Error al crear la categoría: {e}")
        
        return redirect('administrar_categorias')
    
    return render(request, 'restaurant/administrar_categorias.html', {
        'restaurante': restaurante,
        'categorias': categorias
    })

@login_required_redirect
def editar_categoria(request, categoria_id):
    """
    Vista para editar una categoría existente - Requiere ser propietario
    """
    print(f"=== DEBUG editar_categoria ===")
    print(f"Usuario: {request.user.username} (ID: {request.user.id})")
    print(f"Categoría ID: {categoria_id}")
    
    # VERIFICACIÓN ROBUSTA DEL RESTAURANTE
    try:
        restaurante = Restaurante.objects.get(propietario=request.user, activo=True)
        print(f"✅ RESTAURANTE ENCONTRADO: {restaurante.nombre}")
        
    except Restaurante.DoesNotExist:
        print("❌ RESTAURANTE NO ENCONTRADO")
        
        # Métodos alternativos
        restaurante = Restaurante.objects.filter(propietario=request.user, activo=True).first()
        if not restaurante and hasattr(request.user, 'restaurantes'):
            restaurante = request.user.restaurantes.filter(activo=True).first()
        
        if not restaurante:
            messages.error(request, "No tienes un restaurante activo.")
            return redirect('dashboard')
    
    # VERIFICAR QUE LA CATEGORÍA PERTENEZCA AL RESTAURANTE
    try:
        categoria = Categoria.objects.get(id=categoria_id, restaurante=restaurante)
        print(f"✅ CATEGORÍA ENCONTRADA: {categoria.nombre}")
        
    except Categoria.DoesNotExist:
        print("❌ CATEGORÍA NO ENCONTRADA O NO PERTENECE AL USUARIO")
        messages.error(request, "La categoría no existe o no tienes permisos para editarla.")
        return redirect('administrar_categorias')
    
    if request.method == 'POST':
        # DEBUG: Ver datos del formulario
        print(f"📋 DATOS DEL FORMULARIO (editar):")
        for key, value in request.POST.items():
            print(f"  {key}: {value}")
        
        nombre = request.POST.get('nombre', '').strip()
        emoji = request.POST.get('emoji', '🍽️').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        
        # VALIDACIÓN
        if not nombre:
            messages.error(request, "El nombre de la categoría es obligatorio.")
            return redirect('editar_categoria', categoria_id=categoria_id)
        
        # Validar que no exista otra categoría con el mismo nombre (excluyendo la actual)
        if Categoria.objects.filter(
            restaurante=restaurante, 
            nombre__iexact=nombre
        ).exclude(id=categoria_id).exists():
            messages.error(request, f"Ya existe otra categoría con el nombre '{nombre}'.")
            return redirect('editar_categoria', categoria_id=categoria_id)
        
        try:
            # ACTUALIZAR CATEGORÍA
            categoria.nombre = nombre
            categoria.emoji = emoji
            categoria.descripcion = descripcion
            categoria.save()
            
            print(f"✅ CATEGORÍA ACTUALIZADA: {categoria.nombre}")
            messages.success(request, f'Categoría "{categoria.nombre}" actualizada exitosamente.')
            return redirect('administrar_categorias')
            
        except Exception as e:
            print(f"❌ ERROR al actualizar categoría: {e}")
            messages.error(request, f"Error al actualizar la categoría: {e}")
    
    # Para GET, mostrar formulario con datos actuales
    context = {
        'categoria': categoria,
        'restaurante': restaurante,
    }
    return render(request, 'restaurant/editar_categoria.html', context)

@login_required_redirect
def eliminar_categoria(request, categoria_id):
    """
    Vista para eliminar una categoría - Requiere ser propietario
    """
    print(f"=== DEBUG eliminar_categoria ===")
    print(f"Usuario: {request.user.username} (ID: {request.user.id})")
    print(f"Categoría ID: {categoria_id}")
    
    # VERIFICACIÓN ROBUSTA DEL RESTAURANTE
    try:
        restaurante = Restaurante.objects.get(propietario=request.user, activo=True)
        print(f"✅ RESTAURANTE ENCONTRADO: {restaurante.nombre}")
        
    except Restaurante.DoesNotExist:
        print("❌ RESTAURANTE NO ENCONTRADO")
        
        # Métodos alternativos
        restaurante = Restaurante.objects.filter(propietario=request.user, activo=True).first()
        if not restaurante and hasattr(request.user, 'restaurantes'):
            restaurante = request.user.restaurantes.filter(activo=True).first()
        
        if not restaurante:
            messages.error(request, "No tienes un restaurante activo.")
            return redirect('dashboard')
    
    # VERIFICAR QUE LA CATEGORÍA PERTENEZCA AL RESTAURANTE
    try:
        categoria = Categoria.objects.get(id=categoria_id, restaurante=restaurante)
        print(f"✅ CATEGORÍA ENCONTRADA: {categoria.nombre}")
        
    except Categoria.DoesNotExist:
        print("❌ CATEGORÍA NO ENCONTRADA O NO PERTENECE AL USUARIO")
        messages.error(request, "La categoría no existe o no tienes permisos para eliminarla.")
        return redirect('administrar_categorias')
    
    if request.method == 'POST':
        try:
            nombre_categoria = categoria.nombre
            categoria.delete()
            
            print(f"✅ CATEGORÍA ELIMINADA: {nombre_categoria}")
            messages.success(request, f'Categoría "{nombre_categoria}" eliminada exitosamente.')
            return redirect('administrar_categorias')
            
        except Exception as e:
            print(f"❌ ERROR al eliminar categoría: {e}")
            messages.error(request, f"Error al eliminar la categoría: {e}")
    
    context = {
        'categoria': categoria,
        'restaurante': restaurante,
    }
    return render(request, 'restaurant/eliminar_categoria.html', context)
# ==================== GESTIÓN DE PLATOS ====================
# restaurant/views.py - ACTUALIZA ESTAS VISTAS:

@login_required_redirect
def administrar_platos(request):
    """
    Vista para gestionar platos del restaurante - Requiere ser propietario
    """
    print(f"=== DEBUG administrar_platos ===")
    print(f"Usuario: {request.user.username} (ID: {request.user.id})")
    
    # DEBUG: Verificar todas las formas de encontrar el restaurante
    try:
        # Método 1: El que estás usando actualmente
        restaurante = Restaurante.objects.get(propietario=request.user, activo=True)
        print(f"✅ MÉTODO 1 EXITOSO: {restaurante.nombre}")
        
    except Restaurante.DoesNotExist:
        print("❌ MÉTODO 1 FALLÓ: Restaurante.DoesNotExist")
        
        # DEBUG: Ver qué restaurantes existen para este usuario
        todos_restaurantes_usuario = Restaurante.objects.filter(propietario=request.user)
        print(f"Restaurantes del usuario: {todos_restaurantes_usuario.count()}")
        for r in todos_restaurantes_usuario:
            print(f"  - {r.nombre} (Activo: {r.activo})")
        
        # DEBUG: Verificar con filter
        restaurante_filter = Restaurante.objects.filter(propietario=request.user, activo=True).first()
        if restaurante_filter:
            print(f"✅ FILTER ENCONTRÓ: {restaurante_filter.nombre}")
            restaurante = restaurante_filter
        else:
            print("❌ FILTER TAMBIÉN FALLÓ")
            
            # DEBUG: Verificar related_name
            if hasattr(request.user, 'restaurantes'):
                restaurante_related = request.user.restaurantes.filter(activo=True).first()
                if restaurante_related:
                    print(f"✅ RELATED_NAME ENCONTRÓ: {restaurante_related.nombre}")
                    restaurante = restaurante_related
                else:
                    print("❌ RELATED_NAME TAMBIÉN FALLÓ")
            
            # Verificar si tiene solicitudes aprobadas recientemente
            solicitud_aprobada = SolicitudRestaurante.objects.filter(
                usuario=request.user, 
                estado='APROBADO'
            ).first()
            
            if solicitud_aprobada:
                print(f"📋 SOLICITUD APROBADA ENCONTRADA: {solicitud_aprobada.nombre_restaurante}")
                messages.info(request, f"Tu restaurante '{solicitud_aprobada.nombre_restaurante}' fue aprobado. Recargando...")
                return redirect('dashboard')
            else:
                print("❌ NO HAY SOLICITUDES APROBADAS")
                messages.error(request, "No tienes un restaurante activo. Primero necesitas crear un restaurante.")
                return redirect('solicitar_restaurante')
    
    except Exception as e:
        print(f"❌ ERROR INESPERADO: {e}")
        messages.error(request, f"Error al acceder a tu restaurante: {e}")
        return redirect('dashboard')
    
    print(f"✅ RESTAURANTE FINAL: {restaurante.nombre}")
    print("=======================")
    
    # Obtener categorías del restaurante
    categorias = Categoria.objects.filter(restaurante=restaurante, activa=True)
    
    # Obtener platos del restaurante
    platos = Plato.objects.filter(categoria__restaurante=restaurante)
    
    if request.method == 'POST':
        # Lógica para agregar nuevo plato
        categoria_id = request.POST.get('categoria')
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        precio = request.POST.get('precio')
        stock = request.POST.get('stock', 0)
        imagen = request.FILES.get('imagen')
        
        # Validar que la categoría pertenezca al restaurante
        try:
            categoria = Categoria.objects.get(
                id=categoria_id, 
                restaurante=restaurante,
                activa=True
            )
        except Categoria.DoesNotExist:
            messages.error(request, "La categoría seleccionada no es válida.")
            return redirect('administrar_platos')
        
        # Validar campos requeridos
        if not nombre or not precio:
            messages.error(request, "Nombre y precio son campos requeridos.")
            return redirect('administrar_platos')
        
        # Crear el plato CON el restaurante
        Plato.objects.create(
            restaurante=restaurante,
            categoria=categoria,
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
            stock=stock,
            imagen=imagen
        )
        
        messages.success(request, f"Plato '{nombre}' agregado exitosamente.")
        return redirect('administrar_platos')
    
    context = {
        'restaurante': restaurante,
        'categorias': categorias,
        'platos': platos,
    }
    return render(request, 'restaurant/administrar_platos.html', context)
@login_required_redirect
def editar_plato(request, plato_id):
    """
    Vista para editar un plato existente - Requiere ser propietario
    """
    print(f"=== DEBUG editar_plato ===")
    print(f"Usuario: {request.user.username} (ID: {request.user.id})")
    print(f"Plato ID: {plato_id}")
    
    # VERIFICACIÓN ROBUSTA DEL RESTAURANTE
    try:
        restaurante = Restaurante.objects.get(propietario=request.user, activo=True)
        print(f"✅ RESTAURANTE ENCONTRADO: {restaurante.nombre}")
        
    except Restaurante.DoesNotExist:
        print("❌ RESTAURANTE NO ENCONTRADO")
        
        # Métodos alternativos
        restaurante = Restaurante.objects.filter(propietario=request.user, activo=True).first()
        if not restaurante and hasattr(request.user, 'restaurantes'):
            restaurante = request.user.restaurantes.filter(activo=True).first()
        
        if not restaurante:
            messages.error(request, "No tienes un restaurante activo.")
            return redirect('dashboard')
    
    # VERIFICAR QUE EL PLATO PERTENEZCA AL RESTAURANTE
    try:
        plato = Plato.objects.get(id=plato_id, restaurante=restaurante)
        print(f"✅ PLATO ENCONTRADO: {plato.nombre}")
        
    except Plato.DoesNotExist:
        print("❌ PLATO NO ENCONTRADO O NO PERTENECE AL USUARIO")
        messages.error(request, "El plato no existe o no tienes permisos para editarlo.")
        return redirect('administrar_platos')
    
    # Obtener categorías del restaurante para el formulario
    categorias = Categoria.objects.filter(restaurante=restaurante, activa=True)
    
    if request.method == 'POST':
        # DEBUG: Ver datos del formulario
        print(f"📋 DATOS DEL FORMULARIO (editar plato):")
        for key, value in request.POST.items():
            print(f"  {key}: {value}")
        print(f"📁 FILES: {request.FILES}")
        
        # Obtener datos del formulario
        categoria_id = request.POST.get('categoria')
        nombre = request.POST.get('nombre', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        precio = request.POST.get('precio')
        tipo = request.POST.get('tipo', 'COMIDA')
        stock = request.POST.get('stock', 0)
        tiempo_preparacion = request.POST.get('tiempo_preparacion', 15)
        es_popular = request.POST.get('es_popular') == 'on'
        es_recomendado = request.POST.get('es_recomendado') == 'on'
        stock_ilimitado = request.POST.get('stock_ilimitado') == 'on'
        imagen = request.FILES.get('imagen')
        
        # VALIDACIONES
        if not nombre:
            messages.error(request, "El nombre del plato es obligatorio.")
            return redirect('editar_plato', plato_id=plato_id)
        
        if not precio:
            messages.error(request, "El precio del plato es obligatorio.")
            return redirect('editar_plato', plato_id=plato_id)
        
        # Validar que la categoría pertenezca al restaurante
        try:
            categoria = Categoria.objects.get(
                id=categoria_id, 
                restaurante=restaurante,
                activa=True
            )
        except Categoria.DoesNotExist:
            messages.error(request, "La categoría seleccionada no es válida.")
            return redirect('editar_plato', plato_id=plato_id)
        
        try:
            # ACTUALIZAR PLATO
            plato.categoria = categoria
            plato.nombre = nombre
            plato.descripcion = descripcion
            plato.precio = precio
            plato.tipo = tipo
            plato.stock = stock if not stock_ilimitado else 0
            plato.stock_ilimitado = stock_ilimitado
            plato.tiempo_preparacion = tiempo_preparacion
            plato.es_popular = es_popular
            plato.es_recomendado = es_recomendado
            
            if imagen:
                plato.imagen = imagen
            
            plato.save()
            
            print(f"✅ PLATO ACTUALIZADO: {plato.nombre}")
            messages.success(request, f'Plato "{plato.nombre}" actualizado exitosamente.')
            return redirect('administrar_platos')
            
        except Exception as e:
            print(f"❌ ERROR al actualizar plato: {e}")
            messages.error(request, f"Error al actualizar el plato: {e}")
    
    # Para GET, mostrar formulario con datos actuales
    context = {
        'plato': plato,
        'restaurante': restaurante,
        'categorias': categorias,
        'tipos_plato': Plato.TIPO_PLATO,
    }
    return render(request, 'restaurant/editar_plato.html', context)

@login_required_redirect
def eliminar_plato(request, plato_id):
    """
    Vista para eliminar un plato - Requiere ser propietario
    """
    print(f"=== DEBUG eliminar_plato ===")
    print(f"Usuario: {request.user.username} (ID: {request.user.id})")
    print(f"Plato ID: {plato_id}")
    
    # VERIFICACIÓN ROBUSTA DEL RESTAURANTE
    try:
        restaurante = Restaurante.objects.get(propietario=request.user, activo=True)
        print(f"✅ RESTAURANTE ENCONTRADO: {restaurante.nombre}")
        
    except Restaurante.DoesNotExist:
        print("❌ RESTAURANTE NO ENCONTRADO")
        
        # Métodos alternativos
        restaurante = Restaurante.objects.filter(propietario=request.user, activo=True).first()
        if not restaurante and hasattr(request.user, 'restaurantes'):
            restaurante = request.user.restaurantes.filter(activo=True).first()
        
        if not restaurante:
            messages.error(request, "No tienes un restaurante activo.")
            return redirect('dashboard')
    
    # VERIFICAR QUE EL PLATO PERTENEZCA AL RESTAURANTE
    try:
        plato = Plato.objects.get(id=plato_id, restaurante=restaurante)
        print(f"✅ PLATO ENCONTRADO: {plato.nombre}")
        
    except Plato.DoesNotExist:
        print("❌ PLATO NO ENCONTRADO O NO PERTENECE AL USUARIO")
        messages.error(request, "El plato no existe o no tienes permisos para eliminarlo.")
        return redirect('administrar_platos')
    
    if request.method == 'POST':
        try:
            nombre_plato = plato.nombre
            
            # Verificar si el plato está en pedidos activos
            pedidos_con_plato = plato.platopedido_set.filter(
                pedido__estado__in=['PENDIENTE', 'CONFIRMADO', 'PREPARACION']
            ).exists()
            
            if pedidos_con_plato:
                messages.error(request, f'No puedes eliminar "{nombre_plato}" porque está incluido en pedidos activos.')
                return redirect('administrar_platos')
            
            plato.delete()
            
            print(f"✅ PLATO ELIMINADO: {nombre_plato}")
            messages.success(request, f'Plato "{nombre_plato}" eliminado exitosamente.')
            return redirect('administrar_platos')
            
        except Exception as e:
            print(f"❌ ERROR al eliminar plato: {e}")
            messages.error(request, f"Error al eliminar el plato: {e}")
    
    context = {
        'plato': plato,
        'restaurante': restaurante,
    }
    return render(request, 'restaurant/eliminar_plato.html', context)

# ==================== GESTIÓN DE BEBIDAS ====================
@login_required_redirect
def administrar_bebidas(request):
    """
    Vista MEJORADA para gestionar bebidas y refrescos - Requiere ser propietario
    """
    print(f"=== 🚨 DEBUG administrar_bebidas ===")
    print(f"👤 Usuario: {request.user.username} (ID: {request.user.id})")
    
    try:
        restaurante = Restaurante.objects.get(propietario=request.user, activo=True)
        print(f"✅ Restaurante: {restaurante.nombre}")
        
    except Restaurante.DoesNotExist:
        print("❌ No tiene restaurante activo")
        messages.error(request, "No tienes un restaurante activo.")
        return redirect('dashboard')
    
    # PRIMERO: PROCESAR FORMULARIOS POST (esto debe ir ANTES de calcular estadísticas)
    if request.method == 'POST':
        accion = request.POST.get('accion')
        
        if accion == 'crear_bebida':
            # Lógica para crear nueva bebida
            try:
                categoria_id = request.POST.get('categoria')
                nombre = request.POST.get('nombre', '').strip()
                descripcion = request.POST.get('descripcion', '').strip()
                precio = request.POST.get('precio', 0)
                tipo_bebida = request.POST.get('tipo_bebida', 'REFRESCO')
                volumen_ml = request.POST.get('volumen_ml')
                stock = request.POST.get('stock', 0)
                stock_ilimitado = request.POST.get('stock_ilimitado') == 'on'
                es_popular = request.POST.get('es_popular') == 'on'
                imagen = request.FILES.get('imagen')
                
                # Validaciones
                if not nombre:
                    messages.error(request, "El nombre de la bebida es obligatorio.")
                    return redirect('administrar_bebidas')
                
                if float(precio) <= 0:
                    messages.error(request, "El precio debe ser mayor a 0.")
                    return redirect('administrar_bebidas')
                
                categoria = get_object_or_404(Categoria, id=categoria_id, restaurante=restaurante)
                
                # Crear bebida
                nueva_bebida = Plato.objects.create(
                    restaurante=restaurante,
                    categoria=categoria,
                    nombre=nombre,
                    descripcion=descripcion,
                    precio=precio,
                    tipo='BEBIDA',
                    tipo_bebida=tipo_bebida,
                    volumen_ml=volumen_ml if volumen_ml else None,
                    stock=int(stock),  # ✅ Convertir a entero aquí también
                    stock_ilimitado=stock_ilimitado,
                    es_popular=es_popular,
                    imagen=imagen,
                    activo=True,
                    tiempo_preparacion=2
                )
                
                print(f"✅ Bebida creada: {nueva_bebida.nombre}")
                messages.success(request, f"🍹 Bebida '{nombre}' creada exitosamente!")
                
            except Exception as e:
                print(f"❌ Error creando bebida: {e}")
                messages.error(request, f"Error al crear la bebida: {str(e)}")
        
        elif accion == 'toggle_activo':
            # Activar/desactivar bebida
            bebida_id = request.POST.get('bebida_id')
            try:
                bebida = Plato.objects.get(id=bebida_id, restaurante=restaurante, tipo='BEBIDA')
                bebida.activo = not bebida.activo
                bebida.save()
                
                estado = "activada" if bebida.activo else "desactivada"
                messages.success(request, f"Bebida {estado} correctamente.")
                
            except Plato.DoesNotExist:
                messages.error(request, "Bebida no encontrada.")
        
        elif accion == 'actualizar_stock':
            # Actualizar stock rápido - CORREGIDO: convertir a entero
            bebida_id = request.POST.get('bebida_id')
            nuevo_stock = request.POST.get('nuevo_stock', 0)
            try:
                bebida = Plato.objects.get(id=bebida_id, restaurante=restaurante, tipo='BEBIDA')
                bebida.stock = int(nuevo_stock)  # ✅ CONVERTIR A ENTERO
                bebida.save()
                
                print(f"✅ Stock actualizado: {bebida.nombre} -> {nuevo_stock}")
                messages.success(request, f"Stock de {bebida.nombre} actualizado a {nuevo_stock}.")
                
            except (Plato.DoesNotExist, ValueError) as e:
                messages.error(request, "Error al actualizar stock.")
        
        # REDIRIGIR DESPUÉS DE PROCESAR POST para evitar reenvío
        return redirect('administrar_bebidas')
    
    # SEGUNDO: OBTENER DATOS (después de procesar POST)
    bebidas = Plato.objects.filter(
        restaurante=restaurante,
        tipo='BEBIDA'
    ).select_related('categoria').order_by('categoria__orden', 'nombre')
    
    # DEBUG: Verificar los datos actuales
    print("=== 🧪 DEBUG - BEBIDAS ENCONTRADAS ===")
    for bebida in bebidas:
        print(f"🍹 {bebida.nombre} | Stock: {bebida.stock} | Tipo: {type(bebida.stock)} | Activo: {bebida.activo}")
    
    # ESTADÍSTICAS ACTUALIZADAS (se calculan DESPUÉS de los cambios)
    stats = {
        'total_bebidas': bebidas.count(),
        'con_stock': bebidas.filter(
            Q(stock_ilimitado=True) | Q(stock__gt=0)
        ).count(),
        'sin_stock': bebidas.filter(
            stock_ilimitado=False, 
            stock=0
        ).count(),
        'populares': bebidas.filter(es_popular=True).count(),
        'por_tipo': {
            'REFRESCO': bebidas.filter(tipo_bebida='REFRESCO').count(),
            'ALCOHOLICA': bebidas.filter(tipo_bebida='ALCOHOLICA').count(),
            'JUGOS': bebidas.filter(tipo_bebida='JUGOS').count(),
            'CAFE': bebidas.filter(tipo_bebida='CAFE').count(),
            'SMOOTHIE': bebidas.filter(tipo_bebida='SMOOTHIE').count(),
            'AGUA': bebidas.filter(tipo_bebida='AGUA').count(),
        }
    }
    
    print(f"📊 Estadísticas bebidas ACTUALIZADAS: {stats}")
    
    # FILTRADO (si viene por GET)
    tipo_filtro = request.GET.get('tipo', '')
    if tipo_filtro:
        bebidas = bebidas.filter(tipo_bebida=tipo_filtro)
        print(f"🔍 Filtrado por tipo: {tipo_filtro}")
    
    categoria_filtro = request.GET.get('categoria', '')
    if categoria_filtro:
        bebidas = bebidas.filter(categoria_id=categoria_filtro)
        print(f"🔍 Filtrado por categoría ID: {categoria_filtro}")
    
    busqueda = request.GET.get('busqueda', '')
    if busqueda:
        bebidas = bebidas.filter(nombre__icontains=busqueda)
        print(f"🔍 Búsqueda: {busqueda}")
    
    # OBTENER CATEGORÍAS
    categorias = Categoria.objects.filter(restaurante=restaurante, activa=True)
    
    # CREAR CATEGORÍA DE BEBIDAS SI NO EXISTE
    categoria_bebidas, created = Categoria.objects.get_or_create(
        restaurante=restaurante,
        nombre='BEBIDAS Y REFRESCOS',
        defaults={
            'emoji': '🥤',
            'descripcion': 'Nuestra selección de bebidas y refrescos',
            'orden': 999,
            'activa': True
        }
    )
    
    if created:
        print(f"✅ Categoría bebidas creada: {categoria_bebidas.nombre}")
    
    context = {
        'restaurante': restaurante,
        'bebidas': bebidas,
        'categorias': categorias,
        'categoria_bebidas': categoria_bebidas,
        'stats': stats,
        'tipos_bebida': Plato.TIPO_BEBIDA,
        'filtros': {
            'tipo': tipo_filtro,
            'categoria': categoria_filtro,
            'busqueda': busqueda,
        }
    }

    
    return render(request, 'restaurant/administrar_bebidas.html', context)
# ==================== GESTIÓN DE ANUNCIOS ====================
@login_required_redirect
def administrar_anuncios(request):
    """
    Vista para gestionar anuncios del restaurante - Requiere ser propietario
    """
    print(f"=== DEBUG administrar_anuncios ===")
    print(f"Usuario: {request.user.username} (ID: {request.user.id})")
    
    try:
        restaurante = Restaurante.objects.get(propietario=request.user, activo=True)
        print(f"✅ MÉTODO 1 EXITOSO: {restaurante.nombre}")
        
    except Restaurante.DoesNotExist:
        print("❌ MÉTODO 1 FALLÓ: Restaurante.DoesNotExist")
        
        # Métodos alternativos
        restaurante = Restaurante.objects.filter(propietario=request.user, activo=True).first()
        if not restaurante and hasattr(request.user, 'restaurantes'):
            restaurante = request.user.restaurantes.filter(activo=True).first()
        
        if not restaurante:
            messages.error(request, "No tienes un restaurante activo.")
            return redirect('dashboard')
    
    print(f"✅ RESTAURANTE FINAL: {restaurante.nombre}")
    print("=======================")
    
    if request.method == 'POST':
        # DEBUG: Ver datos del formulario
        print(f"📋 DATOS DEL FORMULARIO (anuncio):")
        for key, value in request.POST.items():
            print(f"  {key}: {value}")
        
        titulo = request.POST.get('titulo', '').strip()
        mensaje = request.POST.get('mensaje', '').strip()
        fecha_inicio = request.POST.get('fecha_inicio')
        fecha_fin = request.POST.get('fecha_fin')
        destacado = request.POST.get('destacado') == 'on'
        imagen = request.FILES.get('imagen')
        
        # VALIDACIONES
        if not titulo:
            messages.error(request, "El título del anuncio es obligatorio.")
            return redirect('administrar_anuncios')
        
        if not mensaje:
            messages.error(request, "El mensaje del anuncio es obligatorio.")
            return redirect('administrar_anuncios')
        
        if not fecha_inicio or not fecha_fin:
            messages.error(request, "Las fechas de inicio y fin son obligatorias.")
            return redirect('administrar_anuncios')
        
        try:
            # CREAR ANUNCIO
            anuncio = Anuncio.objects.create(
                restaurante=restaurante,
                titulo=titulo,
                mensaje=mensaje,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                destacado=destacado,
                imagen=imagen
            )
            
            print(f"✅ ANUNCIO CREADO: {anuncio.titulo}")
            messages.success(request, 'Anuncio creado exitosamente.')
            return redirect('administrar_anuncios')
            
        except Exception as e:
            print(f"❌ ERROR al crear anuncio: {e}")
            messages.error(request, f'Error al crear el anuncio: {e}')
    
    anuncios = restaurante.anuncios.all()
    
    return render(request, 'restaurant/administrar_anuncios.html', {
        'restaurante': restaurante,
        'anuncios': anuncios,
    })

@login_required_redirect
def editar_anuncio(request, anuncio_id):
    """
    Vista para editar un anuncio existente - Requiere ser propietario
    """
    print(f"=== DEBUG editar_anuncio ===")
    print(f"Usuario: {request.user.username} (ID: {request.user.id})")
    print(f"Anuncio ID: {anuncio_id}")
    
    # VERIFICACIÓN ROBUSTA DEL RESTAURANTE
    try:
        restaurante = Restaurante.objects.get(propietario=request.user, activo=True)
        print(f"✅ RESTAURANTE ENCONTRADO: {restaurante.nombre}")
        
    except Restaurante.DoesNotExist:
        print("❌ RESTAURANTE NO ENCONTRADO")
        
        # Métodos alternativos
        restaurante = Restaurante.objects.filter(propietario=request.user, activo=True).first()
        if not restaurante and hasattr(request.user, 'restaurantes'):
            restaurante = request.user.restaurantes.filter(activo=True).first()
        
        if not restaurante:
            messages.error(request, "No tienes un restaurante activo.")
            return redirect('dashboard')
    
    # VERIFICAR QUE EL ANUNCIO PERTENEZCA AL RESTAURANTE
    try:
        anuncio = Anuncio.objects.get(id=anuncio_id, restaurante=restaurante)
        print(f"✅ ANUNCIO ENCONTRADO: {anuncio.titulo}")
        
    except Anuncio.DoesNotExist:
        print("❌ ANUNCIO NO ENCONTRADO O NO PERTENECE AL USUARIO")
        messages.error(request, "El anuncio no existe o no tienes permisos para editarlo.")
        return redirect('administrar_anuncios')
    
    if request.method == 'POST':
        # DEBUG: Ver datos del formulario
        print(f"📋 DATOS DEL FORMULARIO (editar anuncio):")
        for key, value in request.POST.items():
            print(f"  {key}: {value}")
        
        titulo = request.POST.get('titulo', '').strip()
        mensaje = request.POST.get('mensaje', '').strip()
        fecha_inicio = request.POST.get('fecha_inicio')
        fecha_fin = request.POST.get('fecha_fin')
        destacado = request.POST.get('destacado') == 'on'
        activo = request.POST.get('activo') == 'on'
        imagen = request.FILES.get('imagen')
        
        # VALIDACIONES
        if not titulo:
            messages.error(request, "El título del anuncio es obligatorio.")
            return redirect('editar_anuncio', anuncio_id=anuncio_id)
        
        if not mensaje:
            messages.error(request, "El mensaje del anuncio es obligatorio.")
            return redirect('editar_anuncio', anuncio_id=anuncio_id)
        
        if not fecha_inicio or not fecha_fin:
            messages.error(request, "Las fechas de inicio y fin son obligatorias.")
            return redirect('editar_anuncio', anuncio_id=anuncio_id)
        
        try:
            # ACTUALIZAR ANUNCIO
            anuncio.titulo = titulo
            anuncio.mensaje = mensaje
            anuncio.fecha_inicio = fecha_inicio
            anuncio.fecha_fin = fecha_fin
            anuncio.destacado = destacado
            anuncio.activo = activo
            
            if imagen:
                anuncio.imagen = imagen
            
            anuncio.save()
            
            print(f"✅ ANUNCIO ACTUALIZADO: {anuncio.titulo}")
            messages.success(request, 'Anuncio actualizado exitosamente.')
            return redirect('administrar_anuncios')
            
        except Exception as e:
            print(f"❌ ERROR al actualizar anuncio: {e}")
            messages.error(request, f'Error al actualizar el anuncio: {e}')
    
    # Para GET, mostrar formulario con datos actuales
    context = {
        'anuncio': anuncio,
        'restaurante': restaurante,
    }
    return render(request, 'restaurant/editar_anuncio.html', context)

@login_required_redirect
def eliminar_anuncio(request, anuncio_id):
    """
    Vista para eliminar un anuncio - Requiere ser propietario
    """
    print(f"=== DEBUG eliminar_anuncio ===")
    print(f"Usuario: {request.user.username} (ID: {request.user.id})")
    print(f"Anuncio ID: {anuncio_id}")
    
    # VERIFICACIÓN ROBUSTA DEL RESTAURANTE
    try:
        restaurante = Restaurante.objects.get(propietario=request.user, activo=True)
        print(f"✅ RESTAURANTE ENCONTRADO: {restaurante.nombre}")
        
    except Restaurante.DoesNotExist:
        print("❌ RESTAURANTE NO ENCONTRADO")
        
        # Métodos alternativos
        restaurante = Restaurante.objects.filter(propietario=request.user, activo=True).first()
        if not restaurante and hasattr(request.user, 'restaurantes'):
            restaurante = request.user.restaurantes.filter(activo=True).first()
        
        if not restaurante:
            messages.error(request, "No tienes un restaurante activo.")
            return redirect('dashboard')
    
    # VERIFICAR QUE EL ANUNCIO PERTENEZCA AL RESTAURANTE
    try:
        anuncio = Anuncio.objects.get(id=anuncio_id, restaurante=restaurante)
        print(f"✅ ANUNCIO ENCONTRADO: {anuncio.titulo}")
        
    except Anuncio.DoesNotExist:
        print("❌ ANUNCIO NO ENCONTRADO O NO PERTENECE AL USUARIO")
        messages.error(request, "El anuncio no existe o no tienes permisos para eliminarlo.")
        return redirect('administrar_anuncios')
    
    if request.method == 'POST':
        try:
            titulo_anuncio = anuncio.titulo
            anuncio.delete()
            
            print(f"✅ ANUNCIO ELIMINADO: {titulo_anuncio}")
            messages.success(request, 'Anuncio eliminado exitosamente.')
            return redirect('administrar_anuncios')
            
        except Exception as e:
            print(f"❌ ERROR al eliminar anuncio: {e}")
            messages.error(request, f'Error al eliminar el anuncio: {e}')
    
    context = {
        'anuncio': anuncio,
        'restaurante': restaurante,
    }
    return render(request, 'restaurant/eliminar_anuncio.html', context)
# ==================== SISTEMA DE PAGOS ====================
@login_required_redirect
def solicitar_restaurante(request):
    """
    Vista para solicitar crear un restaurante (sistema de pago) - Requiere autenticación
    """
    # Verificar si ya tiene un restaurante activo
    if Restaurante.objects.filter(propietario=request.user, activo=True).exists():
        messages.info(request, "Ya tienes un restaurante activo.")
        return redirect('dashboard')
    
    planes = PlanRestaurante.objects.filter(activo=True)
    cuentas_pago = CuentaPago.objects.filter(activo=True)
    
    if request.method == 'POST':
        nombre_restaurante = request.POST.get('nombre_restaurante')
        plan_id = request.POST.get('plan')
        metodo_pago = request.POST.get('metodo_pago')
        
        plan = get_object_or_404(PlanRestaurante, id=plan_id)
        
        # Crear solicitud
        solicitud = SolicitudRestaurante.objects.create(
            usuario=request.user,
            nombre_restaurante=nombre_restaurante,
            plan=plan,
            metodo_pago=metodo_pago,
            monto_pagado=plan.precio_mensual,  # Por defecto mensual
            estado='PENDIENTE'
        )
        
        return redirect('proceso_pago', solicitud_id=solicitud.id)
    
    return render(request, 'restaurant/solicitar_restaurante.html', {
        'planes': planes,
        'cuentas_pago': cuentas_pago,
    })

@login_required_redirect
def proceso_pago(request, solicitud_id):
    """Vista para mostrar los detalles de pago"""
    try:
        solicitud = SolicitudRestaurante.objects.get(id=solicitud_id, usuario=request.user)
    except SolicitudRestaurante.DoesNotExist:
        messages.error(request, "La solicitud no existe o no tienes permisos para verla.")
        return redirect('dashboard')
    
    cuenta_pago = CuentaPago.objects.filter(metodo=solicitud.metodo_pago, activo=True).first()
    
    return render(request, 'restaurant/proceso_pago.html', {
        'solicitud': solicitud,
        'cuenta_pago': cuenta_pago,
    })

@login_required_redirect
def confirmar_pago(request, solicitud_id):
    """Vista para subir comprobante de pago"""
    try:
        solicitud = SolicitudRestaurante.objects.get(id=solicitud_id, usuario=request.user)
    except SolicitudRestaurante.DoesNotExist:
        messages.error(request, "La solicitud no existe o no tienes permisos para verla.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        comprobante = request.FILES.get('comprobante')
        
        if comprobante:
            solicitud.comprobante_pago = comprobante
            solicitud.estado = 'PAGADO'
            solicitud.save()
            
            messages.success(request, "Comprobante subido exitosamente. Espera la verificación del administrador.")
            return redirect('estado_solicitud', solicitud_id=solicitud.id)
        else:
            messages.error(request, "Debes subir un comprobante de pago.")
    
    return render(request, 'restaurant/confirmar_pago.html', {
        'solicitud': solicitud,
    })

@login_required_redirect
def estado_solicitud(request, solicitud_id):
    """
    Vista para ver el estado de la solicitud - Requiere autenticación
    """
    try:
        # Solo permitir que el usuario vea SUS propias solicitudes
        solicitud = SolicitudRestaurante.objects.get(id=solicitud_id, usuario=request.user)
    except SolicitudRestaurante.DoesNotExist:
        messages.error(request, "La solicitud no existe o no tienes permisos para verla.")
        return redirect('dashboard')
    
    return render(request, 'restaurant/estado_solicitud.html', {
        'solicitud': solicitud,
    })


# ==================== SISTEMA DE PEDIDOS ====================
@login_required_redirect
def pedidos(request):
    """
    Vista para ver y gestionar pedidos (para propietarios) - Requiere ser propietario
    """
    print(f"=== DEBUG pedidos ===")
    print(f"Usuario: {request.user.username} (ID: {request.user.id})")
    
    try:
        restaurante = Restaurante.objects.get(propietario=request.user, activo=True)
        print(f"✅ MÉTODO 1 EXITOSO: {restaurante.nombre}")
        
    except Restaurante.DoesNotExist:
        print("❌ MÉTODO 1 FALLÓ: Restaurante.DoesNotExist")
        
        # Métodos alternativos
        restaurante = Restaurante.objects.filter(propietario=request.user, activo=True).first()
        if not restaurante and hasattr(request.user, 'restaurantes'):
            restaurante = request.user.restaurantes.filter(activo=True).first()
        
        if not restaurante:
            messages.error(request, "No tienes un restaurante activo.")
            return redirect('dashboard')
    
    print(f"✅ RESTAURANTE FINAL: {restaurante.nombre}")
    print("=======================")
    
    pedidos_list = restaurante.pedidos.all().select_related('usuario').prefetch_related('items')
    
    return render(request, 'restaurant/pedidos.html', {
        'restaurante': restaurante,
        'pedidos': pedidos_list
    })
# ==================== VISTAS DE CLIENTES ====================

@login_required_redirect
def mis_pedidos(request):
    """
    Vista para que los CLIENTES vean sus pedidos históricos
    """
    print(f"=== 🚨 DEBUG mis_pedidos ===")
    print(f"👤 Usuario: {request.user.username} (ID: {request.user.id})")
    
    if not request.user.is_authenticated:
        messages.error(request, "Debes iniciar sesión para ver tus pedidos.")
        return redirect('login')
    
    try:
        # CORRECTO: Filtrar por usuario y cargar relaciones
        pedidos = Pedido.objects.filter(
            usuario=request.user
        ).select_related('restaurante').prefetch_related('items__plato').order_by('-fecha_creacion')
        
        print(f"📦 Pedidos encontrados: {pedidos.count()}")
        
        for pedido in pedidos:
            print(f"   🛒 Pedido #{pedido.id}")
            print(f"      - Restaurante: {pedido.restaurante.nombre}")
            print(f"      - Estado: {pedido.estado}")
            print(f"      - Total: ${pedido.total}")
            print(f"      - Items: {pedido.items.count()}")
            
            # Debug de items
            for item in pedido.items.all():
                print(f"         🍽️ {item.plato.nombre} x{item.cantidad} = ${item.subtotal}")
        
    except Exception as e:
        print(f"❌ Error en mis_pedidos: {e}")
        pedidos = []
    
    context = {
        'pedidos': pedidos,
        'title': 'Mis Pedidos'
    }
    return render(request, 'restaurant/mis_pedidos.html', context)

@login_required_redirect
def detalle_pedido(request, pedido_id):
    """
    Vista para ver el detalle de un pedido específico
    """
    try:
        pedido = get_object_or_404(
            Pedido, 
            id=pedido_id, 
            usuario=request.user  # Solo el usuario dueño puede verlo
        )
        
        context = {
            'pedido': pedido,
            'items': pedido.items.all().select_related('plato')
        }
        return render(request, 'restaurant/detalle_pedido.html', context)
        
    except Exception as e:
        messages.error(request, "Pedido no encontrado.")
        return redirect('mis_pedidos')
    
@propietario_required
def actualizar_estado_pedido(request, pedido_id):
    """
    Vista para actualizar el estado de un pedido - Requiere ser propietario
    """
    restaurante = get_object_or_404(Restaurante, propietario=request.user)
    pedido = get_object_or_404(Pedido, id=pedido_id, restaurante=restaurante)
    
    if request.method == 'POST':
        form = PedidoForm(request.POST, instance=pedido)
        if form.is_valid():
            form.save()
            messages.success(request, f'Estado del pedido #{pedido.id} actualizado exitosamente.')
            return redirect('pedidos')
        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario.')
    else:
        form = PedidoForm(instance=pedido)
    
    return render(request, 'restaurant/actualizar_estado_pedido.html', {
        'form': form,
        'pedido': pedido
    })

@login_required_redirect
def realizar_pedido(request, restaurante_id):
    """
    Finalizar pedido y crear orden - Requiere autenticación
    """
    restaurante = get_object_or_404(Restaurante, id=restaurante_id)
    carrito = request.session.get('carrito', {}).get(str(restaurante_id), {})
    
    if not carrito or not carrito.get('items'):
        messages.error(request, "Tu carrito está vacío")
        return redirect('ver_carrito', restaurante_id=restaurante_id)
    
    if request.method == 'POST':
        try:
            # Crear pedido
            pedido = Pedido.objects.create(
                restaurante=restaurante,
                cliente=request.user,
                estado='PENDIENTE',
                total=0  # Se calculará después
            )
            
            # Agregar items al pedido
            total_pedido = 0
            items = carrito['items']
            
            for item_data in items.values():
                plato = get_object_or_404(Plato, id=item_data['plato_id'])
                
                # Crear PlatoPedido (si existe ese modelo)
                # O usar el campo items en Pedido si está configurado así
                subtotal = item_data['precio'] * item_data['cantidad']
                total_pedido += subtotal
                
                # Aquí crearías la relación entre pedido y plato
                # Depende de cómo tengas tu modelo de PedidoPlato
            
            # Actualizar total del pedido
            pedido.total = total_pedido
            pedido.save()
            
            # Limpiar carrito
            if str(restaurante_id) in request.session['carrito']:
                del request.session['carrito'][str(restaurante_id)]
                request.session.modified = True
            
            messages.success(request, f"¡Pedido realizado exitosamente! Número de pedido: #{pedido.id}")
            return redirect('pedido_resumen', pedido_id=pedido.id)
            
        except Exception as e:
            messages.error(request, f"Error al realizar el pedido: {str(e)}")
    
    context = {
        'restaurante': restaurante,
        'carrito': carrito,
    }
    return render(request, 'restaurant/realizar_pedido.html', context)

@login_required_redirect
def pedido_resumen(request, pedido_id):
    """
    Vista para ver el detalle completo de un pedido
    """
    try:
        pedido = get_object_or_404(
            Pedido, 
            id=pedido_id, 
            usuario=request.user  # Solo el dueño puede verlo
        )
        
        context = {
            'pedido': pedido,
            'items': pedido.items.all().select_related('plato')
        }
        return render(request, 'restaurant/pedido_resumen.html', context)
        
    except Exception as e:
        print(f"❌ Error en pedido_resumen: {e}")
        messages.error(request, "Pedido no encontrado.")
        return redirect('mis_pedidos')
    
# ==================== PERFIL DE USUARIO ====================
@login_required_redirect
def perfil_usuario(request):
    """
    Vista para gestionar el perfil del usuario - Requiere autenticación
    """
    perfil, created = PerfilUsuario.objects.get_or_create(usuario=request.user)
    
    if request.method == 'POST':
        form = PerfilUsuarioForm(request.POST, request.FILES, instance=perfil)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado exitosamente.')
            return redirect('perfil_usuario')
        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario.')
    else:
        form = PerfilUsuarioForm(instance=perfil)
    
    return render(request, 'restaurant/perfil_usuario.html', {
        'form': form,
        'perfil': perfil
    })

# ==================== VISTAS DE ADMINISTRACIÓN ====================
@staff_required
def admin_dashboard(request):
    """
    Dashboard de administración con estadísticas completas - Requiere staff
    """
    # Estadísticas generales
    total_restaurantes = Restaurante.objects.count()
    total_usuarios = User.objects.count()
    total_solicitudes = SolicitudRestaurante.objects.count()
    
    # Solicitudes por estado
    solicitudes_pendientes = SolicitudRestaurante.objects.filter(estado='PENDIENTE').count()
    solicitudes_pagadas = SolicitudRestaurante.objects.filter(estado='PAGADO').count()
    solicitudes_aprobadas = SolicitudRestaurante.objects.filter(estado='APROBADO').count()
    solicitudes_rechazadas = SolicitudRestaurante.objects.filter(estado='RECHAZADO').count()
    
    # Ingresos
    solicitudes_pagadas_obj = SolicitudRestaurante.objects.filter(estado__in=['PAGADO', 'APROBADO'])
    ingresos_totales = sum(s.monto_pagado for s in solicitudes_pagadas_obj)
    
    # Métodos de pago más usados
    metodos_pago = SolicitudRestaurante.objects.values('metodo_pago').annotate(
        total=Count('id')
    ).order_by('-total')
    
    # Solicitudes recientes
    solicitudes_recientes = SolicitudRestaurante.objects.all().order_by('-fecha_solicitud')[:5]
    
    # Restaurantes recientes
    restaurantes_recientes = Restaurante.objects.all().order_by('-id')[:5]
    
    context = {
        'total_restaurantes': total_restaurantes,
        'total_usuarios': total_usuarios,
        'total_solicitudes': total_solicitudes,
        'solicitudes_pendientes': solicitudes_pendientes,
        'solicitudes_pagadas': solicitudes_pagadas,
        'solicitudes_aprobadas': solicitudes_aprobadas,
        'solicitudes_rechazadas': solicitudes_rechazadas,
        'ingresos_totales': ingresos_totales,
        'metodos_pago': metodos_pago,
        'solicitudes_recientes': solicitudes_recientes,
        'restaurantes_recientes': restaurantes_recientes,
    }
    return render(request, 'restaurant/admin_dashboard.html', context)

@staff_required
def admin_solicitudes(request):
    """
    Panel de administración completo para ver todas las solicitudes - Requiere staff
    """
    # Filtros
    estado = request.GET.get('estado', '')
    metodo_pago = request.GET.get('metodo_pago', '')
    buscar = request.GET.get('buscar', '')
    
    solicitudes = SolicitudRestaurante.objects.all().order_by('-fecha_solicitud')
    
    # Aplicar filtros
    if estado:
        solicitudes = solicitudes.filter(estado=estado)
    if metodo_pago:
        solicitudes = solicitudes.filter(metodo_pago=metodo_pago)
    if buscar:
        solicitudes = solicitudes.filter(
            Q(nombre_restaurante__icontains=buscar) |
            Q(usuario__username__icontains=buscar) |
            Q(usuario__email__icontains=buscar)
        )
    
    # Estadísticas
    total_solicitudes = SolicitudRestaurante.objects.count()
    pendientes = SolicitudRestaurante.objects.filter(estado='PENDIENTE').count()
    pagadas = SolicitudRestaurante.objects.filter(estado='PAGADO').count()
    aprobadas = SolicitudRestaurante.objects.filter(estado='APROBADO').count()
    rechazadas = SolicitudRestaurante.objects.filter(estado='RECHAZADO').count()
    
    context = {
        'solicitudes': solicitudes,
        'total_solicitudes': total_solicitudes,
        'pendientes': pendientes,
        'pagadas': pagadas,
        'aprobadas': aprobadas,
        'rechazadas': rechazadas,
        'filtro_estado': estado,
        'filtro_metodo_pago': metodo_pago,
        'filtro_buscar': buscar,
    }
    return render(request, 'restaurant/admin_solicitudes.html', context)

@staff_required
def detalle_solicitud(request, solicitud_id):
    """
    Vista detallada de una solicitud específica con todas las funcionalidades - Requiere staff
    """
    solicitud = get_object_or_404(SolicitudRestaurante, id=solicitud_id)
    
    # Verificar si ya existe un restaurante para este usuario
    tiene_restaurante = Restaurante.objects.filter(propietario=solicitud.usuario).exists()
    
    if request.method == 'POST':
        # Procesar acciones rápidas
        accion = request.POST.get('accion')
        
        if accion == 'marcar_pagado':
            solicitud.estado = 'PAGADO'
            solicitud.save()
            messages.success(request, f"✅ Solicitud marcada como PAGADA")
            # Enviar email de confirmación
            enviar_email_solicitud_recibida(solicitud)
            
        elif accion == 'marcar_pendiente':
            solicitud.estado = 'PENDIENTE'
            solicitud.save()
            messages.success(request, f"🔄 Solicitud marcada como PENDIENTE")
            
        elif accion == 'notificar_usuario':
            # Reenviar email de estado actual
            if solicitud.estado == 'PAGADO':
                enviar_email_solicitud_recibida(solicitud)
            elif solicitud.estado == 'APROBADO':
                restaurante = Restaurante.objects.filter(propietario=solicitud.usuario).first()
                if restaurante:
                    enviar_email_solicitud_aprobada(solicitud, restaurante)
            messages.success(request, f"📧 Notificación enviada al usuario")
    
    context = {
        'solicitud': solicitud,
        'tiene_restaurante': tiene_restaurante,
    }
    return render(request, 'restaurant/detalle_solicitud.html', context)

@staff_required
def aprobar_solicitud(request, solicitud_id):
    """
    Aprobar una solicitud y crear el restaurante automáticamente
    """
    solicitud = get_object_or_404(SolicitudRestaurante, id=solicitud_id)
    
    if solicitud.estado != 'PAGADO':
        messages.error(request, "Solo se pueden aprobar solicitudes con pago verificado.")
        return redirect('detalle_solicitud', solicitud_id=solicitud.id)
    
    # Verificar que el usuario no tenga ya un restaurante ACTIVO
    if Restaurante.objects.filter(propietario=solicitud.usuario, activo=True).exists():
        messages.error(request, "Este usuario ya tiene un restaurante activo.")
        return redirect('detalle_solicitud', solicitud_id=solicitud.id)
    
    try:
        # ✅ CORREGIDO: Solo campos que EXISTEN en el modelo Restaurante
        restaurante = Restaurante.objects.create(
            propietario=solicitud.usuario,
            nombre=solicitud.nombre_restaurante,
            direccion="Dirección pendiente de actualización",
            telefono="Teléfono pendiente",
            email=solicitud.usuario.email,
            activo=True
        )
        
        # Actualizar solicitud
        solicitud.estado = 'APROBADO'
        solicitud.fecha_aprobacion = timezone.now()
        solicitud.save()
        
        # DEBUG
        print(f"✅ RESTAURANTE CREADO: {restaurante.nombre} (ID: {restaurante.id})")
        
        # Enviar email de aprobación (si existe la función)
        try:
            enviar_email_solicitud_aprobada(solicitud, restaurante)
        except:
            print("⚠️ Función de email no disponible")
        
        messages.success(request, f"✅ Restaurante '{solicitud.nombre_restaurante}' aprobado exitosamente.")
        
    except Exception as e:
        print(f"❌ ERROR al crear restaurante: {str(e)}")
        messages.error(request, f"❌ Error al crear el restaurante: {str(e)}")
    
    return redirect('detalle_solicitud', solicitud_id=solicitud.id)

@staff_required
def rechazar_solicitud(request, solicitud_id):
    """
    Rechazar una solicitud con motivo detallado - Requiere staff
    """
    solicitud = get_object_or_404(SolicitudRestaurante, id=solicitud_id)
    
    if request.method == 'POST':
        motivo = request.POST.get('motivo', '').strip()
        
        if not motivo:
            messages.error(request, "Debes proporcionar un motivo para el rechazo.")
            return redirect('detalle_solicitud', solicitud_id=solicitud.id)
        
        # Actualizar solicitud
        solicitud.estado = 'RECHAZADO'
        solicitud.save()
        
        # Enviar email de rechazo
        enviar_email_solicitud_rechazada(solicitud, motivo)
        
        messages.success(request, f"❌ Solicitud rechazada. Se ha enviado email al usuario con el motivo.")
        return redirect('admin_solicitudes')
    
    context = {
        'solicitud': solicitud,
    }
    return render(request, 'restaurant/rechazar_solicitud.html', context)


@login_required_redirect
def editar_bebida(request, bebida_id):
    """
    Vista para editar una bebida específica
    """
    restaurante = get_object_or_404(Restaurante, propietario=request.user, activo=True)
    bebida = get_object_or_404(Plato, id=bebida_id, restaurante=restaurante, tipo='BEBIDA')
    
    if request.method == 'POST':
        try:
            bebida.nombre = request.POST.get('nombre', bebida.nombre)
            bebida.descripcion = request.POST.get('descripcion', bebida.descripcion)
            bebida.categoria_id = request.POST.get('categoria', bebida.categoria_id)
            bebida.tipo_bebida = request.POST.get('tipo_bebida', bebida.tipo_bebida)
            bebida.precio = request.POST.get('precio', bebida.precio)
            bebida.volumen_ml = request.POST.get('volumen_ml') or None
            bebida.stock = request.POST.get('stock', bebida.stock)
            bebida.stock_ilimitado = request.POST.get('stock_ilimitado') == 'on'
            bebida.es_popular = request.POST.get('es_popular') == 'on'
            bebida.activo = request.POST.get('activo') == 'on'
            
            if 'imagen' in request.FILES:
                bebida.imagen = request.FILES['imagen']
            
            bebida.save()
            messages.success(request, f"Bebida '{bebida.nombre}' actualizada correctamente.")
            return redirect('administrar_bebidas')
            
        except Exception as e:
            messages.error(request, f"Error al actualizar la bebida: {str(e)}")
    
    categorias = Categoria.objects.filter(restaurante=restaurante, activa=True)
    
    context = {
        'restaurante': restaurante,
        'bebida': bebida,
        'categorias': categorias,
        'tipos_bebida': Plato.TIPO_BEBIDA,
    }
    return render(request, 'restaurant/editar_bebida.html', context)

@login_required_redirect
def eliminar_bebida(request, bebida_id):
    """
    Vista para eliminar (desactivar) una bebida
    """
    restaurante = get_object_or_404(Restaurante, propietario=request.user, activo=True)
    bebida = get_object_or_404(Plato, id=bebida_id, restaurante=restaurante, tipo='BEBIDA')
    
    if request.method == 'POST':
        nombre_bebida = bebida.nombre
        bebida.activo = False
        bebida.save()
        
        messages.success(request, f"Bebida '{nombre_bebida}' eliminada correctamente.")
        return redirect('administrar_bebidas')
    
    context = {
        'restaurante': restaurante,
        'bebida': bebida,
    }
    return render(request, 'restaurant/eliminar_bebida.html', context)




# restaurant/views.py - AGREGAR TEMPORALMENTE:

@login_required
def diagnostico_restaurante(request):
    """
    Vista de diagnóstico para verificar el estado del restaurante
    """
    user = request.user
    
    # Verificar diferentes métodos
    tiene_restaurante_filter = Restaurante.objects.filter(propietario=user, activo=True).exists()
    tiene_restaurante_related = hasattr(user, 'restaurantes') and user.restaurantes.filter(activo=True).exists()
    
    restaurantes = Restaurante.objects.filter(propietario=user)
    solicitudes = SolicitudRestaurante.objects.filter(usuario=user)
    
    context = {
        'user': user,
        'tiene_restaurante_filter': tiene_restaurante_filter,
        'tiene_restaurante_related': tiene_restaurante_related,
        'restaurantes': list(restaurantes),
        'solicitudes': list(solicitudes),
    }
    
    return render(request, 'restaurant/diagnostico.html', context)

# restaurant/views.py
@login_required
def debug_restaurante(request):
    """Vista de debug temporal"""
    user = request.user
    
    # Todas las verificaciones posibles
    data = {
        'user': user.username,
        'user_id': user.id,
        'restaurantes_count': Restaurante.objects.filter(propietario=user).count(),
        'restaurantes_activos_count': Restaurante.objects.filter(propietario=user, activo=True).count(),
        'solicitudes_count': SolicitudRestaurante.objects.filter(usuario=user).count(),
        'solicitudes_aprobadas': SolicitudRestaurante.objects.filter(usuario=user, estado='APROBADO').count(),
    }
    
    # Detalles de restaurantes
    restaurantes = Restaurante.objects.filter(propietario=user)
    data['restaurantes'] = [
        {'id': r.id, 'nombre': r.nombre, 'activo': r.activo} 
        for r in restaurantes
    ]
    
    # Detalles de solicitudes
    solicitudes = SolicitudRestaurante.objects.filter(usuario=user)
    data['solicitudes'] = [
        {'id': s.id, 'nombre': s.nombre_restaurante, 'estado': s.estado}
        for s in solicitudes
    ]
    
    return JsonResponse(data)

# restaurant/views.py - AGREGA esta vista COMPLETA
def platos_por_categoria(request, categoria_id):
    """
    Vista para mostrar restaurantes y platos por categoría
    """
    print(f"=== 🚨 DEBUG platos_por_categoria ===")
    print(f"📥 Categoría ID recibido: {categoria_id}")
    
    try:
        # 1. OBTENER CATEGORÍA
        categoria = Categoria.objects.get(id=categoria_id, activa=True)
        print(f"✅ Categoría encontrada: '{categoria.nombre}'")
        
        # 2. OBTENER RESTAURANTES QUE TIENEN ESTA CATEGORÍA
        restaurantes_ids = Plato.objects.filter(
            categoria=categoria,
            activo=True
        ).values_list('restaurante_id', flat=True).distinct()
        
        restaurantes = Restaurante.objects.filter(
            id__in=restaurantes_ids,
            activo=True
        )
        
        print(f"🏪 Restaurantes con esta categoría: {restaurantes.count()}")
        
        # 3. OBTENER PLATOS DESTACADOS
        platos_destacados = Plato.objects.filter(
            categoria=categoria,
            activo=True,
            es_popular=True
        )[:6]
        
        print(f"⭐ Platos destacados: {platos_destacados.count()}")
        
    except Categoria.DoesNotExist:
        print("❌ Categoría no encontrada o inactiva")
        # CORRECCIÓN: Usar 'index' que es tu URL de inicio
        messages.error(request, "La categoría no existe o no está disponible.")
        return redirect('index')
    except Exception as e:
        print(f"❌ Error en platos_por_categoria: {e}")
        messages.error(request, "Error al cargar la categoría.")
        return redirect('index')
    
    print("=== 🏁 DEBUG platos_por_categoria FINALIZADO ===")
    
    context = {
        'categoria': categoria,
        'restaurantes': restaurantes,
        'platos_destacados': platos_destacados,
    }
    return render(request, 'restaurant/platos_por_categoria.html', context)


#nuevas vistas 


# ==================== SISTEMA COMPLETO PARA USUARIOS NO REGISTRADOS ====================

def explorar_restaurantes(request):
    """
    Página principal mejorada para explorar todos los restaurantes - Pública
    """
    restaurantes = Restaurante.objects.filter(activo=True, propietario__isnull=False)
    
    # Filtros
    query = request.GET.get('q', '')
    categoria_filter = request.GET.get('categoria', '')
    
    if query:
        restaurantes = restaurantes.filter(
            Q(nombre__icontains=query) |
            Q(direccion__icontains=query) |
            Q(platos__nombre__icontains=query)
        ).distinct()
    
    if categoria_filter:
        restaurantes = restaurantes.filter(
            Q(categorias__nombre__icontains=categoria_filter) |
            Q(platos__categoria__nombre__icontains=categoria_filter)
        ).distinct()
    
    # CORRECCIÓN: Obtener categorías de forma segura
    categorias_disponibles = Categoria.objects.filter(
        restaurante__in=restaurantes,
        activa=True
    ).distinct()  # Cambiado de values().distinct() a objetos completos
    
    # Estadísticas para mostrar
    stats = {
        'total_restaurantes': restaurantes.count(),
        'restaurantes_con_resenas': restaurantes.annotate(
            num_resenas=Count('resenas')
        ).filter(num_resenas__gt=0).count(),
    }
    
    context = {
        'restaurantes': restaurantes,
        'categorias': categorias_disponibles,  # Cambiado el nombre para claridad
        'query': query,
        'categoria_filter': categoria_filter,
        'stats': stats,
    }
    return render(request, 'restaurant/explorar_restaurantes.html', context)

def detalle_restaurante(request, restaurante_id):
    """
    Página detallada del restaurante con reseñas - Pública
    """
    restaurante = get_object_or_404(Restaurante, id=restaurante_id, activo=True)
    
    # Obtener categorías con platos
    categorias_con_platos = []
    categorias = Categoria.objects.filter(restaurante=restaurante, activa=True).order_by('orden')
    
    for categoria in categorias:
        platos = Plato.objects.filter(
            categoria=categoria, 
            activo=True
        ).order_by('nombre')
        
        if platos.exists():
            categorias_con_platos.append({
                'categoria': categoria,
                'platos': platos
            })
    
    # Reseñas recientes
    reseñas_recientes = restaurante.resenas.filter(activa=True).order_by('-fecha_creacion')[:5]
    
    # CORRECCIÓN: Calcular estadísticas de reseñas manualmente
    resenas_activas = restaurante.resenas.filter(activa=True)
    
    # Calcular distribución de calificaciones
    distribucion = {
        5: resenas_activas.filter(calificacion=5).count(),
        4: resenas_activas.filter(calificacion=4).count(),
        3: resenas_activas.filter(calificacion=3).count(),
        2: resenas_activas.filter(calificacion=2).count(),
        1: resenas_activas.filter(calificacion=1).count(),
    }
    
    # Calcular promedio manualmente
    total_resenas = resenas_activas.count()
    if total_resenas > 0:
        suma_calificaciones = sum(resena.calificacion for resena in resenas_activas)
        promedio_calificaciones = round(suma_calificaciones / total_resenas, 1)
    else:
        promedio_calificaciones = 0.0
    
    estadisticas_resenas = {
        'total': total_resenas,
        'promedio': promedio_calificaciones,
        'distribucion': distribucion
    }
    
    context = {
        'restaurante': restaurante,
        'categorias_con_platos': categorias_con_platos,
        'reseñas_recientes': reseñas_recientes,
        'estadisticas_resenas': estadisticas_resenas,
    }
    return render(request, 'restaurant/detalle_restaurante.html', context)

@login_required_redirect
def checkout_pedido(request, restaurante_id):
    """
    Proceso de checkout completo con registro de dirección y teléfono
    """
    restaurante = get_object_or_404(Restaurante, id=restaurante_id, activo=True)
    carrito = request.session.get('carrito', {}).get(str(restaurante_id), {})
    
    if not carrito or not carrito.get('items'):
        messages.error(request, "Tu carrito está vacío.")
        return redirect('menu_publico', restaurante_id=restaurante_id)
    
    # Obtener o crear perfil de usuario
    perfil, created = PerfilUsuario.objects.get_or_create(usuario=request.user)
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Obtener datos del formulario
                direccion_entrega = form.cleaned_data['direccion']
                telefono_contacto = form.cleaned_data['telefono']
                metodo_pago = form.cleaned_data['metodo_pago']
                comentarios = form.cleaned_data['comentarios']
                comprobante_pago = form.cleaned_data.get('comprobante_pago')
                
                # Calcular total del carrito
                total = sum(
                    item['precio'] * item['cantidad'] 
                    for item in carrito['items'].values()
                )
                
                # Crear pedido
                pedido = Pedido.objects.create(
                    usuario=request.user,
                    restaurante=restaurante,
                    estado='PENDIENTE',
                    metodo_pago=metodo_pago,
                    total=total,
                    direccion_entrega=direccion_entrega,
                    telefono_contacto=telefono_contacto,
                    notas=comentarios,
                    comprobante_pago=comprobante_pago
                )
                
                # Crear items del pedido
                for item_data in carrito['items'].values():
                    plato = Plato.objects.get(id=item_data['plato_id'])
                    
                    PlatoPedido.objects.create(
                        pedido=pedido,
                        plato=plato,
                        cantidad=item_data['cantidad'],
                        precio_unitario=item_data['precio'],
                        notas=item_data.get('notas', '')
                    )
                
                # Actualizar perfil del usuario con dirección y teléfono
                perfil.direccion = direccion_entrega
                perfil.telefono = telefono_contacto
                perfil.save()
                
                # Limpiar carrito
                if str(restaurante_id) in request.session.get('carrito', {}):
                    del request.session['carrito'][str(restaurante_id)]
                    request.session.modified = True
                
                messages.success(request, f"¡Pedido realizado con éxito! Número de pedido: #{pedido.id}")
                return redirect('detalle_pedido_cliente', pedido_id=pedido.id)
                
            except Exception as e:
                messages.error(request, f"Error al procesar el pedido: {str(e)}")
        else:
            messages.error(request, "Por favor, corrige los errores en el formulario.")
    else:
        # Inicializar formulario con datos del perfil si existen
        initial_data = {
            'direccion': perfil.direccion or '',
            'telefono': perfil.telefono or '',
            'metodo_pago': 'EFECTIVO'
        }
        form = CheckoutForm(initial=initial_data)
    
    # Calcular totales para mostrar en el checkout
    items_carrito = carrito.get('items', {})
    subtotal = sum(item['precio'] * item['cantidad'] for item in items_carrito.values())
    impuestos = subtotal * 0.10  # 10% de impuestos
    total = subtotal + impuestos
    
    context = {
        'restaurante': restaurante,
        'carrito': carrito,
        'form': form,
        'perfil': perfil,
        'subtotal': subtotal,
        'impuestos': impuestos,
        'total': total,
    }
    return render(request, 'restaurant/checkout_pedido.html', context)

@login_required_redirect
def detalle_pedido_cliente(request, pedido_id):
    """
    Detalle del pedido para el cliente con opción de calificar
    """
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    items = pedido.items.all().select_related('plato')
    
    # Verificar si ya se pueden agregar reseñas (pedido entregado)
    puede_calificar = pedido.estado == 'ENTREGADO'
    
    # Obtener platos que aún no han sido calificados
    platos_sin_calificar = []
    if puede_calificar:
        platos_pedido = [item.plato for item in items]
        platos_calificados = Resena.objects.filter(
            pedido=pedido,
            usuario=request.user
        ).values_list('plato_id', flat=True)
        
        platos_sin_calificar = [
            plato for plato in platos_pedido 
            if plato.id not in platos_calificados
        ]
    
    context = {
        'pedido': pedido,
        'items': items,
        'puede_calificar': puede_calificar,
        'platos_sin_calificar': platos_sin_calificar,
        'resena_form': ResenaForm()  # Form para agregar reseñas
    }
    return render(request, 'restaurant/detalle_pedido_cliente.html', context)

@login_required_redirect
def agregar_resena(request, pedido_id):
    """
    Agregar reseña a un plato específico del pedido
    """
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    
    # Verificar que el pedido esté entregado
    if pedido.estado != 'ENTREGADO':
        messages.error(request, "Solo puedes calificar pedidos que han sido entregados.")
        return redirect('detalle_pedido_cliente', pedido_id=pedido_id)
    
    if request.method == 'POST':
        form = ResenaForm(request.POST)
        if form.is_valid():
            plato_id = form.cleaned_data['plato_id']
            calificacion = form.cleaned_data['calificacion']
            comentario = form.cleaned_data['comentario']
            
            try:
                plato = Plato.objects.get(id=plato_id)
                
                # Verificar que el plato pertenezca al pedido
                if not pedido.items.filter(plato=plato).exists():
                    messages.error(request, "El plato no pertenece a este pedido.")
                    return redirect('detalle_pedido_cliente', pedido_id=pedido_id)
                
                # Crear o actualizar reseña
                resena, created = Resena.objects.update_or_create(
                    pedido=pedido,
                    usuario=request.user,
                    plato=plato,
                    defaults={
                        'calificacion': calificacion,
                        'comentario': comentario,
                        'restaurante': pedido.restaurante
                    }
                )
                
                if created:
                    messages.success(request, f"¡Reseña agregada para {plato.nombre}!")
                else:
                    messages.success(request, f"¡Reseña actualizada para {plato.nombre}!")
                
                return redirect('detalle_pedido_cliente', pedido_id=pedido_id)
                
            except Plato.DoesNotExist:
                messages.error(request, "Plato no encontrado.")
        else:
            messages.error(request, "Por favor, corrige los errores en el formulario.")
    
    return redirect('detalle_pedido_cliente', pedido_id=pedido_id)

@login_required_redirect
def historial_pedidos(request):
    """
    Historial completo de pedidos del usuario
    """
    pedidos = Pedido.objects.filter(usuario=request.user).select_related(
        'restaurante'
    ).prefetch_related('items__plato').order_by('-fecha_creacion')
    
    # Estadísticas del usuario
    total_pedidos = pedidos.count()
    pedidos_entregados = pedidos.filter(estado='ENTREGADO').count()
    total_gastado = sum(pedido.total for pedido in pedidos if pedido.total)
    
    context = {
        'pedidos': pedidos,
        'total_pedidos': total_pedidos,
        'pedidos_entregados': pedidos_entregados,
        'total_gastado': total_gastado,
    }
    return render(request, 'restaurant/historial_pedidos.html', context)

# ==================== VISTAS PARA PROPIETARIOS MEJORADAS ====================

@propietario_required
def dashboard_mejorado(request):
    """
    Dashboard mejorado para propietarios con métricas de reseñas
    """
    restaurante = get_object_or_404(Restaurante, propietario=request.user, activo=True)
    
    # Métricas existentes (de tu vista dashboard) + nuevas
    total_platos = Plato.objects.filter(categoria__restaurante=restaurante, activo=True).count()
    pedidos_hoy = Pedido.objects.filter(restaurante=restaurante, fecha_creacion__date=timezone.now().date()).count()
    pedidos_pendientes = Pedido.objects.filter(restaurante=restaurante, estado__in=['PENDIENTE', 'CONFIRMADO', 'PREPARACION']).count()
    
    # Nuevas métricas de reseñas
    total_resenas = restaurante.resenas.filter(activa=True).count()
    promedio_calificaciones = restaurante.promedio_calificaciones
    resenas_recientes = restaurante.resenas.filter(activa=True).order_by('-fecha_creacion')[:5]
    
    # Pedidos recientes
    ultimos_pedidos = Pedido.objects.filter(restaurante=restaurante).order_by('-fecha_creacion')[:5]
    
    # Platos mejor calificados
    platos_populares = Plato.objects.filter(
        categoria__restaurante=restaurante,
        activo=True
    ).annotate(
        num_resenas=Count('resenas'),
        avg_rating=Avg('resenas__calificacion')
    ).filter(num_resenas__gt=0).order_by('-avg_rating')[:3]
    
    context = {
        'restaurante': restaurante,
        'total_platos': total_platos,
        'pedidos_hoy': pedidos_hoy,
        'pedidos_pendientes': pedidos_pendientes,
        'total_resenas': total_resenas,
        'promedio_calificaciones': promedio_calificaciones,
        'resenas_recientes': resenas_recientes,
        'ultimos_pedidos': ultimos_pedidos,
        'platos_populares': platos_populares,
    }
    return render(request, 'restaurant/dashboard_mejorado.html', context)

@propietario_required
def gestion_resenas(request):
    """
    Gestión de reseñas para propietarios
    """
    restaurante = get_object_or_404(Restaurante, propietario=request.user, activo=True)
    
    resenas = restaurante.resenas.filter(activa=True).select_related('usuario', 'plato').order_by('-fecha_creacion')
    
    # Estadísticas
    stats = {
        'total': resenas.count(),
        'promedio': restaurante.promedio_calificaciones,
        'por_calificacion': {
            5: resenas.filter(calificacion=5).count(),
            4: resenas.filter(calificacion=4).count(),
            3: resenas.filter(calificacion=3).count(),
            2: resenas.filter(calificacion=2).count(),
            1: resenas.filter(calificacion=1).count(),
        }
    }
    
    context = {
        'restaurante': restaurante,
        'resenas': resenas,
        'stats': stats,
    }
    return render(request, 'restaurant/gestion_resenas.html', context)