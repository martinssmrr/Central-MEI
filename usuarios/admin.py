from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Profile

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Perfil'
    fields = ('telefone',)

class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_telefone', 'is_active', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'profile__telefone')
    
    def get_telefone(self, obj):
        return obj.profile.telefone if hasattr(obj, 'profile') else 'N/A'
    get_telefone.short_description = 'Telefone'

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'telefone', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__username', 'user__email', 'telefone')
    readonly_fields = ('created_at', 'updated_at')

# Desregistra o UserAdmin padrão e registra o customizado
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
