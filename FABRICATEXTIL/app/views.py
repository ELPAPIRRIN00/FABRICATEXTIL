# -*- coding: utf-8 -*-
import json
import os
import google.generativeai as genai
from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
# IMPORTANTE: Se agregaron Count y F para los gráficos del Dashboard
from django.db.models import Sum, Count, F
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from .models import Producto, MovimientoInventario
from .forms import ProductoForm, MovimientoForm, AjustarStockForm

# --- CONFIGURACIÓN DE IA (Gemini) ---
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'TU_API_KEY_AQUI') 
genai.configure(api_key=GEMINI_API_KEY)

# --- Vistas de Producto (CRUD) ---

@login_required
def crear_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            producto_nuevo = form.save()
            return redirect('app:detalle_producto', sku=producto_nuevo.sku)
    else:
        form = ProductoForm()
    contexto = { 'form': form, 'titulo': 'Crear Nuevo Producto' }
    return render(request, 'app/producto_form.html', contexto)


def detalle_producto(request, sku):
    producto = get_object_or_404(Producto, sku=sku)

    url_info = request.build_absolute_uri(
        reverse('app:detalle_producto', args=[producto.sku])
    )
    # El QR de acción ahora apunta al Kiosco para escaneo rápido
    url_accion = request.build_absolute_uri(
        reverse('app:kiosco_movimiento', args=[producto.sku])
    )

    contexto = {
        'producto': producto,
        'url_qr_info': url_info,
        'url_qr_accion': url_accion
    }
    return render(request, 'app/detalle_producto.html', contexto)


@login_required
def editar_producto(request, sku):
    producto = get_object_or_404(Producto, sku=sku)
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('app:detalle_producto', sku=producto.sku)
    else:
        form = ProductoForm(instance=producto)
    contexto = { 'form': form, 'titulo': f'Editando: {producto.sku}', 'producto': producto }
    return render(request, 'app/producto_form.html', contexto)


@login_required
def eliminar_producto(request, sku):
    producto = get_object_or_404(Producto, sku=sku)
    if request.method == 'POST':
        producto.delete()
        return redirect('app:lista_productos')
    contexto = { 'producto': producto, 'titulo': f'Confirmar Eliminación' }
    return render(request, 'app/eliminar_producto.html', contexto)


def lista_productos(request):
    query = request.GET.get('q')
    if query:
        # Búsqueda básica por nombre o SKU
        productos = Producto.objects.filter(nombre_tela__icontains=query) | Producto.objects.filter(sku__icontains=query)
    else:
        productos = Producto.objects.all()
        
    productos = productos.order_by('nombre_tela') 
    contexto = { 'productos': productos, 'query': query }
    return render(request, 'app/lista_productos.html', contexto)


# --- Vistas de Inventario (Manuales - Admin) ---

@login_required
def registrar_entrada(request, producto_sku):
    producto = get_object_or_404(Producto, sku=producto_sku)
    if request.method == 'POST':
        form = MovimientoForm(request.POST)
        if form.is_valid():
            movimiento = form.save(commit=False)
            movimiento.producto = producto
            movimiento.tipo_movimiento = 'ENTRADA'
            # Asignar usuario si está disponible (mejora de auditoría)
            if request.user.is_authenticated:
                movimiento.usuario = request.user
            movimiento.save()
            
            cantidad_entrada = form.cleaned_data.get('cantidad', 0)
            producto.pz += cantidad_entrada
            producto.save()
            
            return redirect('app:detalle_producto', sku=producto.sku)
    else:
        form = MovimientoForm()
    contexto = { 'form': form, 'producto': producto, 'titulo': 'Registrar Entrada' }
    return render(request, 'app/registrar_movimiento.html', contexto)


@login_required
def registrar_salida(request, producto_sku):
    producto = get_object_or_404(Producto, sku=producto_sku)
    if request.method == 'POST':
        form = MovimientoForm(request.POST)
        if form.is_valid():
            movimiento = form.save(commit=False)
            movimiento.producto = producto
            movimiento.tipo_movimiento = 'SALIDA'
            cantidad_salida = form.cleaned_data.get('cantidad', 0)
            
            if producto.pz >= cantidad_salida:
                if request.user.is_authenticated:
                    movimiento.usuario = request.user
                movimiento.save()
                producto.pz -= cantidad_salida
                producto.save()
                return redirect('app:detalle_producto', sku=producto.sku)
            else:
                form.add_error(None, f"No hay stock suficiente ({producto.pz})")
    else:
        form = MovimientoForm()
    contexto = { 'form': form, 'producto': producto, 'titulo': 'Registrar Salida' }
    return render(request, 'app/registrar_movimiento.html', contexto)


