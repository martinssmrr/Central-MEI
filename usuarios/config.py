# Configurações para o sistema de usuários
# Este arquivo contém configurações personalizadas para o app de usuários

# Configurações de validação de senha
PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# URLs de redirecionamento
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = '/usuarios/login/'

# Configurações de e-mail (para futuras funcionalidades)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Para desenvolvimento

# Mensagens de sucesso personalizadas
MESSAGES = {
    'REGISTRO_SUCESSO': 'Conta criada com sucesso! Bem-vindo(a)!',
    'LOGIN_SUCESSO': 'Bem-vindo de volta!',
    'LOGOUT_SUCESSO': 'Você saiu com sucesso!',
}

# Campos obrigatórios para cadastro
REQUIRED_FIELDS = ['nome_completo', 'email', 'telefone', 'password1', 'password2']

# Configurações de telefone
PHONE_VALIDATION = {
    'MIN_LENGTH': 10,
    'MAX_LENGTH': 11,
    'FORMAT_REGEX': r'^\(\d{2}\)\s\d{4,5}-\d{4}$'
}