"""
Context processors para disponibilizar variáveis globais nos templates
"""
from django.conf import settings

def company_context(request):
    """
    Adiciona informações da empresa aos templates
    """
    return {
        'COMPANY_NAME': settings.COMPANY_NAME,
        'COMPANY_PHONE': settings.COMPANY_PHONE, 
        'COMPANY_EMAIL': settings.COMPANY_EMAIL,
        'COMPANY_ADDRESS': settings.COMPANY_ADDRESS,
        'CONTACT_EMAIL': settings.CONTACT_EMAIL,
    }