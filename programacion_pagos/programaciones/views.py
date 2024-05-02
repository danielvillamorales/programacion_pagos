from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import datetime, date, timedelta
import openpyxl
from .models import Pagos, CuentasBancarias,ProgramacionPagosAprobados,Acuerdos
import xlwt
from django.http import HttpResponse
from io import BytesIO
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db.models import F, Value, Case, When, CharField, Value, IntegerField
from django.db.models.functions import Concat
from django.db.models import Subquery, OuterRef
from django.db.models import Sum
import locale
import pandas as pd
import io

# Create your views here.
ESTADO = {'0':'Pendiente', '1':'Aprobado Jefe', '9':'Rechazado'}
EMPRESAS_PERMITIDAS = ["ka", "pendientes", "dyjon", "pulman","nomina"]
MESES = {1:'Enero', 2:'Febrero', 3:'Marzo', 4:'Abril', 5:'Mayo', 6:'Junio', 
         7:'Julio', 8:'Agosto', 9:'Septiembre', 10:'Octubre', 11:'Noviembre', 
         12:'Diciembre'}

def crearObjeto(**kwargs):
    pago = Pagos()
    pago.fecha_pago = kwargs.get("fecha_pago", date.today())
    pago.empresa = kwargs.get("empresa", "ka")
    pago.emision =   datetime.strptime(kwargs.get("emision", date.today()), '%d/%m/%Y').date() 
    pago.vencimiento = datetime.strptime(kwargs.get("vencimiento", date.today()), '%d/%m/%Y').date() 
    pago.nit = kwargs.get("nit", "0")
    pago.proveedor = kwargs.get("proveedor", "0")
    pago.descripcion = kwargs.get("descripcion", "0")
    pago.concepto = kwargs.get("concepto", "0")
    pago.descuento = kwargs.get("descuento", "0")
    pago.valor = kwargs.get("valor", 0)
    pago.estado = kwargs.get("estado", "0")
    return pago
    

def importar_excel(request):
    if request.user.has_perm('programaciones.subir_excel'):
        try:
            #obtener el archivo de excel
            excel_file = request.FILES["excel_file"]

            #importar el archivo de excel 
            wb = openpyxl.load_workbook(excel_file)
            #obtener la hoja de excel
            sheet = wb.get_sheet_by_name('pagos')
            contador = 0
            pagos = []
            #iterar sobre las filas de la hoja
            for r in sheet.rows:
                row_data = {
                "empresa" : r[0].value,
                "emision" :str(r[1].value),
                "vencimiento" : str(r[2].value),
                "nit" : r[3].value,
                "proveedor" : r[4].value,
                "descripcion" : r[5].value,
                "concepto" : r[6].value,
                "descuento" : r[7].value,
                "valor" : int(str(r[8].value))
                }
                pago = crearObjeto(**row_data)
                contador += 1
                if pago.empresa in EMPRESAS_PERMITIDAS:
                    pagos.append(pago)
                else:
                    messages.warning(request, f'Error en la linea {contador} Empresa ({pago.empresa}) no permitida las unicas permitidas son: (ka, dyjon, pulman, pendientes)')
                    return render(request, 'importar.html')
            Pagos.objects.bulk_create(pagos)
            messages.success(request, 'Programacion de pagos subida correctamente')

        except Exception as e:
            messages.error(request, f'Error al subir programacion de pagos: (estructura del archivo o nombre de la hoja incorrectos) {e}')
    else:
        messages.warning(request, 'No tiene permisos para subir la programacion de pagos')
    return render(request, 'importar.html')



def importar(request):
    if request.method == 'POST':
        importar_excel(request)
    return render(request, 'importar.html')

