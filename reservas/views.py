from django.http import Http404
from django.shortcuts import get_object_or_404, render
from .models import Espacio, Reserva
from django.utils import timezone
from django.views.generic import DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView
from .forms import ReservaForm
from django.urls import reverse_lazy

ESPACIOS = [
    {"id": 1, "nombre": "Aula 12", "tipo": "aula", "aforo": 30, "utilidad": "clases"},
    {"id": 2, "nombre": "Laboratorio de Física", "tipo": "laboratorio", "aforo": 24, "utilidad": "física"},
    {"id": 3, "nombre": "Salón de actos", "tipo": "salon", "aforo": 200, "utilidad": "actos"}
]

def buscar(pk):
    for espacio in ESPACIOS:
        if espacio["id"] == pk:
            return espacio
    raise Http404("El espacio no existe")

def lista(request):
    espacios = Espacio.objects.filter(activo=True)
    return render(request, "reservas/lista.html", {"espacios": espacios})

def detalle(request, pk):
    espacio = get_object_or_404(Espacio, pk=pk)
    return render(request, "reservas/detalle.html", {"espacio": espacio})

class EspacioListView(ListView):
    template_name = "reservas/lista.html"
    context_object_name = "espacios"
    def get_queryset(self):
        return Espacio.objects.filter(activo=True)

class EspacioDetailView(DetailView):
    model = Espacio
    template_name = "reservas/detalle.html"
    context_object_name = "espacio"
    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["reservas"] = self.object.reservas.filter(
            estado="confirmada", fecha__gte=timezone.localdate()
        ).select_related("usuario")
        return contexto

class ReservaCreateView(LoginRequiredMixin, CreateView):
    model = Reserva
    form_class = ReservaForm
    template_name = "reservas/reserva_form.html"
    success_url = reverse_lazy("reservas:mias")
    def form_valid(self, form):
        form.instance.usuario = self.request.user
        return super().form_valid(form)

class MisReservasView(LoginRequiredMixin, ListView):
    model = Reserva
    form_class = ReservaForm
    template_name = "reservas/mis_reservas.html"
    context_object_name = "reservas"
    def get_queryset(self):
        return Reserva.objects.filter(usuario=self.request.user).select_related("espacio")