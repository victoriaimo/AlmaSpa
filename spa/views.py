import secrets
from datetime import timedelta
from django.urls import reverse
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from .forms import TurnoForm, SolicitudForm, RegistroForm, LoginForm
from .models import Solicitud, CodigoValidacion, UsuarioAutorizado
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import SolicitudSerializer
from requests.exceptions import RequestException
from .services import obtener_productos_belleza


def inicio(request):
    return render(request, 'spa/inicio.html')



def tratamientos(request):

    productos = []
    error_api = None

    try:
        productos = obtener_productos_belleza()

    except (RequestException, ValueError):
        error_api = (
            'En este momento no se encuentran disponibles '
            'los productos de cuidado facial.'
        )

    return render(request, 'spa/tratamientos.html', {
        'productos': productos,
        'error_api': error_api
    })


def espacio(request):
    return render(request, 'spa/espacio.html')


def clasificar_consulta(mensaje):
    mensaje = mensaje.lower()

    if any(palabra in mensaje for palabra in
           ['precio', 'costo', 'tarifa', 'compra']):
        return 'Comercial'

    elif any(palabra in mensaje for palabra in
             ['soporte', 'error', 'problema', 'ayuda']):
        return 'Tecnica'

    elif any(palabra in mensaje for palabra in
             ['trabajo', 'cv', 'empleo', 'linkedin']):
        return 'RRHH'

    else:
        return 'General'


def turnos(request):
    mensaje_exito = None

    if request.method == 'POST':
        form = TurnoForm(request.POST)

        if form.is_valid():
            datos = form.cleaned_data

            categoria = clasificar_consulta(datos['mensaje'])

            solicitud = Solicitud.objects.create(
                nombre=datos['nombre'],
                email=datos['email'],
                telefono=datos['telefono'],
                tratamiento=datos['tratamiento'],
                fecha=datos['fecha'],
                mensaje=datos['mensaje'],
                categoria=categoria
            )

            asunto = (
                f'{solicitud.get_categoria_display()} - Alma Spa'
            )

            mensaje = (
                f'Hola {datos["nombre"]},\n\n'
                f'Recibimos correctamente tu solicitud de turno en Alma Spa.\n\n'
                f'Nombre y apellido: {datos["nombre"]}\n'
                f'Email: {datos["email"]}\n'
                f'Teléfono: {datos["telefono"]}\n'
                f'Tratamiento: {datos["tratamiento"]}\n'
                f'Fecha preferida: {datos["fecha"].strftime("%d/%m/%Y")}\n'
                f'Mensaje: {datos["mensaje"]}\n'
                f'Categoría: {solicitud.get_categoria_display()}\n\n'
                f'Nos pondremos en contacto con vos para confirmar el turno.\n\n'
                f'Alma Spa'
            )

            try:
                send_mail(
                    asunto,
                    mensaje,
                    settings.DEFAULT_FROM_EMAIL,
                    [datos['email']],
                    fail_silently=False,
                )

                mensaje_exito = (
                    '¡Tu solicitud de turno fue enviada correctamente!'
                )

            except Exception:
                mensaje_exito = (
                    'Tu solicitud fue registrada correctamente, '
                    'pero no se pudo enviar el correo de confirmación.'
                )

            form = TurnoForm()

    else:
        form = TurnoForm()

    return render(request, 'spa/turnos.html', {
        'form': form,
        'mensaje_exito': mensaje_exito
    })

def usuario_autorizado(usuario):
    return (
        usuario.is_authenticated
        and usuario.is_active
        and UsuarioAutorizado.objects.filter(
            email__iexact=usuario.email
        ).exists()
    )

@login_required(login_url='login')
@user_passes_test(usuario_autorizado, login_url='login')
def panel(request):
    solicitudes = Solicitud.objects.all().order_by('-fecha_creacion')

    total = solicitudes.count()

    comerciales = solicitudes.filter(categoria='Comercial').count()
    tecnicas = solicitudes.filter(categoria='Tecnica').count()
    rrhh = solicitudes.filter(categoria='RRHH').count()
    generales = solicitudes.filter(categoria='General').count()

    return render(request, 'spa/panel.html', {
        'solicitudes': solicitudes,
        'total': total,
        'comerciales': comerciales,
        'tecnicas': tecnicas,
        'rrhh': rrhh,
        'generales': generales
    })

@login_required(login_url='login')
@user_passes_test(usuario_autorizado, login_url='login')
def crear_solicitud(request):
    if request.method == 'POST':
        form = SolicitudForm(request.POST)

        if form.is_valid():
            solicitud = form.save(commit=False)
            solicitud.categoria = clasificar_consulta(
                solicitud.mensaje
            )
            solicitud.save()

            return redirect('panel')

    else:
        form = SolicitudForm()

    return render(request, 'spa/solicitud_form.html', {
        'form': form,
        'titulo': 'Crear solicitud'
    })

