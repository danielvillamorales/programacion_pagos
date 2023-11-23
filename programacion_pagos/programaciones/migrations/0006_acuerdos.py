# Generated by Django 4.2.6 on 2023-11-23 18:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('programaciones', '0005_programacionpagosaprobados_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Acuerdos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('año', models.IntegerField()),
                ('mes', models.IntegerField()),
                ('dia', models.IntegerField()),
                ('proovedoor', models.CharField(max_length=300)),
                ('cuota', models.IntegerField()),
                ('observaciones', models.CharField(max_length=300)),
                ('estado', models.CharField(choices=[('0', 'Pendiente'), ('1', 'Aprobado Jefe'), ('9', 'Rechazado')], default='0', max_length=2)),
            ],
        ),
    ]
