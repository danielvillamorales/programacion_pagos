from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import datetime, date
import openpyxl
from .models import Pagos
import xlwt
from django.http import HttpResponse
from io import BytesIO
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.db.models import Q

# Create your views here.
ESTADO = {'0':'Pendiente', '1':'Aprobado Jefe', '9':'Rechazado'}
EMPRESAS_PERMITIDAS = ["ka", "pendientes", "dyjon", "pulman"]

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
    pagos = Pagos.objects.filter(fecha_pago = date.today(), empresa = 'ka').order_by('estado','-valor')
    pagos_dyjon = Pagos.objects.filter(fecha_pago = date.today(), empresa = 'dyjon').order_by('estado','-valor')
    pagos_pulman = Pagos.objects.filter(fecha_pago = date.today(), empresa = 'pulman').order_by('estado','-valor')
    total = sum(pago.valor for pago in pagos)
    total_dyjon = sum(pago.valor for pago in pagos_dyjon)
    total_pulman = sum(pago.valor for pago in pagos_pulman)
    return render(request, 'consulta.html', {'pagos':pagos, 'total':total, 'pagos_dyjon':pagos_dyjon, 'total_dyjon':total_dyjon, 'pagos_pulman':pagos_pulman, 'total_pulman':total_pulman })


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
    return render(request, 'consulta.html', {'pagos':pagos, 'total':total})

def borrar_pendientes(request):
    if request.user.has_perm('programaciones.subir_excel'):
        Pagos.objects.filter(fecha_pago = date.today(), estado = '0').delete()
        messages.success(request, 'Pagos pendientes borrados correctamente')
    else:
        messages.warning(request, 'No tiene permisos para borrar pagos pendientes')
    return redirect('importar')

def historico(request):
    if request.method == 'POST':
        return exportar_clientes(request)
    return render(request, 'historico.html')


def pagos_aprobados(request):
    pagos = Pagos.objects.filter(fecha_pago = date.today(), 
                                 empresa = 'ka',
                                 estado = '1').order_by('empresa', '-valor')
    pagos_pulman = Pagos.objects.filter(fecha_pago = date.today(), 
                                 empresa = 'pulman',
                                 estado = '1').order_by('empresa', '-valor')
    pagos_dyjon = Pagos.objects.filter(fecha_pago = date.today(), 
                                 empresa = 'dyjon',
                                 estado = '1').order_by('empresa', '-valor')

    if request.method == 'POST':
        fecha = datetime.strptime(request.POST.get('ifecha'), '%Y-%m-%d').date()
        pagos = Pagos.objects.filter(fecha_pago = fecha, 
                                 empresa = 'ka',
                                 estado = '1').order_by('empresa', '-valor')
        pagos_pulman = Pagos.objects.filter(fecha_pago = fecha, 
                                 empresa = 'pulman',
                                 estado = '1').order_by('empresa', '-valor')
        pagos_dyjon = Pagos.objects.filter(fecha_pago = fecha, 
                                 empresa = 'dyjon',
                                 estado = '1').order_by('empresa', '-valor')
    total = sum(pago.valor for pago in pagos)
    total_pulman = sum(pago.valor for pago in pagos_pulman)
    total_dyjon = sum(pago.valor for pago in pagos_dyjon)
    return render(request, 'aprobados.html',{'pagos':pagos, 'total':total, 'pagos_pulman':pagos_pulman, 
                                             'total_pulman':total_pulman, 'pagos_dyjon':pagos_dyjon, 
                                             'total_dyjon':total_dyjon})


def exportar_clientes(request):
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('pagos')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['fecha_pago', 'empresa', 'emision', 'vencimiento', 'nit', 'proveedor','descripcion','concepto','descuento','valor','estado_descripcion']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
    
    font_style = xlwt.XFStyle()

    fecha = datetime.strptime(request.POST.get('ifecha'), '%Y-%m-%d').date()
    rows = Pagos.objects.filter(fecha_pago = fecha, estado__in=['1','9']).values_list('fecha_pago', 'empresa', 'emision', 'vencimiento', 'nit', 'proveedor','descripcion','concepto','descuento','valor','estado').order_by('empresa', 'estado')


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