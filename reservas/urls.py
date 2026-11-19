from django.urls import path
from . import views

app_name = "reservas"

urlpatterns = [
    path("", views.EspacioListView.as_view(), name="lista"),
    path("espacios/<int:pk>/", views.EspacioDetailView.as_view(), name="detalle"),
    path("nueva/", views.ReservaCreateView.as_view(), name="nueva"),
    path("mias/", views.MisReservasView.as_view(), name="mias"),
]