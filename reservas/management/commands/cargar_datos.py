from datetime import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from reservas.models import Espacio, Reserva


USUARIOS = [
    {'username': 'profe1', 'password': 'Clave.2026', 'is_staff': False},
    {'username': 'profe2', 'password': 'Clave.2026', 'is_staff': False},
    {'username': 'conserje', 'password': 'Clave.2026', 'is_staff': True},
]

ESPACIOS = [
    {'nombre': 'Aula 12', 'tipo': 'aula', 'aforo': 30, 'activo': True},
    {'nombre': 'Laboratorio de Física', 'tipo': 'laboratorio', 'aforo': 24, 'activo': True},
    {'nombre': 'Salón de actos', 'tipo': 'salon', 'aforo': 200, 'activo': True},
    {'nombre': 'Pista polideportiva', 'tipo': 'pista', 'aforo': 60, 'activo': True},
    {'nombre': 'Aula 3', 'tipo': 'aula', 'aforo': 25, 'activo': False},
]

RESERVAS = [
    {
        'espacio': 'Aula 12', 'fecha': '2027-05-20', 'horario': '09:00-10:00', 
        'usuario': 'profe1', 'estado': 'confirmada', 'motivo': 'Examen de Matemáticas'
        },
    {
        'espacio': 'Aula 12', 'fecha': '2027-05-20', 'horario': '10:00-11:00',
        'usuario': 'profe2', 'estado': 'confirmada', 'motivo': 'Tutoría de 2.º DAW'
    },
    {
        'espacio': 'Salón de actos', 'fecha': '2027-05-20', 'horario': '12:00-14:00',
        'usuario': 'profe1', 'estado': 'pendiente', 'motivo': 'Charla de orientación'
    },
    {
        'espacio': 'Laboratorio de Física', 'fecha': '2027-05-24', 'horario': '08:30-10:20',
        'usuario': 'profe2', 'estado': 'confirmada', 'motivo': 'Práctica de óptica'
    },
    {
        'espacio': 'Pista polideportiva', 'fecha': '2027-05-24', 'horario': '11:15-12:10',
        'usuario': 'profe1', 'estado': 'cancelada', 'motivo': 'Torneo de recreo'
    },
    {
        'espacio': 'Aula 12', 'fecha': '2027-05-24', 'horario': '09:00-10:00',
        'usuario': 'profe1', 'estado': 'pendiente', 'motivo': 'Recuperación'
    },
]

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        Reserva.objects.all().delete()
        usuarios = {}
        for user_data in USUARIOS:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={'is_staff': user_data['is_staff']}
            )
            user.set_password(user_data['password'])
            user.save()
            usuarios[user_data['username']] = user

        espacios = {}
        contador_espacios = 0
        for espacio_data in ESPACIOS:
            espacio, created = Espacio.objects.update_or_create(
                nombre=espacio_data['nombre'],
                defaults={
                    'tipo': espacio_data['tipo'],
                    'aforo': espacio_data['aforo'],
                    'activo': espacio_data['activo']
                }
            )
            espacios[espacio_data['nombre']] = espacio
            contador_espacios += 1

        contador_reservas = 0
        for r_data in RESERVAS:
            horario_str = r_data['horario']
            inicio, fin = [h.strip() for h in horario_str.split('-')]
            Reserva.objects.create(
                espacio=espacios[r_data['espacio']],
                fecha=datetime.strptime(r_data['fecha'], '%Y-%m-%d').date(),
                hora_inicio=datetime.strptime(inicio, '%H:%M').time(),
                hora_fin=datetime.strptime(fin, '%H:%M').time(),
                usuario=usuarios[r_data['usuario']],
                estado=r_data['estado'],
                motivo=r_data['motivo']
            )
            contador_reservas += 1