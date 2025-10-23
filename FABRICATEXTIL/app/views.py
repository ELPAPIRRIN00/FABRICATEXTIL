from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Producto, MovimientoInventario
from .forms import ProductoForm, MovimientoForm
from django.db.models import Count, Sum

# --- VISTAS PRINCIPALES DE LA APLICACIÓN ---

def lista_productos(request):
    """
    Muestra la lista de todos los productos.
    También maneja la lógica de búsqueda.
    """
    query = request.GET.get('q')
    productos = Producto.objects.all().order_by('nombre_tela') # Ordenamos alfabéticamente
    
    if query:
        productos = productos.filter(
            Q(sku__icontains=query) | Q(nombre_tela__icontains=query)
        )
    
    contexto = {
        'productos': productos,
        'query': query
    }
    return render(request, 'app/lista_productos.html', contexto)

def detalle_producto(request, sku):
    """ Muestra la información detallada de un solo producto. """
    producto = get_object_or_404(Producto, sku=sku)
    contexto = {
        'producto': producto
    }
    return render(request, 'app/detalle_producto.html', contexto)

# --- VISTAS PARA CREAR Y MODIFICAR ---

@login_required
def crear_producto(request):
    """ Muestra el formulario para crear un nuevo producto y lo guarda. """
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_de_productos')
    else:
        form = ProductoForm()
    
    return render(request, 'app/crear_producto.html', {'form': form})

@login_required
def ajustar_stock(request, sku):
    """ Permite registrar entradas y salidas de stock para un producto. """
    producto = get_object_or_404(Producto, sku=sku)
    
    if request.method == 'POST':
        form = MovimientoForm(request.POST)
        if form.is_valid():
            movimiento = form.save(commit=False)
            movimiento.producto = producto
            movimiento.usuario = request.user
            
            cantidad_movida = abs(movimiento.cantidad) # Usamos el valor absoluto

            if 'entrada' in request.POST:
                producto.pz += cantidad_movida
                movimiento.tipo_movimiento = 'Entrada'
                movimiento.cantidad = cantidad_movida
            elif 'salida' in request.POST:
                if cantidad_movida <= producto.pz:
                    producto.pz -= cantidad_movida
                    movimiento.tipo_movimiento = 'Salida'
                    movimiento.cantidad = cantidad_movida
                else:
                    # Opcional: Manejar el error si se intenta sacar más stock del que hay
                    # Por ahora, simplemente no hacemos nada si no hay stock suficiente.
                    pass
            
            producto.save()
            movimiento.save()
            return redirect('detalle_producto', sku=producto.sku)
    else:
        form = MovimientoForm()
        
    return render(request, 'app/ajustar_stock.html', {
        'form': form,
        'producto': producto
    })

@login_required
def eliminar_producto(request, sku):
    """ Muestra la página de confirmación y elimina un producto. """
    producto = get_object_or_404(Producto, sku=sku)
    if request.method == 'POST':
        producto.delete()
        return redirect('lista_de_productos')
    return render(request, 'app/eliminar_producto.html', {'producto': producto})

# --- VISTAS DE HERRAMIENTAS ---

def escaner_view(request):
    """ Muestra la página con el escáner de QR. """
    return render(request, 'app/escaner.html')


def reportes_view(request):
    # Consulta 1: Contar el número total de tipos de producto
    total_productos_unicos = Producto.objects.count()

    # Consulta 2: Sumar el total de piezas de todos los productos
    total_piezas_stock = Producto.objects.aggregate(total=Sum('pz'))['total'] or 0

    # Consulta 3: Agrupar por 'tipo' y contar cuántos productos hay en cada grupo
    productos_por_tipo = Producto.objects.values('tipo').annotate(cantidad=Count('tipo')).order_by('-cantidad')

    # Consulta 4: Obtener los 5 movimientos de inventario más recientes
    ultimos_movimientos = MovimientoInventario.objects.order_by('-fecha_movimiento')[:5]

    contexto = {
        'total_productos_unicos': total_productos_unicos,
        'total_piezas_stock': total_piezas_stock,
        'productos_por_tipo': productos_por_tipo,
        'ultimos_movimientos': ultimos_movimientos,
    }
    return render(request, 'app/reportes.html', contexto)