@login_required(login_url='login') 
def consulta(request):
    if request.method == 'POST':
        print('entro al post')
        check = request.POST.getlist('check')
        boton = request.POST.get('boton')
        print(boton)
        if len(check) == 0:
            messages.warning(request, 'No se seleccionaron pagos')

        if boton == 'aprobar':
            Pagos.objects.filter(id__in=check).update(estado='1')
            messages.success(request, 'Pagos aprobados correctamente')
        elif boton == 'rechazar':
            Pagos.objects.filter(id__in=check).update(estado='9')
            messages.success(request, 'Pagos rechazados correctamente')
        else:
            messages.warning(request, 'Error al aprobar o rechazar pagos')
    pagos_nomina = Pagos.objects.filter(fecha_pago = date.today(), empresa = 'nomina').order_by('estado','vencimiento','-valor')
    pagos = Pagos.objects.filter(fecha_pago = date.today(), empresa = 'ka').order_by('estado','vencimiento','-valor')
    pagos_dyjon = Pagos.objects.filter(fecha_pago = date.today(), empresa = 'dyjon').order_by('estado','vencimiento','-valor')
    pagos_pulman = Pagos.objects.filter(fecha_pago = date.today(), empresa = 'pulman').order_by('estado','vencimiento','-valor')

    pagos_rechazados = pagos.filter(estado = '9')
    total_rechazados = sum(pago.valor for pago in pagos_rechazados)
    total = sum(pago.valor for pago in pagos) - total_rechazados
    pagos_rechazados_dyjon = pagos_dyjon.filter(estado = '9')
    total_rechazados_dyjon = sum(pago.valor for pago in pagos_rechazados_dyjon)
    total_dyjon = sum(pago.valor for pago in pagos_dyjon) - total_rechazados_dyjon
    pagos_rechazados_pulman = pagos_pulman.filter(estado = '9') 
    total_rechazados_pulman = sum(pago.valor for pago in pagos_rechazados_pulman)
    total_pulman = sum(pago.valor for pago in pagos_pulman)  - total_rechazados_pulman
    total_nomina = sum(pago.valor for pago in pagos_nomina)
    return render(request, 'consulta.html', {'pagos':pagos, 'total':total, 'pagos_dyjon':pagos_dyjon,
                                             'pagos_nomina':pagos_nomina, 'total_nomina':total_nomina,
                                              'total_dyjon':total_dyjon, 'pagos_pulman':pagos_pulman,
                                                'total_pulman':total_pulman, 'total_rechazados_dyjon':total_rechazados_dyjon, 
                                                 'total_rechazados_pulman':total_rechazados_pulman, 'total_rechazados':total_rechazados })


def aprobar(request, id):
    if request.user.has_perm('programaciones.aprobar_pago'):
        pago = Pagos.objects.get(id=id)
        pago.estado = '1'
        pago.save()
    else:
        messages.warning(request, 'No tiene permisos para aprobar pagos')
    return redirect('consulta')

def rechazar(request, id):
    if request.user.has_perm('programaciones.aprobar_pago'):
        pago = Pagos.objects.get(id=id)
        pago.estado = '9'
        pago.save()
    else:
        messages.warning(request, 'No tiene permisos para rechazazr pagos')
    return redirect('consulta')

def aprobar_todo(request):
    if request.user.has_perm('programaciones.aprobar_pago'):
        Pagos.objects.filter(Q(fecha_pago=date.today()) & Q(estado='0') & ~Q(empresa='pendientes')).update(estado='1')
        messages.success(request, 'Pagos aprobados correctamente')
    else:
        messages.warning(request, 'No tiene permisos para aprobar pagos')
    return redirect('consulta')

def pendientes(request):
    pagos = Pagos.objects.filter(fecha_pago = date.today(), estado = '0', empresa = 'pendientes').order_by('vencimiento','-valor')
    total = sum(pago.valor for pago in pagos)
    # Consulta para obtener el monto total de los pagos por mes
    pagos_por_mes = Pagos.objects.filter(fecha_pago = date.today(), 
                                         estado = '0', 
                                         empresa = 'pendientes'
                                         ).values('vencimiento__month', 'vencimiento__year'
                                                  ).annotate(total=Sum('valor')
                                                             ).order_by('vencimiento__year', 'vencimiento__month')
    print(pagos_por_mes)
    return render(request, 'pendientes.html', {'pagos':pagos, 'total':total,
                                             'pagos_por_mes':pagos_por_mes })

