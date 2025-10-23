from django.urls import path
from . import views

urlpatterns = [
    path('productos/', views.lista_productos, name='lista_de_productos'),
    path('producto/nuevo/', views.crear_producto, name='crear_producto'),
    path('producto/<str:sku>/', views.detalle_producto, name='detalle_producto'),
    path('producto/<str:sku>/ajustar/', views.ajustar_stock, name='ajustar_stock'),
    path('producto/<str:sku>/eliminar/', views.eliminar_producto, name='eliminar_producto'),
    path('escaner/', views.escaner_view, name='escaner'),
    path('reportes/', views.reportes_view, name='reportes'),
]