from django.db import models
from django.contrib.auth.models import User

class Restaurante(models.Model):
    # Información básica
    propietario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='restaurantes')
    nombre = models.CharField(max_length=100)
    direccion = models.TextField()
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    
    # Imágenes
    logo = models.ImageField(upload_to='restaurantes/logos/', blank=True, null=True)
    imagen_portada = models.ImageField(upload_to='restaurantes/portadas/', blank=True, null=True)
    
    # Personalización
    color_primario = models.CharField(max_length=7, default='667eea')  # Sin #
    color_secundario = models.CharField(max_length=7, default='764ba2') # Sin #
    tema = models.CharField(max_length=50, default='default')
    idioma = models.CharField(max_length=10, default='es')
    
    # Estado
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Restaurante"
        verbose_name_plural = "Restaurantes"
    
    def __str__(self):
        return f"{self.nombre} - {self.propietario.username}"

    # ✅ PROPIEDADES CORREGIDAS - DENTRO DE LA CLASE
    @property
    def promedio_calificaciones(self):
        """Calcula el promedio de calificaciones del restaurante"""
        resenas = self.resenas.filter(activa=True)
        if resenas.exists():
            return round(sum(r.calificacion for r in resenas) / resenas.count(), 1)
        return 0

    @property
    def total_resenas(self):
        """Retorna el total de reseñas del restaurante"""
        return self.resenas.filter(activa=True).count()

    @property
    def esta_abierto(self):
        """Verifica si el restaurante debería estar abierto según la hora actual"""
        from django.utils import timezone
        now = timezone.now().time()
        # Por defecto retornamos True (puedes ajustar según tu lógica)
        return True


class Categoria(models.Model):
    # Cada categoría pertenece a un restaurante específico
    restaurante = models.ForeignKey(Restaurante, on_delete=models.CASCADE, related_name='categorias')
    nombre = models.CharField(max_length=100)
    emoji = models.CharField(max_length=10, default='🍽️')  # Emoji para la categoría
    descripcion = models.TextField(blank=True, null=True)
    imagen = models.ImageField(upload_to='categorias/', blank=True, null=True)
    orden = models.IntegerField(default=0)  # Para ordenar categorías
    activa = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ['orden', 'nombre']
        unique_together = ['restaurante', 'nombre']  # No repetir nombres en mismo restaurante
    
    def __str__(self):
        return f"{self.emoji} {self.nombre} - {self.restaurante.nombre}"


