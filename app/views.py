from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

from .models import Caso, Evidencia, Prefetch, Registro
from .forms import CrearCasoForm, CargarEvidenciaForm

from django.forms.models import inlineformset_factory

from django.core.files.storage import default_storage

from datetime import datetime
from app.tickets import crear_ticket, anadir_respuesta

from app.tasks import procesar_evidencia, reprocesar_registro, reprocesar_prefetch
from app.utils import descargar, descargarCSV

class Home(LoginRequiredMixin, ListView):
    template_name = 'app/home.html'
    model = Caso

    def get_queryset(self):
        qs = super(Home, self).get_queryset()
        return qs.filter(usuario_creador=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(Home, self).get_context_data(**kwargs)
        #context['crear_caso_flag'] = 1 if self.request.user.cliente.max_casos > len(context['caso_list']) else 0
        context['evidencia_list'] = dict([(caso.id, Evidencia.objects.filter(caso=caso)) for caso in context['caso_list']])
        return context

class CrearCaso(LoginRequiredMixin, View):
    template = 'app/caso_form.html'
    success_url = reverse_lazy('skyev:home')

    def get(self, request):
        form = CrearCasoForm()
        ctx = {'form': form}
        return render(request, self.template, ctx)

    def post(self, request):
        print(request.POST)
        form = CrearCasoForm(request.POST, request.FILES or None)

        if not form.is_valid():
            ctx = {'form': form }
            return render(request, self.template, ctx)

        caso = form.save(commit=False)
        caso.usuario_creador = request.user

        # Request a sistema tickets
        caso.ticket_id = 1 #crear_ticket(caso)
        caso.save()

        return redirect(self.success_url)

class CargarEvidencia(LoginRequiredMixin, View):
    template = 'app/evidencia_form.html'
    success_url = reverse_lazy('skyev:home')

    def get(self, request, ticket_id):
        form = CargarEvidenciaForm()
        ctx = {'form': form, 'ticket_id': ticket_id }
        return render(request, self.template, ctx)

    def post(self, request, ticket_id):
        # Validar request y archivos adjuntos
        form = CargarEvidenciaForm(request.POST, request.FILES or None)

        if not form.is_valid():
            ctx = {'form': form }
            return  redirect(self.success_url)

        # Inicializar arreglo de archivos de evidencia
        evidencias = []
        # Obtener caso asociado al ticket
        caso = get_object_or_404(Caso, ticket_id=ticket_id)

        # Obtener valor inicial consecutivo de evidencia
        if Evidencia.objects.filter(caso=caso).exists():
            ini_evidencia = Evidencia.objects.filter(caso=caso).latest('evidencia_num').evidencia_num  + 1
        else:
            ini_evidencia = 1

        for num, file in enumerate(request.FILES.getlist('evidencia_file'), start=ini_evidencia):
            # Crear evidencia asignando consecutivo
            ev = Evidencia(caso=caso, fecha_cargue=datetime.today().strftime('%Y-%m-%d'), evidencia_num=num)
            ev.save()

            # Asignar un nombre al archivo y asociarlo al registro de Evidencia
            nombre = str(caso.ticket_id) + '-' + str(ev.evidencia_num)
            file.name = nombre + '.zip'
            ev.archivo=file
            ev.save()

            evidencias.append(ev)
            procesar_evidencia.delay(file.name, nombre)

        # { Enviar evidencias a sistema tickets }
        # anadir_respuesta(caso, evidencias)

        return redirect(self.success_url)

class ReprocesarRegistro(LoginRequiredMixin, View):

    success_url = reverse_lazy('skyev:home')

    def get(self, request, ticket_id, ev_num):
        nombre = str(ticket_id) + '-' + str(ev_num)
        reprocesar_registro.delay(nombre)
        return redirect(self.success_url)

class ReprocesarPrefetch(LoginRequiredMixin, View):

    success_url = reverse_lazy('skyev:home')

    def get(self, request, ticket_id, ev_num):
        nombre = str(ticket_id) + '-' + str(ev_num)
        reprocesar_prefetch.delay(nombre)
        return redirect(self.success_url)

class DetallePrefetch(LoginRequiredMixin, ListView):
    template_name = 'app/detalle_prefetch.html'
    model = Prefetch

    def get(self, request, ticket_id, ev_num):
        caso = Caso.objects.get(ticket_id=ticket_id)
        evidencia = Evidencia.objects.get(caso=caso, evidencia_num=ev_num)
        prefetch_list = Prefetch.objects.filter(evidencia=evidencia) # TODO Optimizar
        context = { 'prefetch_list': prefetch_list , 'evidencia': evidencia}
        return render(request, self.template_name, context)

class DetalleRegistro(LoginRequiredMixin, ListView):
    template_name = 'app/detalle_registro.html'
    model = Registro

    def get(self, request, ticket_id, ev_num):
        caso = Caso.objects.get(ticket_id=ticket_id)
        evidencia = Evidencia.objects.get(caso=caso, evidencia_num=ev_num)
        registro_list = Registro.objects.filter(evidencia=evidencia, usuario_pc__isnull=True)  # TODO Optimizar

        ntuser_list = Registro.objects.filter(evidencia=evidencia, usuario_pc__isnull=False)
        ntuser_dict = dict()

        for entry in ntuser_list:
            if entry.usuario_pc not in ntuser_dict:
                ntuser_dict[entry.usuario_pc] = []
            ntuser_dict[entry.usuario_pc].append(entry)

        print(ntuser_dict)

        for key in ntuser_dict:
            print("Key:", key)
            print("Value:", ntuser_dict[key])


        context = { 'registro_list': registro_list, 'ntuser_dict': ntuser_dict, 'evidencia': evidencia}
        return render(request, self.template_name, context)

class DescargarEjecutable(LoginRequiredMixin, View):

    def get(self, request):
        path = 'extraccion.zip'
        return descargar(path)

class DescargarEvidencia(LoginRequiredMixin, View):

    def get(self, request, ticket_id, ev_num):
        path = get_object_or_404(Evidencia, caso=ticket_id, evidencia_num=ev_num).archivo
        return descargar(str(path))

class DescargarPrefetch(LoginRequiredMixin, View):

    def get(self, request, ticket_id, ev_num):
        caso = Caso.objects.get(ticket_id=ticket_id)
        evidencia = Evidencia.objects.get(caso=caso, evidencia_num=ev_num)
        prefetch_list = Prefetch.objects.filter(evidencia=evidencia) # TODO Optimizar
        header = 'last_run_time;exe_file;pf_hash;pf_run_count;pf_file;pf_version;volume_count;volume_timestamp;volume_dev_path;volume_serial_number'
        return descargarCSV(header, prefetch_list, str(evidencia) + "_Prefetch")

class DescargarRegistro(LoginRequiredMixin, View):

    def get(self, request, ticket_id, ev_num):
        caso = Caso.objects.get(ticket_id=ticket_id)
        evidencia = Evidencia.objects.get(caso=caso, evidencia_num=ev_num)
        registro_list = Registro.objects.filter(evidencia=evidencia)  # TODO Optimizar
        header = 'Descripción;Llave;Valor;Usuario'
        return descargarCSV(header, registro_list, str(evidencia) + "_Registro")
