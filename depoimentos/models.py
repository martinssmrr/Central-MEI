from django.db import models

class Depoimento(models.Model):
    nome = models.CharField(max_length=100)
    foto = models.ImageField(upload_to='depoimentos/', blank=True, null=True)
    conteudo = models.TextField(max_length=500)
    cargo = models.CharField(max_length=100, blank=True)
    empresa = models.CharField(max_length=100, blank=True)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-criado_em']
        verbose_name = 'Depoimento'
        verbose_name_plural = 'Depoimentos'

    def __str__(self):
        return f"Depoimento de {self.nome}"
