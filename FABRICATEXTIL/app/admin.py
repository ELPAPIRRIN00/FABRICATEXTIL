from django.contrib import admin
from .models import Producto, Categoria, Proveedor

class ProductoAdmin(admin.ModelAdmin):
    # Organiza el formulario en secciones con los campos CORRECTOS
    fieldsets = [
        ('Identificación Principal', {
            'fields': ('sku', 'nombre_tela', 'tipo')
        }),
        ('Características', {
            'fields': ('composicion', 'color')
        }),
        ('Dimensiones y Stock', {
            'fields': (('largo', 'ancho'), ('pz', 'peso_por_pz'), 'peso_aprox')
        }),
        ('Notas Adicionales', {
            'fields': ('descripcion',)
        }),
    ]
    # Columnas que se verán en la lista de productos (también corregido)
    list_display = ('sku', 'nombre_tela', 'tipo', 'color', 'pz', 'largo', 'ancho', 'peso_aprox')
    # Añade filtros útiles
    list_filter = ('tipo', 'color', 'composicion')
    # Añade una barra de búsqueda
    search_fields = ('sku', 'nombre_tela')


# Le decimos a Django que use nuestra clase personalizada para el modelo Producto
admin.site.register(Producto, ProductoAdmin)

# Registramos los otros modelos de forma simple
admin.site.register(Categoria)
admin.site.register(Proveedor)