def pendientes_next(request):
    pagos = Pagos.objects.filter(fecha_pago =date.today(), vencimiento = date.today() + timedelta(days=1), estado = '0',
                                  empresa = 'pendientes').order_by('vencimiento','-valor')
    total = sum(pago.valor for pago in pagos)
    total_rechazados_pulman = 0 
    total_rechazados_dyjon = 0
    total_rechazados = 0 
    
    return render(request, 'consulta.html', {'pagos':pagos, 'total':total, 
                                             'total_rechazados_pulman':total_rechazados_pulman,
                                             'total_rechazados_dyjon':total_rechazados_dyjon, 'total_rechazados':total_rechazados})

def borrar_pendientes(request):
    if request.user.has_perm('programaciones.subir_excel'):
        Pagos.objects.filter(fecha_pago = date.today(), estado = '0').delete()
        messages.success(request, 'Pagos pendientes borrados correctamente')
    else:
        messages.warning(request, 'No tiene permisos para borrar pagos pendientes')
    return redirect('importar')

def historico(request):
    if request.method == 'POST':
        if request.POST.get('tipo') == 'acuerdo':
            return exportar_acuerdo(request)
        else:
            return exportar_clientes(request)
    return render(request, 'historico.html')


def pagos_aprobados(request):
    fecha = date.today()
    if request.method == 'POST':
        if request.POST.get('tipo') == 'buscador':
            print('entro al buscador')
            fecha = datetime.strptime(request.POST.get('ifecha'), '%Y-%m-%d').date()
        else: 
            numero = request.POST.get('validar')

            if 'acuerdo' in numero:
                print('entro al acuerdo')
                numero = numero.replace('acuerdo','')
                acuerdo = Acuerdos.objects.get(pk=numero)
                acuerdo.revision = '1'
                acuerdo.save()
                fecha = date(acuerdo.año, acuerdo.mes, acuerdo.dia)
            else:  
                pago = Pagos.objects.get(pk=numero)
                pago.revision = 1
                pago.save()
                fecha = pago.fecha_pago
            
    pagos = ProgramacionPagosAprobados.objects.filter(fecha_pago = fecha, 
                                 estado = '1').order_by('revision','empresa', '-valor')  
    #acuerdos = Acuerdos.objects.filter(año = fecha.year,
    #                                 mes = fecha.month, 
    #                                dia = fecha.day , estado = '1').values_list('año','mes','dia','nit','proovedoor','cuota','observaciones','estado').order_by('año','mes','dia')
    #cuentas_bancarias = CuentasBancarias.objects.filter(estado = '0').values_list('nit','banco','tipo_cuenta','numero_cuenta','digito_verificacion')
    #df = pd.DataFrame(acuerdos, columns=['año','mes','dia','nit','proovedoor','cuota','observaciones','estado'])
    #df_cuentas = pd.DataFrame(cuentas_bancarias, columns=['nit','banco','tipo_cuenta','numero_cuenta','digito_verificacion'])
    #df = pd.merge(df, df_cuentas, on=['nit','nit'], how='left')
    # Fusionar columnas 'banco', 'tipo_cuenta' y 'numero_cuenta' en una sola columna
    #df['cuenta_bancarias'] = df[['banco', 'tipo_cuenta', 'numero_cuenta']].apply(
    #    lambda x: ' - '.join(x.dropna().astype(str)), axis=1
    #)
    # Agrupar por NIT y concatenar las cuentas
    #df_grouped = df.groupby('nit').agg({
    #    'digito_verificacion': 'first',
    #    'proovedoor': 'first',
    #    'cuota': 'first',
    #    'observaciones': 'first',
    #    'cuenta_bancarias': lambda x: ', '.join(x.dropna().astype(str)),
    #}).reset_index()


    #html_table = df_grouped.to_html(classes='table table-striped', index=False)
    for pago in pagos:
        pago.cuentas_concatenadas = pago.cuentas_concatenadas.replace('|', '<br>') if pago.cuentas_concatenadas else ''
        
    total = sum(pago.valor for pago in pagos.filter(empresa = 'ka')) # type: ignore
    total_pulman = sum(pago.valor for pago in pagos.filter(empresa = 'pulman'))
    total_dyjon = sum(pago.valor for pago in pagos.filter(empresa = 'dyjon'))
    total_acuerdo = sum(pago.valor for pago in pagos.filter(empresa = 'acuerdo'))
    return render(request, 'aprobados.html',{'pagos':pagos, 'total':total,
                                             'total_pulman':total_pulman,
                                             'total_dyjon':total_dyjon,'total_acuerdo':total_acuerdo})
                                            



