import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    """
    Gestionnaire d'erreurs personnalisé pour DRF.
    """
    # Appelle le gestionnaire par défaut fourni par DRF
    response = exception_handler(exc, context)

    if response is not None:
        response.data['status_code'] = response.status_code
    else:
        # Si aucune réponse DRF n'est définie, crée une réponse générique
        logger.error(f"Unhandled exception: {exc}")
        return Response(
            {"detail": "Une erreur interne est survenue."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return response
