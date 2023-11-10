from django.contrib import admin
from .models import CuentasBancarias, Pagos

# Register your models here.
admin.site.register(CuentasBancarias)
admin.site.register(Pagos)