def exportar_clientes(request):
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('pagos')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['fecha_pago', 'empresa', 'emision', 'vencimiento', 'nit', 'proveedor','descripcion','concepto','descuento','valor','estado_descripcion','cuentas']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
    
    font_style = xlwt.XFStyle()

    fecha = datetime.strptime(request.POST.get('ifecha'), '%Y-%m-%d').date()
    rows = ProgramacionPagosAprobados.objects.filter(fecha_pago = fecha, estado__in=['1','9']).values_list('fecha_pago', 'empresa', 'emision', 'vencimiento', 'nit', 'proveedor','descripcion','concepto','descuento','valor','estado','cuentas_concatenadas').order_by('empresa', 'estado')


    # Procesar los datos y escribir en el archivo
    for row_num, row in enumerate(rows, start=1):
        for col_num, value in enumerate(row):
            if isinstance(value, date):
                formatted_date = value.strftime('%Y-%m-%d')
                ws.write(row_num, col_num, formatted_date, font_style)
            else:
                ws.write(row_num, col_num, value if col_num!=10 else ESTADO.get(value) , font_style) 



    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=pagos_programados.xls'
    # Guardar el contenido del libro de trabajo en un búfer BytesIO
    output = BytesIO()
    wb.save(output)
    
    # Configurar la posición del búfer al principio
    output.seek(0)
    
    # Configurar el contenido del búfer como contenido de la respuesta
    response.write(output.getvalue())
    
    return response

def exportar_acuerdo(request):
    fecha = datetime.strptime(request.POST.get('ifecha'), '%Y-%m-%d').date()
    cuotas = Acuerdos.objects.filter(año = fecha.year,
                                     mes = fecha.month, 
                                    dia = fecha.day , estado = '1').values_list('año','mes','dia','nit','proovedoor','cuota','observaciones','estado').order_by('año','mes','dia')
    cuentas_bancarias = CuentasBancarias.objects.filter(estado = '0').values_list('nit','banco','tipo_cuenta','numero_cuenta','digito_verificacion')
    df = pd.DataFrame(cuotas, columns=['año','mes','dia','nit','proovedoor','cuota','observaciones','estado'])
    df_cuentas = pd.DataFrame(cuentas_bancarias, columns=['nit','banco','tipo_cuenta','numero_cuenta','digito_verificacion'])
    df = pd.merge(df, df_cuentas, on=['nit','nit'], how='left')
    # Fusionar columnas 'banco', 'tipo_cuenta' y 'numero_cuenta' en una sola columna
    df['cuenta_bancarias'] = df[['banco', 'tipo_cuenta', 'numero_cuenta']].apply(
        lambda x: ' - '.join(x.dropna().astype(str)), axis=1
    )
    # Agrupar por NIT y concatenar las cuentas
    df_grouped = df.groupby('nit').agg({
        'cuenta_bancarias': lambda x: ', '.join(x.dropna().astype(str)),
        'digito_verificacion': 'first',
        'año': 'first',
        'mes': 'first',
        'dia': 'first',
        'proovedoor': 'first',
        'cuota': 'first',
        'observaciones': 'first',
        'estado': 'first',
    }).reset_index()

    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')
    df_grouped.to_excel(writer, sheet_name='pagos_acuerdo', index=False)
    writer.close()
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=pagos_acuerdo.xlsx'
    output.seek(0)
    response.write(output.getvalue())
    return response

