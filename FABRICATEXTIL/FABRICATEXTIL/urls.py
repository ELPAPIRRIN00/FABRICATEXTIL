from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('inventario/', include('app.urls', namespace='app')),
    path('accounts/', include('django.contrib.auth.urls')),
    # Borra cualquier otra línea path() que hubiera aquí (como la de 'about', 'contact', etc.)
]
