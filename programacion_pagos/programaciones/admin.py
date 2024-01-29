from django.contrib import admin
from .models import CuentasBancarias, Pagos

# Register your models here.
admin.site.register(CuentasBancarias)


@admin.register(Pagos)
class PermisosAdmin(admin.ModelAdmin):
    list_display = ('fecha_pago','nit', 'proveedor','valor','estado','empresa')
    search_fields = ('fecha_pago','nit', 'proveedor','valor','estado','empresa')
    ordering = ('-id',)