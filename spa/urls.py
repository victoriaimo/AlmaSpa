
from django.urls import path
from . import views

urlpatterns = [
    # Páginas públicas
    path('', views.inicio, name='inicio'),
    path('tratamientos/', views.tratamientos, name='tratamientos'),
    path('espacio/', views.espacio, name='espacio'),
    path('turnos/', views.turnos, name='turnos'),

    # Panel administrativo - CRUD
    path('panel/', views.panel, name='panel'),
    path('panel/crear/', views.crear_solicitud, name='crear_solicitud'),
    path('panel/editar/<int:id>/', views.editar_solicitud, name='editar_solicitud'),
    path('panel/eliminar/<int:id>/', views.eliminar_solicitud, name='eliminar_solicitud'),

    # Autenticación
    path('registro/', views.registro, name='registro'),
    path('validar-cuenta/<int:id>/', views.validar_cuenta, name='validar_cuenta'),
    path('login/', views.iniciar_sesion, name='login'),
    path('logout/', views.cerrar_sesion, name='logout'),

    # API propia
    path('api/consultas/', views.api_consultas, name='api_consultas'),

    # API externa
    path('api/productos/', views.api_productos_belleza, name='api_productos'),
]
