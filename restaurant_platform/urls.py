# restaurant_platform/urls.py
from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView, include
from restaurant import views
from django.conf import settings
from django.conf.urls.static import static

# Handlers de errores
handler403 = 'restaurant.views.handler403'
handler404 = 'restaurant.views.handler404'
handler500 = 'restaurant.views.handler500'

urlpatterns = [
    # Redireccionamiento temporal para imagen de categoria
    path('media/categorias/d6obuqsuu2ua1.jpg', RedirectView.as_view(url='/static/images/d6obuqsuu2ua1.jpg', permanent=False)),
    # ADMIN DE DJANGO - Debe ir PRIMERO
    path('admin/', admin.site.urls),
    
    # ==================== URLs PÚBLICAS ====================
    path('', views.index, name='index'),
    path('bienvenidos/', views.bienvenidos, name='bienvenidos'),
    path('categorias/', views.categorias, name='categorias'),
    path('restaurantes/', views.restaurantes_list, name='restaurantes'),
    path('contacto/', views.contacto, name='contacto'),
    
    # ==================== EXPLORACIÓN PÚBLICA MEJORADA ====================
    path('explorar/', views.explorar_restaurantes, name='explorar_restaurantes'),
    path('restaurante/<int:restaurante_id>/', views.detalle_restaurante, name='detalle_restaurante'),
    path('categoria/<int:categoria_id>/', views.platos_por_categoria, name='platos_por_categoria'),
    path('menu/<int:restaurante_id>/', views.menu_publico, name='menu_publico'),
    
    # ==================== AUTENTICACIÓN ====================
    path('accounts/', include('django.contrib.auth.urls')),
    path('registro/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # ==================== DASHBOARD & PANEL PROPIETARIO ====================
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard-mejorado/', views.dashboard_mejorado, name='dashboard_mejorado'),
    path('crear-restaurante/', views.crear_restaurante, name='crear_restaurante'),
    
    # ==================== GESTIÓN DE CONTENIDO ====================
    path('administrar/categorias/', views.administrar_categorias, name='administrar_categorias'),
    path('categoria/editar/<int:categoria_id>/', views.editar_categoria, name='editar_categoria'),
    path('categoria/eliminar/<int:categoria_id>/', views.eliminar_categoria, name='eliminar_categoria'),
    
    path('administrar/platos/', views.administrar_platos, name='administrar_platos'),
    path('plato/editar/<int:plato_id>/', views.editar_plato, name='editar_plato'),
    path('plato/eliminar/<int:plato_id>/', views.eliminar_plato, name='eliminar_plato'),
    
    path('administrar/bebidas/', views.administrar_bebidas, name='administrar_bebidas'),
    path('bebida/editar/<int:bebida_id>/', views.editar_bebida, name='editar_bebida'),
    path('bebida/eliminar/<int:bebida_id>/', views.eliminar_bebida, name='eliminar_bebida'),
    
    path('administrar/anuncios/', views.administrar_anuncios, name='administrar_anuncios'),
    path('anuncio/editar/<int:anuncio_id>/', views.editar_anuncio, name='editar_anuncio'),
    path('anuncio/eliminar/<int:anuncio_id>/', views.eliminar_anuncio, name='eliminar_anuncio'),
    
    # ==================== SISTEMA DE PAGOS ====================
    path('solicitar-restaurante/', views.solicitar_restaurante, name='solicitar_restaurante'),
    path('proceso-pago/<int:solicitud_id>/', views.proceso_pago, name='proceso_pago'),
    path('confirmar-pago/<int:solicitud_id>/', views.confirmar_pago, name='confirmar_pago'),
    path('estado-solicitud/<int:solicitud_id>/', views.estado_solicitud, name='estado_solicitud'),
    
    # ==================== PANEL ADMINISTRATIVO (CUSTOM) ====================
    path('administracion/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('administracion/solicitudes/', views.admin_solicitudes, name='admin_solicitudes'),
    path('administracion/solicitud/<int:solicitud_id>/', views.detalle_solicitud, name='detalle_solicitud'),
    path('administracion/aprobar-solicitud/<int:solicitud_id>/', views.aprobar_solicitud, name='aprobar_solicitud'),
    path('administracion/rechazar-solicitud/<int:solicitud_id>/', views.rechazar_solicitud, name='rechazar_solicitud'),
    
    # ==================== SISTEMA DE PEDIDOS COMPLETO ====================
    path('pedidos/', views.pedidos, name='pedidos'),
    path('pedido/actualizar/<int:pedido_id>/', views.actualizar_estado_pedido, name='actualizar_estado_pedido'),
    path('realizar-pedido/<int:restaurante_id>/', views.realizar_pedido, name='realizar_pedido'),
    path('pedido/<int:pedido_id>/', views.pedido_resumen, name='pedido_resumen'),
    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),
    path('historial-pedidos/', views.historial_pedidos, name='historial_pedidos'),
    path('mis-pedidos/<int:pedido_id>/', views.detalle_pedido, name='detalle_pedido'),
    path('pedido/<int:pedido_id>/detalle/', views.detalle_pedido_cliente, name='detalle_pedido_cliente'),
    
    # ==================== SISTEMA DE CHECKOUT Y RESEÑAS ====================
    path('checkout/<int:restaurante_id>/', views.checkout_pedido, name='checkout_pedido'),
    path('pedido/<int:pedido_id>/resena/', views.agregar_resena, name='agregar_resena'),
    path('gestion-resenas/', views.gestion_resenas, name='gestion_resenas'),
    
    # ==================== SISTEMA DE CARRITO ====================
    path('carrito/<int:restaurante_id>/', views.ver_carrito, name='ver_carrito'),
    path('carrito/<int:restaurante_id>/agregar/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/<int:restaurante_id>/actualizar/', views.actualizar_carrito, name='actualizar_carrito'),
    
    # ==================== DIAGNÓSTICO Y DEBUG ====================
    path('diagnostico/', views.diagnostico_restaurante, name='diagnostico'),
    path('debug/', views.debug_restaurante, name='debug'),
    path('menu-restaurante/<int:restaurante_id>/', views.menu_publico, name='menu_restaurante'),
    # ==================== PERFIL DE USUARIO ====================
    path('perfil/', views.perfil_usuario, name='perfil_usuario'),
]    

# Servir archivos multimedia durante el desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
