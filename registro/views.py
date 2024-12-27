from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import RegistroHora
from django.http import HttpResponse
from datetime import timedelta
from datetime import datetime
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import F, ExpressionWrapper, DurationField
from django.db.models.functions import ExtractMonth, ExtractYear
from django.db .models import Sum
from .forms import CustomUserCreationForm

def registrarse(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Tu cuenta ha sido creada exitosamente! Ahora puedes iniciar sesión.')
            return redirect('login')  # Redirige a la página de inicio de sesión
        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/registrarse.html', {'form': form})


def landing_page(request):
    """
    Vista para la página de presentación.
    """
    return render(request, 'registro/landing_page.html')  # Página de presentación si no está autenticado

# Vista para registrar el inicio de la jornada
@login_required
def dashboard(request):
    if request.method == 'POST':
        # Validar si ya existe un registro activo
        if RegistroHora.objects.filter(usuario=request.user, hora_fin=None).exists():
            return HttpResponse("Ya has registrado tu inicio de jornada", status=400)

        # Crear un nuevo registro de jornada
        hora_inicio = timezone.now()
        RegistroHora.objects.create(usuario=request.user, hora_inicio=hora_inicio)

        # Redirigir a la misma página para mostrar el cronómetro
        return redirect('dashboard')

    # Obtener registro activo si existe
    registro_activo = RegistroHora.objects.filter(usuario=request.user, hora_fin=None).first()
    return render(request, 'registro/dashboard.html', {
        'hora_inicio': registro_activo.hora_inicio.isoformat() if registro_activo else None,
        'registro_activo': bool(registro_activo),  # Indica si hay un registro activo
    })


# Vista para registrar el fin de la jornada
@login_required
def registrar_fin(request):
    if request.method == 'POST':
        # Buscar un registro activo
        registro = RegistroHora.objects.filter(usuario=request.user, hora_fin=None).first()

        if not registro:
            return HttpResponse("No hay una jornada activa para finalizar.", status=400)

        # Registrar la hora de fin
        registro.hora_fin = timezone.now()
        registro.save()

        # Redirigir a la página de resumen o mostrar mensaje de éxito
        return redirect('resumen')

    return render(request, 'registro/fin.html')

@login_required
def eliminar_registro(request, pk):
    registro = get_object_or_404(RegistroHora, pk=pk)
    registro.delete()
    messages.success(request, "El registro ha sido eliminado exitosamente.")
    return redirect('resumen')  # Cambia 'resumen' según tu vista actual

@login_required
def resumen(request):
    from datetime import timedelta, date

    # Obtener parámetros de filtrado desde la URL
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    mes = request.GET.get('mes')

    # Convertir las fechas al formato correcto (YYYY-MM-DD) si es necesario
    if fecha_inicio:
        try:
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
        except ValueError:
            fecha_inicio = None

    if fecha_fin:
        try:
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
        except ValueError:
            fecha_fin = None

    # Filtro base: registros del usuario autenticado
    registros = RegistroHora.objects.filter(usuario=request.user)

    # Filtro por rango de fechas (fecha inicio y fecha fin)
    if fecha_inicio and fecha_fin:
        registros = registros.filter(hora_inicio__date__gte=fecha_inicio, hora_fin__date__lte=fecha_fin)
    elif fecha_inicio:
        registros = registros.filter(hora_inicio__date__gte=fecha_inicio)
    elif fecha_fin:
        registros = registros.filter(hora_fin__date__lte=fecha_fin)

    # Filtro por mes (si se selecciona un mes)
    if mes:
        registros = registros.filter(hora_inicio__month=int(mes))

    # Si no hay registros, manejar la condición
    no_registros = not registros.exists()

    # Calcular totales
    total_horas_trabajadas = timedelta()
    dias_trabajados = set()
    registros_con_horas = []

    # Fechas para cálculos adicionales
    hoy = date.today()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    inicio_mes = hoy.replace(day=1)

    horas_esta_semana = timedelta()
    horas_este_mes = timedelta()

    for registro in registros:
        if registro.hora_fin:
            horas_trabajadas = registro.hora_fin - registro.hora_inicio
            total_horas_trabajadas += horas_trabajadas

            # Registrar el día trabajado
            dias_trabajados.add(registro.hora_inicio.date())

            # Calcular horas trabajadas esta semana
            if registro.hora_inicio.date() >= inicio_semana:
                horas_esta_semana += horas_trabajadas

            # Calcular horas trabajadas este mes
            if registro.hora_inicio.date() >= inicio_mes:
                horas_este_mes += horas_trabajadas
        else:
            horas_trabajadas = timedelta()

        # Convertir horas trabajadas a horas y minutos
        horas, remainder = divmod(horas_trabajadas.total_seconds(), 3600)
        minutos, _ = divmod(remainder, 60)
        horas_trabajadas_formateadas = f"{int(horas)}h {int(minutos)}m"

        registros_con_horas.append({
            'registro': registro,
            'horas_trabajadas': horas_trabajadas_formateadas
        })

    # Formatear horas trabajadas esta semana y este mes
    def format_timedelta(td):
        horas, remainder = divmod(td.total_seconds(), 3600)
        minutos, _ = divmod(remainder, 60)
        return f"{int(horas)}h {int(minutos)}m"

    # Paginación
    paginator = Paginator(registros_con_horas, 10)  # 10 resultados por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Lista de meses para pasar a la plantilla
    meses = [
        {'numero': i, 'nombre': nombre} for i, nombre in enumerate([
            'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
            'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
        ], start=1)
    ]

    # Contexto para la plantilla
    return render(request, 'registro/resumen.html', {
        'page_obj': page_obj if not no_registros else None,
        'total_horas_trabajadas': format_timedelta(total_horas_trabajadas) if not no_registros else "0h 0m",
        'dias_trabajados': len(dias_trabajados) if not no_registros else 0,
        'horas_esta_semana': format_timedelta(horas_esta_semana) if not no_registros else "0h 0m",
        'horas_este_mes': format_timedelta(horas_este_mes) if not no_registros else "0h 0m",
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'meses': meses,
        'mes': mes,
        'no_registros': no_registros
    })