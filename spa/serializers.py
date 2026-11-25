
from rest_framework import serializers
from .models import Solicitud


class SolicitudSerializer(serializers.ModelSerializer):

    categoria_nombre = serializers.CharField(
        source='get_categoria_display',
        read_only=True
    )

    class Meta:
        model = Solicitud

        fields = [
            'id',
            'nombre',
            'email',
            'telefono',
            'tratamiento',
            'fecha',
            'mensaje',
            'categoria',
            'categoria_nombre',
            'fecha_creacion',
        ]
