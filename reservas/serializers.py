import copy

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from .models import Espacio, Reserva

class EspacioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Espacio
        fields = ["id", "nombre", "tipo", "aforo", "activo"]

class ReservaSerializer(serializers.ModelSerializer):
    usuario = serializers.CharField(source="usuario.username", read_only=True)
    espacio_nombre = serializers.CharField(source="espacio.nombre", read_only=True)
    class Meta:
        model = Reserva
        fields = ["id", "espacio", "espacio_nombre", "usuario", "fecha",
                  "hora_inicio", "hora_fin", "motivo", "estado", "creada"]
        read_only_fields = ["estado", "creada", "usuario", "espacio_nombre"]

    def validate(self, datos):
        reserva = copy.copy(self.instance) if self.instance else Reserva()
        for campo, valor in datos.items():
            setattr(reserva, campo, valor)
        try:
            reserva.clean()
        except DjangoValidationError as error:
            mensajes = error.message_dict if hasattr(error, "error_dict") else error.messages
            raise serializers.ValidationError(mensajes)
        return datos