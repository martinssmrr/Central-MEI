from django.apps import AppConfig


class ServicosConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "servicos"
    verbose_name = "Serviços MEI"
    
    def ready(self):
        """
        Carrega os signals quando a aplicação está pronta.
        
        Isso garante que os signals de automação entre solicitações MEI
        e o painel financeiro sejam registrados corretamente.
        """
        import servicos.signals
