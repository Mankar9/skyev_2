from django.urls import path

from . import views

app_name = 'skyev'

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('crear_caso', views.CrearCaso.as_view(), name='crear_caso'),

    path('caso/<int:ticket_id>/cargar_evidencia/', views.CargarEvidencia.as_view(), name='cargar_evidencia'),
    path('caso/<int:ticket_id>/prefetch/<int:ev_num>', views.DetallePrefetch.as_view(), name='detalle_prefetch'),
    path('caso/<int:ticket_id>/registro/<int:ev_num>', views.DetalleRegistro.as_view(), name='detalle_registro'),

    path('descargar_ejecutable', views.DescargarEjecutable.as_view(), name='descargar_ejecutable'),
    path('caso/<int:ticket_id>/descargar_evidencia/<int:ev_num>', views.DescargarEvidencia.as_view(), name='descargar_evidencia'),

    path('caso/<int:ticket_id>/descargar_prefetch/<int:ev_num>/', views.DescargarPrefetch.as_view(), name='descargar_prefetch'),
    path('caso/<int:ticket_id>/descargar_registro/<int:ev_num>/', views.DescargarRegistro.as_view(), name='descargar_registro'),

    path('caso/<int:ticket_id>/reprocesar_registro/<int:ev_num>/', views.ReprocesarRegistro.as_view(), name='reprocesar_registro'),
    path('caso/<int:ticket_id>/reprocesar_prefetch/<int:ev_num>/', views.ReprocesarPrefetch.as_view(), name='reprocesar_prefetch'),
]