class Plato(models.Model):
    TIPO_PLATO = [
        ('COMIDA', 'Comida'),
        ('BEBIDA', 'Bebida'),
        ('POSTRE', 'Postre'),
        ('ENTRADA', 'Entrada'),
    ]
    
    TIPO_BEBIDA = [
        ('REFRESCO', 'Refresco'),
        ('ALCOHOLICA', 'Bebida Alcohólica'),
        ('JUGOS', 'Jugos Naturales'),
        ('CAFE', 'Café y Té'),
        ('SMOOTHIE', 'Smoothies'),
        ('AGUA', 'Agua y Bebidas'),
    ]
    
    # Relaciones
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='platos')
    restaurante = models.ForeignKey(Restaurante, on_delete=models.CASCADE, related_name='platos')
    
    # Información básica
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    tipo = models.CharField(max_length=10, choices=TIPO_PLATO, default='COMIDA')
    tipo_bebida = models.CharField(max_length=15, choices=TIPO_BEBIDA, blank=True, null=True)
    
    # Especificaciones para bebidas
    volumen_ml = models.IntegerField(blank=True, null=True, help_text="Volumen en mililitros")
    grados_alcohol = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True, help_text="Graduación alcohólica")
    es_caliente = models.BooleanField(default=False, help_text="Para café/té caliente")
    contiene_hielo = models.BooleanField(default=True, help_text="Sirve con hielo")
    contiene_azucar = models.BooleanField(default=True, help_text="Contiene azúcar")
    
    # Precio e inventario
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    precio_promocion = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stock = models.IntegerField(default=0)
    stock_ilimitado = models.BooleanField(default=False)
    
    # Imágenes
    imagen = models.ImageField(upload_to='platos/', blank=True, null=True)
    
    # Estado y características
    activo = models.BooleanField(default=True)
    es_popular = models.BooleanField(default=False)
    es_recomendado = models.BooleanField(default=False)
    
    # Tiempos
    tiempo_preparacion = models.IntegerField(default=5, help_text="Tiempo en minutos")
    
    # Metadata
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    # ✅ PROPIEDADES CORREGIDAS - DENTRO DE LA CLASE
    @property
    def precio_actual(self):
        """Retorna el precio actual (promoción o normal)"""
        if self.precio_promocion and self.precio_promocion > 0:
            return self.precio_promocion
        return self.precio

    @property
    def promedio_calificaciones(self):
        """Calcula el promedio de calificaciones"""
        resenas = self.resenas.filter(activa=True)
        if resenas.exists():
            return round(sum(r.calificacion for r in resenas) / resenas.count(), 1)
        return 0

    @property
    def total_resenas(self):
        """Retorna el total de reseñas"""
        return self.resenas.filter(activa=True).count()

    @property
    def en_stock(self):
        """Verifica si el plato está en stock"""
        return self.stock_ilimitado or self.stock > 0

    def __str__(self):
        return self.nombre


class Anuncio(models.Model):
    restaurante = models.ForeignKey(Restaurante, on_delete=models.CASCADE, related_name='anuncios')
    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    imagen = models.ImageField(upload_to='anuncios/', blank=True, null=True)
    
    # Fechas de activación
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    
    # Estado
    activo = models.BooleanField(default=True)
    destacado = models.BooleanField(default=False)
    
    # Metadata
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Anuncio"
        verbose_name_plural = "Anuncios"
        ordering = ['-destacado', '-fecha_creacion']
    
    def __str__(self):
        return f"{self.titulo} - {self.restaurante.nombre}"
    
    @property
    def esta_activo(self):
        """Verifica si el anuncio está activo según las fechas"""
        from django.utils import timezone
        ahora = timezone.now()
        return self.activo and self.fecha_inicio <= ahora <= self.fecha_fin


class Pedido(models.Model):
    ESTADOS_PEDIDO = [
        ('PENDIENTE', 'Pendiente'),
        ('CONFIRMADO', 'Confirmado'),
        ('PREPARACION', 'En Preparación'),
        ('LISTO', 'Listo para Recoger'),
        ('EN_CAMINO', 'En Camino'),
        ('ENTREGADO', 'Entregado'),
        ('CANCELADO', 'Cancelado'),
    ]
    
    METODOS_PAGO = [
        ('EFECTIVO', 'Efectivo'),
        ('TARJETA', 'Tarjeta'),
        ('TRANSFERENCIA', 'Transferencia'),
    ]
    
    # Relaciones
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pedidos')
    restaurante = models.ForeignKey(Restaurante, on_delete=models.CASCADE, related_name='pedidos')
    
    # Información del pedido
    estado = models.CharField(max_length=20, choices=ESTADOS_PEDIDO, default='PENDIENTE')
    metodo_pago = models.CharField(max_length=20, choices=METODOS_PAGO, default='EFECTIVO')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Información de entrega
    direccion_entrega = models.TextField(blank=True, null=True)
    telefono_contacto = models.CharField(max_length=20, blank=True, null=True)
    notas = models.TextField(blank=True, null=True)
    
    # Tiempos
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_confirmacion = models.DateTimeField(blank=True, null=True)
    fecha_entrega = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"Pedido #{self.id} - {self.usuario.username} - {self.restaurante.nombre}"
    
    def calcular_total(self):
        """Calcula el total del pedido sumando todos los platos"""
        total = sum(item.subtotal for item in self.items.all())
        self.total = total
        self.save()
        return total


class PlatoPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='items')
    plato = models.ForeignKey(Plato, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    notas = models.TextField(blank=True, null=True)  # Notas específicas para este plato
    
    class Meta:
        verbose_name = "Plato en Pedido"
        verbose_name_plural = "Platos en Pedidos"
    
    def __str__(self):
        return f"{self.plato.nombre} x{self.cantidad} - Pedido #{self.pedido.id}"
    
    @property
    def subtotal(self):
        """Calcula el subtotal para este item"""
        return self.precio_unitario * self.cantidad
    
    # ✅ MÉTODO SAVE CORREGIDO - DENTRO DE LA CLASE
    def save(self, *args, **kwargs):
        # Si es nuevo, guardar el precio actual del plato
        if not self.pk and self.plato:
            self.precio_unitario = self.plato.precio_actual
        super().save(*args, **kwargs)
        # Recalcular el total del pedido
        if hasattr(self, 'pedido') and self.pedido:
            self.pedido.calcular_total()


class PerfilUsuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatares/', blank=True, null=True)
    
    # Preferencias
    tema_oscuro = models.BooleanField(default=False)
    notificaciones = models.BooleanField(default=True)
    
    # Metadata
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuario"
    
    def __str__(self):
        return f"Perfil de {self.usuario.username}"


class PlanRestaurante(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio_mensual = models.DecimalField(max_digits=10, decimal_places=2)
    precio_anual = models.DecimalField(max_digits=10, decimal_places=2)
    activo = models.BooleanField(default=True)
    
    def __str__(self):
        return self.nombre


class SolicitudRestaurante(models.Model):
    ESTADOS = [
        ('PENDIENTE', 'Pendiente de Pago'),
        ('PAGADO', 'Pago Verificado'),
        ('APROBADO', 'Aprobado'),
        ('RECHAZADO', 'Rechazado'),
    ]
    
    METODOS_PAGO = [
        ('TRANSFERENCIA', 'Transferencia Bancaria'),
        ('USDT_TRC20', 'USDT TRC20'),
        ('BINANCE', 'Binance Pay'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nombre_restaurante = models.CharField(max_length=100)
    plan = models.ForeignKey(PlanRestaurante, on_delete=models.CASCADE)
    metodo_pago = models.CharField(max_length=20, choices=METODOS_PAGO)
    monto_pagado = models.DecimalField(max_digits=10, decimal_places=2)
    comprobante_pago = models.ImageField(upload_to='comprobantes/')
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE')
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.nombre_restaurante} - {self.usuario.username}"


class CuentaPago(models.Model):
    metodo = models.CharField(max_length=20, choices=SolicitudRestaurante.METODOS_PAGO)
    nombre_titular = models.CharField(max_length=100)
    numero_cuenta = models.CharField(max_length=100)
    banco = models.CharField(max_length=100, blank=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    activo = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.metodo} - {self.nombre_titular}"


class Resena(models.Model):
    ESTRELLAS_CHOICES = [
        (1, '⭐'),
        (2, '⭐⭐'),
        (3, '⭐⭐⭐'),
        (4, '⭐⭐⭐⭐'),
        (5, '⭐⭐⭐⭐⭐'),
    ]
    
    pedido = models.ForeignKey('Pedido', on_delete=models.CASCADE, related_name='resenas')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resenas')
    restaurante = models.ForeignKey('Restaurante', on_delete=models.CASCADE, related_name='resenas')
    plato = models.ForeignKey('Plato', on_delete=models.CASCADE, null=True, blank=True, related_name='resenas')
    calificacion = models.IntegerField(choices=ESTRELLAS_CHOICES)
    comentario = models.TextField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activa = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Reseña"
        verbose_name_plural = "Reseñas"
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"Reseña de {self.usuario.username} - {self.calificacion} estrellas"