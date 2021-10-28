from django.contrib import admin
from .models import *

from .forms import CustomUserCreationForm, CustomUserChangeForm
from django.contrib.auth.admin import UserAdmin
from .models import Usuario


# Register your models here.
admin.site.register(Caso)
admin.site.register(EstadoCaso)
admin.site.register(Evidencia)
admin.site.register(EstadoEvidencia)
admin.site.register(Registro)
admin.site.register(SubllaveRegistro)
admin.site.register(LlaveRegistro)
admin.site.register(ArchivoRegistro)
admin.site.register(Prefetch)
admin.site.register(InformeConsolidado)
admin.site.register(EstadoInforme)
admin.site.register(InformeDetallado)
admin.site.register(Cliente)

# https://testdriven.io/blog/django-custom-user-model/
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = Usuario
    list_display = ('email', 'empresa', 'is_staff', 'is_active',)
    list_filter = ('email', 'empresa', 'is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('email', 'empresa', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'empresa', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)

admin.site.register(Usuario, CustomUserAdmin)
