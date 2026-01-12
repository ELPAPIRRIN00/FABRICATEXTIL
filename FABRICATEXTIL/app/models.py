from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# --- Choices (Listas de Opciones) ---

TIPO_CHOICES = [
    ('Tela', 'Tela'),
    ('Toalla', 'Toalla'),
    ('Paquete', 'Paquete'),
    ('Bulto', 'Bulto'),
    ('Otro', 'Otro'),
]

TIPO_MOVIMIENTO_CHOICES = [
    ('ENTRADA', 'Entrada'),
    ('SALIDA', 'Salida'),
]


# --- Modelo Principal: Producto ---

class Producto(models.Model):
    # --- Identificación Básica ---
    sku = models.CharField(max_length=50, unique=True, primary_key=True, verbose_name="SKU")
    nombre_tela = models.CharField(max_length=200, verbose_name="Nombre de Tela (Artículo)")
    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES, default='Tela')
    color = models.CharField(max_length=100, blank=True, null=True)
    composicion = models.CharField(max_length=200, blank=True, null=True)

    # --- Medidas y Peso ---
    largo = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name="Largo (m)")
    ancho = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name="Ancho (m)")
    peso_por_pieza = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Peso por Pieza (kg)")
    peso_aprox = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Peso Aproximado (kg)")

    # --- Datos de Empaque ---
    paquete_pz = models.IntegerField(blank=True, null=True, verbose_name="Piezas por Paquete (PAQUETE)")
    paquetes_bulto = models.IntegerField(blank=True, null=True, verbose_name="Paquetes por Bulto")
    bulto_pz = models.IntegerField(blank=True, null=True, verbose_name="Piezas por Bulto (BULTO)")

    # --- Stock y Logística ---
    pz = models.IntegerField(default=0, verbose_name="Piezas (Stock Actual)")
    ubicacion = models.CharField(max_length=100, blank=True, null=True, verbose_name="Ubicación")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción / Notas")

    def __str__(self):
        return f"{self.nombre_tela} ({self.sku})"


# --- Modelo de Historial: MovimientoInventario ---

class MovimientoInventario(models.Model):
    producto = models.ForeignKey(
        Producto, 
        on_delete=models.CASCADE, 
        related_name="movimientoinventario_set"
    )
    
    # --- CAMPO DE AUDITORÍA ---
    usuario = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, # Si se borra el usuario, no se borra el historial
        null=True, 
        blank=True,
        verbose_name="Usuario Responsable"
    )
    
    tipo_movimiento = models.CharField(
        max_length=10, 
        choices=TIPO_MOVIMIENTO_CHOICES
    )
    
    cantidad = models.IntegerField(default=0)
    
    # Fecha automática
    fecha = models.DateTimeField(auto_now_add=True)
    
    # Notas
    notas = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        user_name = self.usuario.username if self.usuario else "Sistema"
        return f"{self.get_tipo_movimiento_display()} ({self.cantidad}) - {user_name}"

    class Meta:
        ordering = ['-fecha']