from django.db import models
from django.contrib.auth.models import User

# Modelos de apoyo (definidos ANTES que Producto)
class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.nombre

class Proveedor(models.Model):
    nombre = models.CharField(max_length=200, unique=True)
    contacto = models.CharField(max_length=200, blank=True, null=True)
    def __str__(self):
        return self.nombre

# --- El Modelo de Producto COMPLETO ---
class Producto(models.Model):
    TIPOS_DE_PRODUCTO = [
        ('Rollo', 'Rollo'),
        ('Paquete', 'Paquete'),
        ('Bulto', 'Bulto'),
        ('Toalla', 'Toalla'),
    ]

    sku = models.CharField(max_length=100, unique=True, verbose_name="SKU")
    nombre_tela = models.CharField(max_length=100, verbose_name="Nombre Tela / Artículo")
    largo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Largo (L)")
    ancho = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Ancho (Anch)")
    pz = models.IntegerField(default=0, verbose_name="Piezas (Pz)")
    peso_por_pz = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Peso por Pieza (gr)")
    peso_aprox = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Peso Aproximado (kg)")
    color = models.CharField(max_length=50)
    composicion = models.CharField(max_length=100, blank=True, null=True)
    tipo = models.CharField(max_length=50, choices=TIPOS_DE_PRODUCTO, default='Rollo')
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción / Comentarios")
    
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.sku

class MovimientoInventario(models.Model):
    TIPOS_MOVIMIENTO = [
        ('Entrada', 'Entrada'),
        ('Salida', 'Salida'),
        ('Ajuste', 'Ajuste'),
    ]

    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='movimientos')
    tipo_movimiento = models.CharField(max_length=10, choices=TIPOS_MOVIMIENTO)
    cantidad = models.IntegerField(default=0)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_movimiento = models.DateTimeField(auto_now_add=True)
    notas = models.CharField(max_length=255, blank=True, null=True, help_text="Ej: Orden de producción #OP-582")

    def __str__(self):
        return f"{self.tipo_movimiento} de {self.cantidad} para {self.producto.sku}"