# --- NUEVA VISTA: KIOSCO (Escaneo Rápido) ---
# Esta vista NO requiere @login_required para agilidad en almacén

def kiosco_movimiento(request, sku):
    producto = get_object_or_404(Producto, sku=sku)

    if request.method == 'POST':
        tipo = request.POST.get('tipo') # 'entrada' o 'salida'
        try:
            cantidad = int(request.POST.get('cantidad', 1))
        except ValueError:
            cantidad = 1
        
        # Intentamos obtener usuario si hay sesión iniciada, si no, es anónimo (Sistema)
        usuario_actual = request.user if request.user.is_authenticated else None

        if tipo == 'entrada':
            producto.pz += cantidad
            producto.save()
            
            MovimientoInventario.objects.create(
                producto=producto, 
                tipo_movimiento='ENTRADA', 
                cantidad=cantidad, 
                notas='Escaneo Rápido (Kiosco)',
                usuario=usuario_actual
            )
            messages.success(request, f'✅ Se agregaron {cantidad} pz a {producto.nombre_tela}')
            
        elif tipo == 'salida':
            if producto.pz >= cantidad:
                producto.pz -= cantidad
                producto.save()
                
                MovimientoInventario.objects.create(
                    producto=producto, 
                    tipo_movimiento='SALIDA', 
                    cantidad=cantidad, 
                    notas='Escaneo Rápido (Kiosco)',
                    usuario=usuario_actual
                )
                messages.warning(request, f'🔻 Se retiraron {cantidad} pz de {producto.nombre_tela}')
            else:
                messages.error(request, f'❌ Stock insuficiente. Tienes {producto.pz}, intentaste sacar {cantidad}.')

        # Recargamos la misma página para ver el cambio instantáneo
        return redirect('app:kiosco_movimiento', sku=sku)

    return render(request, 'app/kiosco_movimiento.html', {'producto': producto})


# --- VISTA ANTIGUA DE ACCIÓN (Mantenida por compatibilidad) ---

def accion_producto(request, sku):
    # Redirigimos al nuevo sistema Kiosco para unificar
    return redirect('app:kiosco_movimiento', sku=sku)


@login_required
def ajustar_stock(request, sku):
    producto = get_object_or_404(Producto, sku=sku)
    if request.method == 'POST':
        form = AjustarStockForm(request.POST)
        if form.is_valid():
            nueva_cantidad = form.cleaned_data['nueva_cantidad']
            cantidad_actual = producto.pz
            diferencia = nueva_cantidad - cantidad_actual
            if diferencia != 0:
                tipo_mov = 'ENTRADA' if diferencia > 0 else 'SALIDA'
                MovimientoInventario.objects.create(
                    producto=producto,
                    tipo_movimiento=tipo_mov,
                    cantidad=abs(diferencia),
                    notas=f"Ajuste manual. Anterior: {cantidad_actual}",
                    usuario=request.user
                )
            producto.pz = nueva_cantidad
            producto.save()
            return redirect('app:detalle_producto', sku=producto.sku)
    else:
        form = AjustarStockForm(initial={'nueva_cantidad': producto.pz})
    contexto = { 'form': form, 'producto': producto, 'titulo': 'Ajustar Stock' }
    return render(request, 'app/ajustar_stock.html', contexto)


# --- DASHBOARD (Panel de Control) ---
# Nueva vista agregada

@login_required
def dashboard(request):
    # 1. DATOS PARA TARJETAS (KPIs)
    total_productos = Producto.objects.count()
    total_piezas = Producto.objects.aggregate(total=Sum('pz'))['total'] or 0
    # Stock bajo si hay menos de 5 piezas
    productos_bajo_stock = Producto.objects.filter(pz__lte=5).count()

    # 2. DATOS PARA GRÁFICO DE BARRAS (Top 10 productos con más stock)
    top_productos = Producto.objects.order_by('-pz')[:10]
    nombres_productos = [p.nombre_tela for p in top_productos]
    stock_productos = [p.pz for p in top_productos]

    # 3. DATOS PARA GRÁFICO DE PASTEL (Entradas vs Salidas - Histórico)
    movimientos_data = MovimientoInventario.objects.values('tipo_movimiento').annotate(total=Count('id'))
    
    entradas = 0
    salidas = 0
    for mov in movimientos_data:
        if mov['tipo_movimiento'] == 'ENTRADA':
            entradas = mov['total']
        elif mov['tipo_movimiento'] == 'SALIDA':
            salidas = mov['total']

    # 4. TABLA DE ALERTA (Productos con poco stock)
    alerta_stock = Producto.objects.filter(pz__lte=5).order_by('pz')[:5]

    contexto = {
        'titulo': 'Dashboard de Métricas',
        'total_productos': total_productos,
        'total_piezas': total_piezas,
        'productos_bajo_stock': productos_bajo_stock,
        'alerta_stock': alerta_stock,
        # JSON para Chart.js
        'nombres_productos_json': json.dumps(nombres_productos),
        'stock_productos_json': json.dumps(stock_productos),
        'entradas_json': entradas,
        'salidas_json': salidas,
    }
    return render(request, 'app/dashboard.html', contexto)


