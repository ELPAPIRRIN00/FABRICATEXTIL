from django.contrib import admin
# --- CORRECCIÓN 1 ---
# Importamos SOLO los modelos que SÍ existen: Producto y MovimientoInventario
from .models import Producto, MovimientoInventario

# --- CORRECCIÓN 2 ---
# Usamos el decorador @admin.register, es la forma moderna.
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    # Organiza el formulario en secciones
    fieldsets = [
        ('Identificación Principal', {
            'fields': ('sku', 'nombre_tela', 'tipo')
        }),
        ('Características', {
            'fields': ('composicion', 'color')
        }),
        ('Dimensiones y Stock', {
            # --- CORRECCIÓN 3 ---
            # Corregimos el typo a 'peso_por_pieza' (como en models.py)
            'fields': (('largo', 'ancho'), ('pz', 'peso_por_pieza'), 'peso_aprox')
        }),
        # --- CORRECCIÓN 4 ---
        # Añadimos los NUEVOS campos de la tabla en su propia sección
        ('Datos de Empaque (de la Tabla)', {
            'fields': ('paquete_pz', 'paquetes_bulto', 'bulto_pz')
        }),
        ('Notas Adicionales', {
            # Añadimos 'ubicacion' que faltaba aquí
            'fields': ('ubicacion', 'descripcion',)
        }),
    ]
    
    # Columnas que se verán en la lista de productos
    # --- CORRECCIÓN 5 ---
    # Añadimos los nuevos campos a la lista
    list_display = (
        'sku', 'nombre_tela', 'tipo', 'color', 'pz', 
        'paquete_pz', 'bulto_pz', 'ubicacion'
    )
    
    # Añade filtros útiles
    list_filter = ('tipo', 'color', 'composicion', 'ubicacion')
    # Añade una barra de búsqueda
    search_fields = ('sku', 'nombre_tela')


# --- CORRECCIÓN 6 ---
# Registramos el modelo de Movimientos para verlo en el Admin
@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'producto', 'tipo_movimiento', 'cantidad', 'notas')
    list_filter = ('tipo_movimiento', 'fecha')
    search_fields = ('producto__sku', 'producto__nombre_tela', 'notas')
    date_hierarchy = 'fecha'

# --- CORRECCIÓN 7 ---
# Eliminamos las líneas que daban error
# admin.site.register(Categoria)  <-- ELIMINADO (daba error)
# admin.site.register(Proveedor) <-- ELIMINADO (daba error)