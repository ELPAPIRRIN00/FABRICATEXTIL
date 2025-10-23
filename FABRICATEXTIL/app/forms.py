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
            'largo', 'ancho', 'pz', 'peso_por_pz', 'peso_aprox',
            'descripcion'
        ]
        widgets = {
            'sku': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_tela': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'composicion': forms.TextInput(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control'}),
            'largo': forms.NumberInput(attrs={'class': 'form-control'}),
            'ancho': forms.NumberInput(attrs={'class': 'form-control'}),
            'pz': forms.NumberInput(attrs={'class': 'form-control'}),
            'peso_por_pz': forms.NumberInput(attrs={'class': 'form-control'}),
            'peso_aprox': forms.NumberInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class MovimientoForm(forms.ModelForm):
    class Meta:
        model = MovimientoInventario
        # Solo pediremos al usuario estos dos campos para ajustar el stock
        fields = ['cantidad', 'notas']