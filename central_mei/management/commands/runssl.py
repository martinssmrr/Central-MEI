"""
Comando Django para executar servidor com SSL
"""
import os
from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Executa o servidor Django com SSL para desenvolvimento'

    def add_arguments(self, parser):
        parser.add_argument(
            '--host',
            default='127.0.0.1',
            help='Host para o servidor (padrão: 127.0.0.1)'
        )
        parser.add_argument(
            '--port',
            default='8000',
            help='Porta para o servidor (padrão: 8000)'
        )

    def handle(self, *args, **options):
        host = options['host']
        port = options['port']
        
        # Caminhos dos certificados
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        cert_file = os.path.join(base_dir, 'ssl', 'cert.pem')
        key_file = os.path.join(base_dir, 'ssl', 'key.pem')
        
        # Verificar se os certificados existem
        if not os.path.exists(cert_file) or not os.path.exists(key_file):
            self.stdout.write(
                self.style.ERROR('Certificados SSL não encontrados!')
            )
            self.stdout.write('Execute: python generate_ssl.py')
            return
        
        self.stdout.write(
            self.style.SUCCESS(f'🚀 Iniciando servidor HTTPS em https://{host}:{port}/')
        )
        self.stdout.write(f'📁 Usando certificados em: {os.path.dirname(cert_file)}')
        self.stdout.write('⚠️ Certificado auto-assinado - aceite o aviso de segurança no navegador')
        
        # Executar runserver_plus com SSL
        try:
            call_command('runserver_plus', 
                        f'{host}:{port}',
                        cert_file=cert_file,
                        key_file=key_file)
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erro ao iniciar servidor SSL: {e}')
            )
            self.stdout.write('Certifique-se de que django-extensions está instalado')