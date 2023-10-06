from django.db import models
from datetime import date

# Create your models here.


ESTADOS = (
    ('0', 'Pendiente'),
    ('1', 'Aprobado Jefe'),
    ('9', 'Rechazado')
)

class Pagos(models.Model):
    fecha_pago = models.DateField(default=date.today)
    empresa = models.CharField(max_length=20, default='ka')
    emision = models.DateField()
    vencimiento = models.DateField()
    nit = models.CharField(max_length=20)
    proveedor = models.CharField(max_length=200)
    descripcion = models.CharField(max_length=100)
    concepto = models.CharField(max_length=100)
    descuento = models.CharField(max_length=20)
    valor = models.IntegerField(default=0)
    estado = models.CharField(max_length=2 , choices=ESTADOS, default='0')


    class Meta:
        permissions = [('subir_excel', 'subir_excel'),
                       ('aprobar_pago', 'aprobar_pago'),
                       ]