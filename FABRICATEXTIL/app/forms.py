"""
Definition of forms.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _
from .models import Producto, MovimientoInventario # <-- Importación añadida

class BootstrapAuthenticationForm(AuthenticationForm):
    """Authentication form which uses boostrap CSS."""
    username = forms.CharField(max_length=254,
                               widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'User name'}))
    password = forms.CharField(label=_("Password"),
                               widget=forms.PasswordInput({
                                   'class': 'form-control',
                                   'placeholder':'Password'}))

# --- Formularios de Inventario (AÑADIDOS) ---

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            'sku', 'nombre_tela', 'tipo', 'composicion', 'color', 
            'largo', 'ancho', 'pz', 
            'peso_por_pieza', 'peso_aprox', 
            'paquete_pz', 'paquetes_bulto', 'bulto_pz',  # <-- NUEVOS
            'ubicacion', 'descripcion'
        ]
        
        # Añadimos 'widgets' para que se vean bien en Bootstrap
        widgets = {
            'sku': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_tela': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'composicion': forms.TextInput(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control'}),
            'largo': forms.NumberInput(attrs={'class': 'form-control'}),
            'ancho': forms.NumberInput(attrs={'class': 'form-control'}),
            'pz': forms.NumberInput(attrs={'class': 'form-control'}),
            'peso_por_pieza': forms.NumberInput(attrs={'class': 'form-control'}),
            'peso_aprox': forms.NumberInput(attrs={'class': 'form-control'}),
            
            # --- Widgets para los NUEVOS campos ---
            'paquete_pz': forms.NumberInput(attrs={'class': 'form-control'}),
            'paquetes_bulto': forms.NumberInput(attrs={'class': 'form-control'}),
            'bulto_pz': forms.NumberInput(attrs={'class': 'form-control'}),
            # --- Fin ---
            
            'ubicacion': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class MovimientoForm(forms.ModelForm):
    class Meta:
        model = MovimientoInventario
        fields = ['cantidad', 'notas']
        # Añadimos widgets para aplicar estilos de Bootstrap
        widgets = {
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 10'}),
            'notas': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Para orden de producción #552'}),
        }

class AjustarStockForm(forms.Form):
    """
    Un formulario simple para ajustar el stock a una cantidad específica.
    """
    nueva_cantidad = forms.IntegerField(
        label="Nueva Cantidad de Stock",
        required=True,
        min_value=0, # No se puede tener stock negativo
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 50'})
    )