def agregar_cuenta(request):
    if request.method == 'POST':
        if request.user.has_perm('programaciones.add_cuentasbancarias'):
            nit = request.POST.get('nit')
            digito_verificaicon = request.POST.get('digito_verificacion')
            proveedor = request.POST.get('proveedor').upper()
            banco = request.POST.get('banco').upper()
            tipo_cuenta = request.POST.get('tipo_cuenta')
            numero_cuenta = request.POST.get('numero_cuenta')
            cuenta = CuentasBancarias(nit=nit, proveedor=proveedor, banco=banco, tipo_cuenta=tipo_cuenta, numero_cuenta=numero_cuenta, digito_verificacion=digito_verificaicon)
            cuenta.save()
            messages.success(request, 'Cuenta agregada correctamente')
        else:
            messages.warning(request, 'No tiene permisos para agregar cuentas')
    return render(request, 'agregar_cuenta.html')


def cuentas(request):
    if request.method== 'POST':
        buscar = request.POST.get('buscar').upper()
        cuentas = CuentasBancarias.objects.filter(Q(nit=buscar) | Q(proveedor__icontains = buscar))
    else:
        cuentas = CuentasBancarias.objects.all()
    return render(request, 'cuentas.html', {'cuentas':cuentas})

def inactivar_cuenta(request, id):
    if request.user.has_perm('programaciones.add_cuentasbancarias'):
        cuenta = CuentasBancarias.objects.get(id=id)
        cuenta.estado = '1'
        cuenta.save()
        messages.success(request, 'Cuenta inactivada correctamente')
    else:
        messages.warning(request, 'No tiene permisos para inactivar cuentas')
    return redirect('cuentas')


def totales_ano(request):
    month_names = {
    1: 'Enero',
    2: 'Febrero',
    3: 'Marzo',
    4: 'Abril',
    5: 'Mayo',
    6: 'Junio',
    7: 'Julio',
    8: 'Agosto',
    9: 'Septiembre',
    10: 'Octubre',
    11: 'Noviembre',
    12: 'Diciembre',
    }
    cuotas = Acuerdos.objects.all().values('año','mes').annotate(total=Sum('cuota'),
                                                                 pendiente=Sum(Case(When(estado='0', then='cuota'), default=Value(0), output_field=IntegerField()))
                                                                                    ).order_by('año','mes')
    
    i=4
    for cuota in cuotas:
        
        cuota['mes_nombre'] = month_names.get(cuota['mes'])
        cuota['numero_de_cuota'] = i
        i+=1
    total_pendientes = Acuerdos.objects.filter(estado = '0').aggregate(total=Sum('cuota'))
    total_aprobados = Acuerdos.objects.filter(estado = '1').aggregate(total=Sum('cuota'))
    return render(request, 'totales_ano.html', {'cuotas':cuotas, 'total_pendientes':total_pendientes, 'total_aprobados':total_aprobados})

def totales_mes(request, anio , mes):
    cuotas = Acuerdos.objects.filter(año=anio, mes=mes).values('año','mes', 'dia').annotate(
        total=Sum('cuota'),
        pendiente=Sum(Case(When(estado='0', then='cuota'), default=Value(0), output_field=IntegerField())),
        pagado = Sum(Case(When(estado='1', then='cuota'), default=Value(0), output_field=IntegerField()))).order_by('año','mes','dia')
    
    for cuota in cuotas:
        cuota['mes_nombre'] = MESES.get(int(cuota['mes']))
        cuota['dia_nombre'] = get_dia_semana(cuota['año'] , cuota['mes'] , cuota['dia'])
    total_pendientes = Acuerdos.objects.filter(año=anio, mes=mes, estado = '0').aggregate(total=Sum('cuota'))
    total_aprobados = Acuerdos.objects.filter(año=anio, mes=mes, estado = '1').aggregate(total=Sum('cuota'))
    return render(request, 'totales_mes.html', {'cuotas':cuotas, 'total_pendientes':total_pendientes, 'total_aprobados':total_aprobados})

