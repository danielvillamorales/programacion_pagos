"""programacion_pagos URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LoginView,LogoutView
from programaciones.views import importar, consulta, aprobar, rechazar, aprobar_todo, pendientes, borrar_pendientes, historico, pagos_aprobados,pendientes_next,agregar_cuenta,inactivar_cuenta,cuentas

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/',LoginView.as_view(template_name='login.html'),name="login"),
    path('',LoginView.as_view(template_name='login.html'),name="login"),
    path('accounts/logout/',LogoutView.as_view(template_name='logout.html'),name="logout"),
    path('importar/',importar,name="importar"),
    path('consulta/',consulta,name="consulta"),
    path('aprobar/<int:id>',aprobar,name="aprobar"),
    path('rechazar/<int:id>',rechazar,name="rechazar"),
    path('aprobar_todo/',aprobar_todo,name="aprobar_todo"),
    path('pendientes/',pendientes,name="pendientes"),
    path('borrar_pendientes/',borrar_pendientes,name="borrar_pendientes"),
    path('historico/',historico,name="historico"),
    path('pagos_aprobados/',pagos_aprobados,name="pagos_aprobados"),
    path('pendientes_next', pendientes_next, name="pendientes_next"),
    path('agregar_cuenta', agregar_cuenta, name="agregar_cuenta"),
    path('cuentas', cuentas, name="cuentas"),
    path('inactivar_cuenta/<int:id>', inactivar_cuenta, name="inactivar_cuenta"),
]
