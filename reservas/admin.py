from django.contrib import admin
from .models import Espacio, Reserva

# Register your models here.
@admin.register(Espacio)
class Espacios(admin.ModelAdmin):
    list_display = ["nombre", "tipo", "aforo", "activo"]
    list_filter = ["tipo", "activo"]
    search_fields = ["nombre"]

@admin.register(Reserva)
class Reservas(admin.ModelAdmin):
    list_display = ["espacio", "fecha", "hora_inicio", "hora_fin", "usuario", "estado"]
    list_filter = ["estado", "espacio", "fecha"]
    search_fields = ["motivo", "usuario__username"]
    list_select_related = ["espacio", "usuario"]
    readonly_fields = ["creada"]