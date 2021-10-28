from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

from .managers import CustomUserManager
from django.utils.translation import ugettext_lazy as _

class Cliente(models.Model):
    nombre_empresa = models.CharField(max_length=100, blank=True, null=True)
    max_casos = models.IntegerField()

    def __str__(self):
        return self.nombre_empresa

class Usuario(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)
    empresa = models.ForeignKey(Cliente, on_delete=models.CASCADE, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

class EstadoCaso(models.Model):
    nombre = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return self.nombre

class Caso(models.Model):
    usuario_creador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=50, blank=True, null=True)
    descripcion = models.CharField(max_length=200, blank=True, null=True)
    estado = models.ForeignKey(EstadoCaso, on_delete=models.CASCADE, default=1)
    fecha_creacion = models.DateField(blank=True, null=True)
    fecha_actualizacion = models.DateField(blank=True, null=True)
    ruta_consolidado = models.CharField(max_length=100,blank=True, null=True)
    fecha_consolidado = models.DateField(blank=True, null=True)
    ticket_id = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return '[' + str(self.ticket_id) + '] - ' + self.titulo

class EstadoEvidencia(models.Model):
    nombre = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.nombre

class Evidencia(models.Model):
    caso = models.ForeignKey(Caso, on_delete=models.CASCADE)
    evidencia_num = models.IntegerField()
    estado = models.ForeignKey(EstadoEvidencia, on_delete=models.CASCADE, default=1)
    revisada = models.BooleanField(default=False)
    fecha_cargue = models.DateField(blank=True, null=True)
    fecha_revision = models.DateField(blank=True, null=True)
    analisis_detallado = models.BooleanField(default=False)
    registro_finalizado = models.BooleanField(default=False)
    archivo = models.FileField(upload_to='evidencia', blank=True, null=True)

    class Meta:
        unique_together = (("caso", "evidencia_num"),)

    def __str__(self):
        return str(self.caso.ticket_id) + "-" + str(self.evidencia_num)

class ArchivoRegistro(models.Model):
    nombre = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.nombre

class LlaveRegistro(models.Model):
    key = models.CharField(max_length=200, blank=True, null=True)
    archivo = models.ForeignKey(ArchivoRegistro, on_delete=models.CASCADE, null=True)
    nombre_subllaves = models.BooleanField(default=False) # Guardar los nombres de las subllaves
    nombres = models.BooleanField(default=False) # Guardar nombres de valores
    datos = models.BooleanField(default=True) # Guardar nombres y datos de valores

    def __str__(self):
        return str(self.archivo.nombre) + "\\" + str(self.key)

class SubllaveRegistro(models.Model):
    nombre = models.CharField(max_length=200, blank=True, null=False)
    key = models.ForeignKey(LlaveRegistro, on_delete=models.CASCADE, null=True)
    descripcion = models.CharField(max_length=200, blank=True, null=True)
    llave_padre_aleatoria = models.BooleanField(default=False)

    def __str__(self):
        if self.key == None:
            return self.descripcion
        else:
            return str(self.key) + "\\" + self.nombre

class Registro(models.Model):
    evidencia = models.ForeignKey(Evidencia, on_delete=models.CASCADE)
    key = models.ForeignKey(SubllaveRegistro, on_delete=models.CASCADE, null=True)
    valor = models.CharField(max_length=100, blank=True, null=True)
    usuario_pc = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return str(self.evidencia) + "-" + self.key.descripcion

    def toCsvFormat(self):
        fields = [self.key.descripcion, self.key, self.valor, self.usuario_pc]
        return ';'.join(str(field or '') for field in fields)

class Prefetch(models.Model):
    evidencia = models.ForeignKey(Evidencia, on_delete=models.CASCADE)
    last_run_time = models.CharField(max_length=100, blank=True, null=True)
    exe_file = models.CharField(max_length=100, blank=True, null=True)
    pf_hash = models.CharField(max_length=100, blank=True, null=True)
    pf_run_count = models.CharField(max_length=100, blank=True, null=True)
    pf_file = models.CharField(max_length=100, blank=True, null=True)
    pf_version = models.CharField(max_length=100, blank=True, null=True)
    volume_count = models.CharField(max_length=100, blank=True, null=True)
    volume_timestamp = models.CharField(max_length=100, blank=True, null=True)
    volume_dev_path = models.CharField(max_length=100, blank=True, null=True)
    volume_serial_number = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.exe_file

    def toCsvFormat(self):
        fields = [self.last_run_time, self.exe_file, self.pf_hash,
            self.pf_run_count, self.pf_file, self.pf_version, self.volume_count,
            self.volume_timestamp, self.volume_dev_path, self.volume_serial_number,
            ]
        return ';'.join(str(field or '') for field in fields)


class EstadoInforme(models.Model):
    nombre = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.nombre

class InformeConsolidado(models.Model):
    caso = models.ForeignKey(Caso, on_delete=models.CASCADE)
    estado = models.ForeignKey(EstadoInforme, on_delete=models.CASCADE)
    ruta = models.CharField(max_length=100, blank=True, null=True)
    fecha_cargue = models.DateField(blank=True, null=True)

class InformeDetallado(models.Model):
    evidencia = models.ForeignKey(Evidencia, on_delete=models.CASCADE)
    estado = models.ForeignKey(EstadoInforme, on_delete=models.CASCADE)
    ruta = models.CharField(max_length=100, blank=True, null=True)
    fecha_cargue = models.DateField(blank=True, null=True)
