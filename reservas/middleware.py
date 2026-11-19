import logging

logger = logging.getLogger("reservas.peticiones")

class RegistroPeticionesMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.user.is_authenticated:
            nombre =  request.user.username
        else:
            nombre = "anonimo"
        logger.info("%s %s %s %s", request.method, request.path, response.status_code, nombre)
        return response

