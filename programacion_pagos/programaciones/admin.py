from django.contrib import admin
from .models import CuentasBancarias, Pagos, Acuerdos

# Register your models here.
admin.site.register(CuentasBancarias)


@admin.register(Pagos)
class PagosAdmin(admin.ModelAdmin):
    list_display = (
        "fecha_pago",
        "nit",
        "proveedor",
        "valor",
        "estado",
        "descripcion",
    )
    search_fields = (
        "fecha_pago",
        "nit",
        "proveedor",
        "valor",
        "estado",
        "empresa",
        "descripcion",
    )
    list_filter = ("estado", "empresa", "fecha_pago")
    list_editable = ("estado",)
    ordering = ("-id",)


@admin.register(Acuerdos)
class AcuerdosAdmin(admin.ModelAdmin):
    list_display = (
        "año",
        "mes",
        "dia",
        "nit",
        "proovedoor",
        "cuota",
        "estado",
    )
    search_fields = (
        "año",
        "mes",
        "dia",
        "nit",
        "proovedoor",
        "cuota",
        "estado",
    )
    list_filter = ("estado", "año", "mes", "dia")
    list_editable = ("estado",)
    ordering = ("-id",)