@login_required(login_url='login')
@user_passes_test(usuario_autorizado, login_url='login')
def editar_solicitud(request, id):
    solicitud = get_object_or_404(Solicitud, id=id)

    if request.method == 'POST':
        form = SolicitudForm(request.POST, instance=solicitud)

        if form.is_valid():
            solicitud = form.save(commit=False)
            solicitud.categoria = clasificar_consulta(
                solicitud.mensaje
            )
            solicitud.save()

            return redirect('panel')

    else:
        form = SolicitudForm(instance=solicitud)

    return render(request, 'spa/solicitud_form.html', {
        'form': form,
        'titulo': 'Editar solicitud'
    })

@login_required(login_url='login')
@user_passes_test(usuario_autorizado, login_url='login')
def eliminar_solicitud(request, id):
    solicitud = get_object_or_404(Solicitud, id=id)

    if request.method == 'POST':
        solicitud.delete()
        return redirect('panel')

    return render(request, 'spa/eliminar_solicitud.html', {
        'solicitud': solicitud
    })


def registro(request):
    mensaje_exito = None

    if request.method == 'POST':
        form = RegistroForm(request.POST)

        if form.is_valid():
            try:
                with transaction.atomic():
                    usuario = form.save()

                    codigo = str(
                        secrets.randbelow(900000) + 100000
                    )

                    CodigoValidacion.objects.create(
                        usuario=usuario,
                        codigo=codigo
                    )

                    enlace = request.build_absolute_uri(
                        reverse(
                            'validar_cuenta',
                            args=[usuario.id]
                        )
                    )

                    asunto = 'Validación de cuenta - Alma Spa'

                    mensaje = (
                        f'Hola {usuario.first_name},\n\n'
                        f'Tu código de validación es: {codigo}\n\n'
                        f'Ingresá al siguiente enlace para validar '
                        f'tu cuenta:\n{enlace}\n\n'
                        f'Alma Spa'
                    )

                    send_mail(
                        asunto,
                        mensaje,
                        settings.DEFAULT_FROM_EMAIL,
                        [usuario.email],
                        fail_silently=False
                    )

                mensaje_exito = (
                    'Le llegará un correo para validar su cuenta'
                )

                form = RegistroForm()

            except Exception:
                form.add_error(
                    None,
                    'No se pudo completar el registro. '
                    'Intentá nuevamente.'
                )

    else:
        form = RegistroForm()

    return render(request, 'spa/registro.html', {
        'form': form,
        'mensaje_exito': mensaje_exito
    })


def validar_cuenta(request, id):
    usuario = get_object_or_404(User, id=id)

    validacion = get_object_or_404(
        CodigoValidacion,
        usuario=usuario
    )

    error = None
    mensaje_exito = None

    if validacion.utilizado:
        error = 'Esta cuenta ya fue validada.'

    elif not UsuarioAutorizado.objects.filter(
        email__iexact=usuario.email
    ).exists():
        error = (
            'Acceso restringido. No está autorizado '
            'a utilizar este sistema.'
        )

    elif timezone.now() > (
        validacion.fecha_creacion + timedelta(minutes=30)
    ):
        error = 'El código de validación ha vencido.'

    elif request.method == 'POST':
        codigo = request.POST.get('codigo', '').strip()

        if secrets.compare_digest(codigo, validacion.codigo):

            with transaction.atomic():
                usuario.is_active = True
                usuario.save()

                validacion.utilizado = True
                validacion.save()

            mensaje_exito = (
                'Tu cuenta fue validada correctamente. '
                'Ya podés iniciar sesión.'
            )

        else:
            error = 'El código ingresado es incorrecto.'

    return render(request, 'spa/validar_cuenta.html', {
        'usuario': usuario,
        'error': error,
        'mensaje_exito': mensaje_exito
    })


def iniciar_sesion(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)

        email = request.POST.get('username', '').strip().lower()

        if not UsuarioAutorizado.objects.filter(
            email__iexact=email
        ).exists():

            form.add_error(
                None,
                'Acceso restringido. No está autorizado '
                'a utilizar este sistema.'
            )

        elif form.is_valid():
            usuario = form.get_user()
            login(request, usuario)

            return redirect('panel')

    else:
        form = LoginForm(request)

    return render(request, 'spa/login.html', {
        'form': form
    })


@require_POST
@login_required
def cerrar_sesion(request):
    logout(request)
    return redirect('inicio')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_consultas(request):

    if not usuario_autorizado(request.user):
        return Response(
            {
                'error': 'Acceso restringido. No está autorizado a utilizar este sistema.'
            },
            status=status.HTTP_403_FORBIDDEN
        )

    solicitudes = Solicitud.objects.all().order_by(
        '-fecha_creacion'
    )

    serializer = SolicitudSerializer(
        solicitudes,
        many=True
    )

    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_productos_belleza(request):

    if not usuario_autorizado(request.user):
        return Response(
            {
                'error': 'Acceso restringido. No está autorizado a utilizar este sistema.'
            },
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        productos = obtener_productos_belleza()

        return Response({
            'total': len(productos),
            'productos': productos
        })

    except (RequestException, ValueError):
        return Response(
            {
                'error': 'No se pudo obtener información de la API externa.'
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