# --- Vistas Estáticas y Reportes ---

def index(request):
    num_productos = Producto.objects.count()
    contexto = { 'titulo': 'Inicio', 'num_productos': num_productos }
    return render(request, 'app/index.html', contexto)

def about(request):
    return render(request, 'app/about.html', {'titulo': 'Acerca de'})

def contact(request):
    return render(request, 'app/contact.html', {'titulo': 'Contacto'})

@login_required
def ver_reportes(request):
    # Filtros de fecha
    fecha_inicio_str = request.GET.get('fecha_inicio')
    fecha_fin_str = request.GET.get('fecha_fin')
      
    movimientos_query = MovimientoInventario.objects.all()

    if fecha_inicio_str and fecha_fin_str:
        try:
            fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d')
            fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d')
            fecha_fin = fecha_fin + timedelta(days=1) - timedelta(seconds=1)
            movimientos_query = movimientos_query.filter(fecha__range=[fecha_inicio, fecha_fin])
        except ValueError:
            pass
      
    ultimos_movimientos = movimientos_query.order_by('-fecha')[:50]

    total_piezas = Producto.objects.aggregate(total=Sum('pz'))['total'] or 0
    productos_unicos = Producto.objects.count()
    stock_por_modelo = Producto.objects.values('nombre_tela').annotate(total_pz=Sum('pz')).order_by('-total_pz')

    contexto = {
        'titulo': 'Reportes',
        'total_piezas': total_piezas,
        'productos_unicos': productos_unicos,
        'stock_por_modelo': stock_por_modelo,
        'ultimos_movimientos': ultimos_movimientos,
        'fecha_inicio': fecha_inicio_str,
        'fecha_fin': fecha_fin_str,
    }
    return render(request, 'app/reportes.html', contexto)

# --- Vistas del Escáner ---

def escaner_view(request):
    """
    1. Esta vista se activa con el botón del MENÚ.
    Muestra la pantalla de elección (eleccion_escaner.html).
    """
    return render(request, 'app/eleccion_escaner.html', {'titulo': 'Escanear'})

def camara_view(request):
    """
    2. Esta vista se activa con el botón "Abrir Cámara".
    Muestra la pantalla negra de la cámara (escaner.html).
    """
    return render(request, 'app/escaner.html', {'titulo': 'Cámara Activa'})


# --- API PARA IA (GEMINI) ---

@login_required
def generar_descripcion_api(request):
    """
    Recibe un prompt en JSON, llama a Gemini y devuelve la respuesta.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            prompt = data.get('prompt', '')
            
            if not prompt:
                return JsonResponse({'error': 'No prompt provided'}, status=400)

            # Configuración del modelo (Gemini Pro)
            model = genai.GenerativeModel('gemini-pro')
            
            # Generar contenido
            response = model.generate_content(prompt)
            texto_generado = response.text

            return JsonResponse({'descripcion': texto_generado})

        except Exception as e:
            print(f"Error Gemini API: {e}")
            return JsonResponse({'error': str(e)}, status=500)
      
    return JsonResponse({'error': 'Invalid method'}, status=405)

# --- BORRAR ESTO DESPUÉS DE USAR ---
def crear_superusuario_rapido(request):
    # Verifica si ya existe el usuario 'admin'
    if not User.objects.filter(username='admin').exists():
        # Crea el usuario: usuario='admin', correo='', contraseña='admin123'
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        return HttpResponse("✅ ¡Listo! Usuario: <b>admin</b> / Contraseña: <b>admin123</b> creados.")
    else:
        return HttpResponse("⚠️ El usuario 'admin' ya existe. Intenta iniciar sesión.")
