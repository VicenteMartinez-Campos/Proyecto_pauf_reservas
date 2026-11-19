from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.urls import reverse

# Create your models here.
class Espacio(models.Model):
    class Tipo(models.TextChoices):
        AULA = "aula", "Aula"
        LABORATORIO = "laboratorio", "Laboratorio"
        SALON = "salon", "Salón de actos"
        PISTA = "pista", "Pista deportiva"

    nombre = models.CharField(max_length=80, unique=True)
    tipo = models.CharField(max_length=20, choices=Tipo.choices)
    aforo = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    def get_absolute_url(self):
        return reverse("reservas:detalle", args=[self.pk])

class Reserva(models.Model):
    class Estado(models.TextChoices):
            PENDIENTE = "pendiente", "Pendiente"
            CONFIRMADA = "confirmada", "Confirmada"
            CANCELADA = "cancelada", "Cancelada"

    espacio = models.ForeignKey(Espacio, on_delete=models.PROTECT, related_name="reservas")
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reservas")
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    motivo = models.CharField(max_length=200)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.PENDIENTE)
    creada = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['fecha', 'hora_inicio']
        constraints = [
            models.CheckConstraint(
                condition=models.Q(hora_fin__gt=models.F("hora_inicio")),
                name="reserva_fin_posterior_inicio",
            ),
        ]

    def __str__(self):
        return f"{self.espacio} {self.fecha:%d/%m/%Y} {self.hora_inicio:%H:%M}-{self.hora_fin:%H:%M}"

    def solapes(self):
        """Comprueba si existe otra reserva confirmada que se solape con este horario."""
        return Reserva.objects.filter(
            espacio_id=self.espacio_id,
            fecha=self.fecha,
            estado=Reserva.Estado.CONFIRMADA,
            hora_inicio__lt=self.hora_fin,
            hora_fin__gt=self.hora_inicio
        ).exclude(pk=self.pk).exists()

    def clean(self):
        if self.hora_inicio and self.hora_fin:
            if self.hora_fin <= self.hora_inicio:
                raise ValidationError(
                    {"hora_fin": "La hora fin debe ser posterior a la hora inicio."}
                )

        if self.espacio_id:
            if not self.espacio.activo:
                raise ValidationError({"espacio": "El espacio no está disponible para reservas."})

        if self.estado != self.Estado.CANCELADA and self.espacio_id and self.fecha and self.hora_inicio and self.hora_fin:
            if self.solapes():
                raise ValidationError("El espacio ya tiene una reserva confirmada que se solapa con ese horario.")