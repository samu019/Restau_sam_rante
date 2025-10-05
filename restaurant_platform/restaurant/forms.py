from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
import re
from .models import Pedido
from .models import Restaurante, Categoria, Plato, Anuncio, PerfilUsuario
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
import re
from .models import Pedido
from .models import Restaurante, Categoria, Plato, Anuncio, PerfilUsuario, Resena  # AGREGAR Resena AQUÍ
# ==================== FORMULARIOS DE AUTENTICACIÓN ====================

class RegisterForm(UserCreationForm):
    """
    Formulario de registro con validación personalizada de contraseña
    """
    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa tu contraseña'
        }),
        help_text="La contraseña debe contener al menos 1 mayúscula, 1 número y 1 símbolo."
    )
    
    password2 = forms.CharField(
        label="Confirmar Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirma tu contraseña'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de usuario'
            }),
        }
        labels = {
            'username': 'Nombre de Usuario',
        }
        help_texts = {
            'username': 'Requerido. 150 caracteres o menos. Solo letras, números y @/./+/-/_',
        }

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        
        # Validaciones personalizadas
        if len(password1) < 8:
            raise ValidationError("La contraseña debe tener al menos 8 caracteres.")
        
        if not re.search(r'[A-Z]', password1):
            raise ValidationError("La contraseña debe contener al menos una letra mayúscula.")
        
        if not re.search(r'\d', password1):
            raise ValidationError("La contraseña debe contener al menos un número.")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password1):
            raise ValidationError("La contraseña debe contener al menos un símbolo especial.")
        
        return password1

class CustomLoginForm(AuthenticationForm):
    """
    Formulario de login personalizado
    """
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre de usuario'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Contraseña'
        })
    )

# ==================== FORMULARIOS DE RESTAURANTE ====================

class RestauranteForm(forms.ModelForm):
    """
    Formulario para crear y editar restaurantes
    """
    class Meta:
        model = Restaurante
        fields = ['nombre', 'direccion', 'telefono', 'email', 'logo']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del restaurante'
            }),
            'direccion': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Dirección completa',
                'rows': 3
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono de contacto'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@ejemplo.com'
            }),
            'logo': forms.FileInput(attrs={
                'class': 'form-control'
            }),
        }
        labels = {
            'nombre': 'Nombre del Restaurante',
            'direccion': 'Dirección',
            'telefono': 'Teléfono',
            'email': 'Correo Electrónico',
            'logo': 'Logo del Restaurante',
        }

class RestauranteConfigForm(forms.ModelForm):
    """
    Formulario para configurar la apariencia del restaurante
    """
    class Meta:
        model = Restaurante
        fields = ['color_primario', 'color_secundario', 'tema', 'idioma']
        widgets = {
            'color_primario': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color',
                'style': 'width: 80px; height: 40px;'
            }),
            'color_secundario': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color', 
                'style': 'width: 80px; height: 40px;'
            }),
            'tema': forms.Select(attrs={'class': 'form-control'}),
            'idioma': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'color_primario': 'Color Primario',
            'color_secundario': 'Color Secundario',
            'tema': 'Tema de Diseño',
            'idioma': 'Idioma',
        }

# ==================== FORMULARIOS DE CATEGORÍAS ====================

class CategoriaForm(forms.ModelForm):
    """
    Formulario para crear y editar categorías
    """
    class Meta:
        model = Categoria
        fields = ['nombre', 'emoji', 'descripcion', 'imagen', 'orden']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la categoría'
            }),
            'emoji': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '🍔 🍕 🍹',
                'maxlength': '10'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción de la categoría',
                'rows': 3
            }),
            'imagen': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'orden': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
        }
        labels = {
            'nombre': 'Nombre de la Categoría',
            'emoji': 'Emoji Representativo',
            'descripcion': 'Descripción',
            'imagen': 'Imagen de la Categoría',
            'orden': 'Orden de Visualización',
        }

# ==================== FORMULARIOS DE PLATOS ====================

