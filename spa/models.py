
from django.db import models
from django.contrib.auth.models import User


class Solicitud(models.Model):

    CATEGORIAS = [
        ('Comercial', 'Consulta Comercial'),
        ('Tecnica', 'Consulta Técnica'),
        ('RRHH', 'Consulta de RRHH'),
        ('General', 'Consulta General'),
    ]

    nombre = models.CharField(max_length=100)
    email = models.EmailField()
    telefono = models.CharField(max_length=20)
    tratamiento = models.CharField(max_length=100)
    fecha = models.DateField()
    mensaje = models.TextField()
    categoria = models.CharField(
        max_length=20,
        choices=CATEGORIAS,
        default='General'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre



class UsuarioAutorizado(models.Model):
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email



class CodigoValidacion(models.Model):
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    codigo = models.CharField(max_length=6)

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    utilizado = models.BooleanField(default=False)

    def __str__(self):
        return self.usuario.email
