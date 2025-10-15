from django.db import models

class Plano(models.Model):
    nome = models.CharField(max_length=100)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    descricao = models.TextField()
    beneficios = models.JSONField(default=list, help_text="Lista de benefícios")
    ativo = models.BooleanField(default=True)
    destaque = models.BooleanField(default=False, help_text="Plano em destaque")
    ordem = models.IntegerField(default=0, help_text="Ordem de exibição")
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['ordem', 'preco']
        verbose_name = 'Plano'
        verbose_name_plural = 'Planos'

    def __str__(self):
        return self.nome