class PlatoForm(forms.ModelForm):
    """
    Formulario para crear y editar platos
    """
    class Meta:
        model = Plato
        fields = [
            'nombre', 'descripcion', 'categoria', 'precio', 
            'precio_promocion', 'tipo', 'stock', 'stock_ilimitado',
            'imagen', 'tiempo_preparacion', 'es_popular', 'es_recomendado'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del plato'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción detallada del plato',
                'rows': 4
            }),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'precio_promocion': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'stock_ilimitado': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'imagen': forms.FileInput(attrs={'class': 'form-control'}),
            'tiempo_preparacion': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '120'
            }),
            'es_popular': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'es_recomendado': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'nombre': 'Nombre del Plato',
            'descripcion': 'Descripción',
            'categoria': 'Categoría',
            'precio': 'Precio Normal',
            'precio_promocion': 'Precio Promocional',
            'tipo': 'Tipo de Plato',
            'stock': 'Cantidad en Stock',
            'stock_ilimitado': 'Stock Ilimitado',
            'imagen': 'Imagen del Plato',
            'tiempo_preparacion': 'Tiempo de Preparación (min)',
            'es_popular': 'Marcar como Popular',
            'es_recomendado': 'Marcar como Recomendado',
        }

    def __init__(self, *args, **kwargs):
        restaurante = kwargs.pop('restaurante', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar categorías solo del restaurante actual
        if restaurante:
            self.fields['categoria'].queryset = Categoria.objects.filter(restaurante=restaurante)

# ==================== FORMULARIOS DE ANUNCIOS ====================

class AnuncioForm(forms.ModelForm):
    """
    Formulario para crear y editar anuncios
    """
    class Meta:
        model = Anuncio
        fields = ['titulo', 'mensaje', 'imagen', 'fecha_inicio', 'fecha_fin', 'destacado']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título del anuncio'
            }),
            'mensaje': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Mensaje del anuncio',
                'rows': 4
            }),
            'imagen': forms.FileInput(attrs={'class': 'form-control'}),
            'fecha_inicio': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'fecha_fin': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'destacado': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'titulo': 'Título del Anuncio',
            'mensaje': 'Mensaje',
            'imagen': 'Imagen del Anuncio',
            'fecha_inicio': 'Fecha de Inicio',
            'fecha_fin': 'Fecha de Fin',
            'destacado': 'Destacado',
        }

# ==================== FORMULARIOS DE PERFIL ====================

class PerfilUsuarioForm(forms.ModelForm):
    """
    Formulario para editar el perfil de usuario
    """
    class Meta:
        model = PerfilUsuario
        fields = ['telefono', 'direccion', 'avatar', 'tema_oscuro', 'notificaciones']
        widgets = {
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de teléfono'
            }),
            'direccion': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Dirección de entrega',
                'rows': 3
            }),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
            'tema_oscuro': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'notificaciones': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'telefono': 'Teléfono',
            'direccion': 'Dirección',
            'avatar': 'Foto de Perfil',
            'tema_oscuro': 'Usar Tema Oscuro',
            'notificaciones': 'Recibir Notificaciones',
        }

# ==================== FORMULARIOS DE PEDIDOS ====================

class PedidoForm(forms.ModelForm):
    """
    Formulario para actualizar el estado de pedidos
    """
    class Meta:
        model = Pedido
        fields = ['estado', 'metodo_pago', 'notas']
        widgets = {
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'metodo_pago': forms.Select(attrs={'class': 'form-control'}),
            'notas': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Notas adicionales para el pedido',
                'rows': 3
            }),
        }
        labels = {
            'estado': 'Estado del Pedido',
            'metodo_pago': 'Método de Pago',
            'notas': 'Notas Adicionales',
        }

# ==================== FORMULARIOS NUEVOS PARA SISTEMA COMPLETO ====================

class ResenaForm(forms.ModelForm):
    """
    Formulario para agregar reseñas a platos
    """
    class Meta:
        model = Resena  # ✅ Ahora Resena está importado correctamente
        fields = ['plato', 'calificacion', 'comentario']
        widgets = {
            'calificacion': forms.Select(attrs={
                'class': 'form-control',
                'required': 'required'
            }),
            'comentario': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Comparte tu experiencia con este plato...',
                'required': 'required'
            }),
            'plato': forms.HiddenInput(),  # Oculto porque lo determinamos desde la vista
        }
        labels = {
            'calificacion': 'Calificación',
            'comentario': 'Tu Comentario',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizar las opciones de calificación
        self.fields['calificacion'].choices = [
            (5, '⭐⭐⭐⭐⭐ Excelente'),
            (4, '⭐⭐⭐⭐ Muy Bueno'),
            (3, '⭐⭐⭐ Bueno'),
            (2, '⭐⭐ Regular'),
            (1, '⭐ Malo'),
        ]
class CheckoutForm(forms.Form):
    """
    Formulario para el proceso de checkout
    """
    direccion = forms.CharField(
        max_length=500,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Ingresa tu dirección completa para la entrega',
            'required': 'required'
        }),
        required=True
    )
    telefono = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tu número de teléfono',
            'required': 'required'
        }),
        required=True
    )
    metodo_pago = forms.ChoiceField(
        choices=Pedido.METODOS_PAGO,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'required': 'required'
        }),
        required=True
    )
    comentarios = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Instrucciones especiales para la entrega...'
        })
    )
    comprobante_pago = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )

class BusquedaRestaurantesForm(forms.Form):
    """
    Formulario para buscar restaurantes
    """
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar restaurantes...'
        })
    )
    categoria = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Filtrar por categoría...'
        })
    )