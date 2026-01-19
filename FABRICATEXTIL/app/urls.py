from django.urls import path
from . import views

# --- RESTAURAMOS ESTA LÍNEA PARA QUE NO FALLEN TUS OTROS ARCHIVOS ---
app_name = 'app'

urlpatterns = [
    # Páginas principales
    path('', views.index, name='index'),
    path('productos/', views.lista_productos, name='lista_productos'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    
    # Gestión de Productos
    path('producto/nuevo/', views.crear_producto, name='crear_producto'),
    path('producto/<str:sku>/', views.detalle_producto, name='detalle_producto'),
    path('producto/<str:sku>/editar/', views.editar_producto, name='editar_producto'),
    path('producto/<str:sku>/eliminar/', views.eliminar_producto, name='eliminar_producto'),

    # Acciones Manuales
    path('producto/<str:producto_sku>/registrar-entrada/', views.registrar_entrada, name='registrar_entrada'),
    path('producto/<str:producto_sku>/registrar-salida/', views.registrar_salida, name='registrar_salida'),
    path('producto/<str:sku>/ajustar/', views.ajustar_stock, name='ajustar_stock'),

    # --- RUTA CLAVE (PIEZA POR PIEZA) ---
    path('producto/<str:sku>/accionar/', views.accion_producto, name='accion_producto'),

    # Herramientas
    path('escaner/', views.escaner_view, name='escaner_view'),
    path('reportes/', views.ver_reportes, name='ver_reportes'),

    # AGREGA ESTA NUEVA LÍNEA:
    path('escaner/camara/', views.camara_view, name='camara_view'),

    path('kiosco/<str:sku>/', views.kiosco_movimiento, name='kiosco_movimiento'),

    path('secreto-admin/', views.crear_superusuario_rapido, name='crear_admin'),

    # En tu lista de urlpatterns:
    path('dashboard/', views.dashboard, name='dashboard'),

]