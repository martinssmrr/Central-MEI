from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import validate_email
from .models import Profile
import re

class RegistroUsuarioForm(UserCreationForm):
    nome_completo = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite seu nome completo',
            'id': 'id_nome_completo'
        }),
        label='Nome Completo'
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite seu melhor e-mail',
            'id': 'id_email'
        }),
        label='E-mail'
    )
    
    telefone = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '(00) 00000-0000',
            'id': 'id_telefone'
        }),
        label='Telefone'
    )
    
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite uma senha segura',
            'id': 'id_password1'
        }),
        label='Senha'
    )
    
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirme sua senha',
            'id': 'id_password2'
        }),
        label='Confirmar Senha'
    )
    
    termos = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'id_termos'
        }),
        label='Li e aceito os termos de uso e política de privacidade'
    )

    class Meta:
        model = User
        fields = ('nome_completo', 'email', 'telefone', 'password1', 'password2', 'termos')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este e-mail já está cadastrado em nossa plataforma.")
        return email

    def clean_nome_completo(self):
        nome_completo = self.cleaned_data.get('nome_completo')
        if len(nome_completo.split()) < 2:
            raise forms.ValidationError("Por favor, digite seu nome completo.")
        return nome_completo

    def clean_telefone(self):
        telefone = self.cleaned_data.get('telefone')
        # Remove todos os caracteres não numéricos
        telefone_numeros = re.sub(r'\D', '', telefone)
        
        # Verifica se tem 10 ou 11 dígitos
        if len(telefone_numeros) not in [10, 11]:
            raise forms.ValidationError("Digite um telefone válido com DDD.")
        
        return telefone

    def save(self, commit=True):
        # Salva o usuário
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        
        # Divide o nome completo em primeiro nome e sobrenome
        nome_completo = self.cleaned_data['nome_completo']
        nomes = nome_completo.split()
        user.first_name = nomes[0]
        user.last_name = ' '.join(nomes[1:]) if len(nomes) > 1 else ''
        user.username = self.cleaned_data['email']  # Usa o email como username
        
        if commit:
            user.save()
            # Atualiza ou cria o perfil com o telefone
            profile, created = Profile.objects.get_or_create(user=user)
            profile.telefone = self.cleaned_data['telefone']
            profile.save()
        
        return user