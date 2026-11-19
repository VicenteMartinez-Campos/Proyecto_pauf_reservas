from datetime import date
from django.db.models import ProtectedError
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import serializers
from django.db.models import ProtectedError

from .models import Espacio, Reserva
from .serializers import EspacioSerializer, ReservaSerializer
from .consultas import ocupacion

class EspacioViewSet (viewsets.ModelViewSet):
    queryset = Espacio.objects.all()
    serializer_class = EspacioSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        tipo = self.request.query_params.get('tipo')
        activo = self.request.query_params.get('activo')

        if tipo:
            queryset = queryset.filter(tipo=tipo)
        
        if activo is not None:
            if activo.lower() == 'true':
                queryset = queryset.filter(activo=True)
            elif activo.lower() == 'false':
                queryset = queryset.filter(activo=False)

        return queryset

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                {"detail": "El espacio tiene reservas y no se puede borrar."},
                status=status.HTTP_409_CONFLICT,
            )

    @action(detail=False, url_path="ocupacion")
    def ocupacion_del_dia(self, request):
        fecha_str = request.query_params.get('fecha')
        if not fecha_str:
            return Response(
                {"detail": "Falta el parámetro fecha (AAAA-MM-DD)."},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            fecha = date.fromisoformat(fecha_str)
        except ValueError:
            return Response(
                {"fecha": "Formato de fecha no válido (AAAA-MM-DD)."},
                status=status.HTTP_400_BAD_REQUEST
            )

        datos = ocupacion(fecha)
        return Response(datos)


class ReservaViewSet (viewsets.ModelViewSet):
    serializer_class = ReservaSerializer

    def get_queryset(self):
        queryset = Reserva.objects.select_related('espacio', 'usuario').all()

        fecha_str = self.request.query_params.get('fecha')
        espacio_id = self.request.query_params.get('espacio')
        estado = self.request.query_params.get('estado')

        if fecha_str:
            try:
                fecha = date.fromisoformat(fecha_str)
                queryset = queryset.filter(fecha=fecha)
            except ValueError:
                raise serializers.ValidationError({"fecha": "Formato de fecha no válido (AAAA-MM-DD)."})

        if espacio_id:
            if not espacio_id.isdigit():
                raise serializers.ValidationError({"espacio": "El id del espacio debe ser un número."})
            queryset = queryset.filter(espacio_id=espacio_id)

        if estado:
            queryset = queryset.filter(estado=estado)

        return queryset

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)