def get_dia_semana(año, mes ,dia):
    fecha = date(año, mes, dia)
    # Establecer la configuración regional a español
    locale.setlocale(locale.LC_TIME, 'es_ES')

    # Obtener el nombre del día de la semana en español
    nombre_dia = fecha.strftime("%A")
    nombre_dia = nombre_dia.upper()
    #print(nombre_dia)

    # Restablecer la configuración regional a la predeterminada
    locale.setlocale(locale.LC_TIME, '')

    return nombre_dia

def detalle_acuerdo(request, anio , mes, dia):
    cuotas = Acuerdos.objects.filter(año=anio, mes=mes, dia=dia).order_by('estado','año','mes','dia')
    for cuota in cuotas:
        cuota.nombre_dia = get_dia_semana(cuota.año , cuota.mes , cuota.dia)
    return render(request, 'detalle_acuerdo.html', {'cuotas':cuotas})

def aprobar_acuerdo(request, id):
    if request.user.has_perm('programaciones.aprobar_pago'):
        cuota = Acuerdos.objects.get(id=id)
        acuerdos = Acuerdos.objects.filter(año=cuota.año, mes=cuota.mes, dia=cuota.dia)
        if len(acuerdos) > 0:
            acuerdos.update(estado='1')
            messages.success(request, 'Cuota aprobada correctamente')
        else:
            messages.warning(request, 'Error al aprobar cuotas')
        return redirect('detalle_acuerdo', cuota.año, cuota.mes, cuota.dia)
    else:
        messages.warning(request, 'No tiene permisos para aprobar cuotas')
        return redirect('totales_mes')
    
def aprobar_unico(request, id):
    if request.user.has_perm('programaciones.aprobar_pago'):
        cuota = Acuerdos.objects.get(id=id)
        cuota.estado = '1'
        cuota.save()
        messages.success(request, 'Cuota aprobada correctamente')
        return redirect('detalle_acuerdo', cuota.año, cuota.mes, cuota.dia)
    else:
        messages.warning(request, 'No tiene permisos para aprobar cuotas')
        return redirect('totales_mes')
    
def rechazar_acuerdo(request, id):
    if request.user.has_perm('programaciones.aprobar_pago'):
        
        cuota = Acuerdos.objects.get(id=id)
        dia_consulta = cuota.dia
        cuota.dia = Acuerdos.objects.filter(año=cuota.año, mes=cuota.mes).order_by('-dia').first().dia
        cuota.save()
        messages.success(request, 'Cuota rechazada correctamente, se paso para el ultimo dia')
        return redirect('detalle_acuerdo', cuota.año, cuota.mes, dia_consulta)
    else:
        messages.warning(request, 'No tiene permisos para aprobar cuotas')
        return redirect('totales_mes')
    
def pendientes_acuerdo(request):
    mes = date.today().month
    año = date.today().year
    dia = date.today().day
    acuerdos = Acuerdos.objects.filter(año=año, mes=mes, estado='0').order_by('dia','-cuota')
    if request.method == 'POST':
        ultimo_dia_acuerdos = Acuerdos.objects.filter(año=año, mes=mes).order_by('-dia').first()
        acuerdos_aprobados = Acuerdos.objects.filter(año=año, mes=mes, dia = dia ,estado='1')
        acuerdos_pendientes = Acuerdos.objects.filter(año=año, mes=mes, dia = dia ,estado='0')
        if len(acuerdos_aprobados) > 0 and len(acuerdos_pendientes) == 0:
            messages.warning(request, 'Ya existen cuotas aprobadas para este dia no se puede modificar')
            return render(request, 'pendientes_acuerdo.html', {'acuerdos':acuerdos})

        print(ultimo_dia_acuerdos.dia)
        Acuerdos.objects.filter(año=año, mes=mes, dia= dia, estado ='0').update(dia = ultimo_dia_acuerdos.dia)
        lista = request.POST.get('selected_items').split(',')
        Acuerdos.objects.filter(id__in=lista).update(dia = dia)
        return redirect('detalle_acuerdo', año, mes, dia)
    return render(request, 'pendientes_acuerdo.html', {'acuerdos':acuerdos})
    