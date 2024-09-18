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
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from programaciones.views import (
    agregar_cuenta,
    aprobar,
    aprobar_acuerdo,
    aprobar_todo,
    aprobar_unico,
    borrar_pendientes,
    busqueda,
    consulta,
    cuentas,
    detalle_acuerdo,
    historico,
    importar,
    inactivar_cuenta,
    pagos_aprobados,
    pendientes,
    pendientes_acuerdo,
    pendientes_next,
    rechazar,
    rechazar_acuerdo,
    totales_ano,
    totales_mes,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "accounts/login/", LoginView.as_view(template_name="login.html"), name="login"
    ),
    path("", LoginView.as_view(template_name="login.html"), name="login"),
    path(
        "accounts/logout/",
        LogoutView.as_view(template_name="logout.html"),
        name="logout",
    ),
    path("importar/", importar, name="importar"),
    path("consulta/", consulta, name="consulta"),
    path("aprobar/<int:id>", aprobar, name="aprobar"),
    path("rechazar/<int:id>", rechazar, name="rechazar"),
    path("aprobar_todo/", aprobar_todo, name="aprobar_todo"),
    path("pendientes/", pendientes, name="pendientes"),
    path("borrar_pendientes/", borrar_pendientes, name="borrar_pendientes"),
    path("historico/", historico, name="historico"),
    path("pagos_aprobados/", pagos_aprobados, name="pagos_aprobados"),
    path("pendientes_next", pendientes_next, name="pendientes_next"),
    path("agregar_cuenta", agregar_cuenta, name="agregar_cuenta"),
    path("cuentas", cuentas, name="cuentas"),
    path("inactivar_cuenta/<int:id>", inactivar_cuenta, name="inactivar_cuenta"),
    path("totales_ano/", totales_ano, name="totales_ano"),
    path("totales_mes/<int:anio>/<int:mes>/", totales_mes, name="totales_mes"),
    path(
        "detalle_acuerdo/<int:anio>/<int:mes>/<int:dia>",
        detalle_acuerdo,
        name="detalle_acuerdo",
    ),
    path("aprobar_acuerdo/<int:id>", aprobar_acuerdo, name="aprobar_acuerdo"),
    path("pendientes_acuerdo/", pendientes_acuerdo, name="pendientes_acuerdo"),
    path("aprobar_unico/<int:id>", aprobar_unico, name="aprobar_unico"),
    path("rechazar_acuerdo/<int:id>", rechazar_acuerdo, name="rechazar_acuerdo"),
    path("busqueda/", busqueda, name="busqueda"),
]
