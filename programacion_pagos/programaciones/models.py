from django.db import models
from datetime import date

# Create your models here.


ESTADOS = (
    ('0', 'Pendiente'),
    ('1', 'Aprobado Jefe'),
    ('9', 'Rechazado')
)

TIPO_CUENTA = ( 
    ('a', 'Ahorros'),
    ('c','Corriente'),
    ('o', 'Otra')
)

ESTADOS_CUENTA = (
    ('0', 'Activa'),
    ('1', 'Inactiva')
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

    def __str__(self) -> str:
        return f'{self.id} {self.nit} - {self.proveedor} - {self.descripcion} - {self.concepto} - {self.valor}'

    class Meta:
        permissions = [('subir_excel', 'subir_excel'),
                       ('aprobar_pago', 'aprobar_pago'),
                       ]
        


class CuentasBancarias(models.Model):
    nit = models.CharField(max_length=20)
    digito_verificacion = models.CharField(max_length=1, blank=True, null=True)
    proveedor = models.CharField(max_length=200)
    banco = models.CharField(max_length=100)
    tipo_cuenta = models.CharField(max_length=1, choices=TIPO_CUENTA, default='a')
    numero_cuenta = models.CharField(max_length=20)
    estado = models.CharField(max_length=2 , choices=ESTADOS_CUENTA, default='0')

    def __str__(self):
        return f'{self.nit} - {self.proveedor} - {self.banco} - {self.tipo_cuenta} - {self.numero_cuenta}'
    
class ProgramacionPagosAprobados(models.Model):
    id = models.BigIntegerField(primary_key=True)
    fecha_pago = models.DateField(blank=True, null=True)
    emision = models.DateField(blank=True, null=True)
    vencimiento = models.DateField(blank=True, null=True)
    nit = models.CharField(max_length=20, blank=True, null=True)
    proveedor = models.CharField(max_length=200, blank=True, null=True)
    descripcion = models.CharField(max_length=100, blank=True, null=True)
    concepto = models.CharField(max_length=100, blank=True, null=True)
    descuento = models.CharField(max_length=20, blank=True, null=True)
    valor = models.IntegerField(blank=True, null=True)
    estado = models.CharField(max_length=2, blank=True, null=True)
    empresa = models.CharField(max_length=20, blank=True, null=True)
    cuentas_concatenadas = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'programacion_pagos_aprobados'


class Acuerdos(models.Model):
    año = models.IntegerField()
    mes = models.IntegerField()
    dia = models.IntegerField()
    proovedoor = models.CharField(max_length=300)
    cuota = models.IntegerField()
    observaciones = models.CharField(max_length=300, blank=True, null=True)
    estado = models.CharField(max_length=2 , choices=ESTADOS, default='0')

    def __str__(self):
        return f'{self.año} - {self.mes} - {self.dia} - {self.proovedoor} - {self.cuota} - {self.observaciones} - {self.estado}'