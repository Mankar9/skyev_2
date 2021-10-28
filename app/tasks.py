from celery import Celery

import app.prefetch
import os

from .models import Caso, Evidencia, Prefetch, Registro, LlaveRegistro, SubllaveRegistro, ArchivoRegistro, EstadoEvidencia
from django.shortcuts import get_object_or_404

app = Celery('tasks', broker='pyamqp://guest@localhost//')

@app.task
def procesar_evidencia(zip, name):

    print("Procesando: " + name )
    unzip(zip, name) # Descomprimir empaquetado cargado
    descifrar(name) # Descifrar contenido del archivo
    unzip(name + '/descifrada.zip', name + '/' + name) # Descomprimir evidencia descifrada

    caso = name.split('-')[0]
    ev_num = name.split('-')[1]
    ev = get_object_or_404(Evidencia, caso__ticket_id=caso, evidencia_num = ev_num)

    # Procesar evidencia
    procesar_prefetch(ev, name)
    procesar_registro(ev, name)

    if not ev.estado.nombre == 'Fallido':
        ev.estado = get_object_or_404(EstadoEvidencia, nombre='Finalizado')
        ev.save()

import zipfile

# Descomprimir archivo de evidencia
def unzip(zip, unzipped):
    with zipfile.ZipFile('evidencia/' + zip, 'r') as zip_ref:
        zip_ref.extractall('evidencia/' +unzipped)

from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_v1_5
from Crypto.Util.Padding import unpad
from Crypto import Random
import struct, os

# Descifrar evidencia
def descifrar(file):

    f = open('private.key','r')
    rsa_key = RSA.import_key(f.read())
    with open('evidencia/' + file + '/init') as f:
        keys = f.readlines()

    sentinel = Random.new().read(256)

    # Descifrar con RSA parámetros de cifrado simétrico
    cipher_rsa = PKCS1_v1_5.new(rsa_key)
    aes_key = cipher_rsa.decrypt(bytearray.fromhex(keys[0]), sentinel)
    aes_iv = cipher_rsa.decrypt(bytearray.fromhex(keys[1]), sentinel)

    chunksize=24*1024

    # https://eli.thegreenplace.net/2010/06/25/aes-encryption-of-files-in-python-with-pycrypto
    # https://pycryptodome.readthedocs.io/en/latest/src/util/util.html
    with open('evidencia/' + file + '/evidencia.zip', 'rb') as infile:

        cipher_aes = AES.new(aes_key, AES.MODE_CBC, aes_iv)

        # Descifrar con AES archivo evidencia.zip y generar archivo descifrada.zip
        with open('evidencia/' + file + '/descifrada.zip', 'wb') as outfile:
            while True:
                chunk = infile.read(chunksize)
                if len(chunk) < chunksize:
                    outfile.write(unpad(cipher_aes.decrypt(chunk), 16))
                    break
                outfile.write(cipher_aes.decrypt(chunk))

def procesar_prefetch(ev, name):
    count = 0
    field_num = 0

    try:

        # Ejecutar script prefetch
        prefetch_path = "evidencia" + os.sep + name + os.sep + name + os.sep + "Prefetch"
        os.system("py app/prefetch.py " + prefetch_path + " -o " + prefetch_path)

        ev.estado = get_object_or_404(EstadoEvidencia, nombre='Procesando Prefetch')
        ev.save()

        with open('evidencia/' + name + '/' + name + '/' + 'Prefetch_run_count.csv', 'r') as infile:

            line = infile.readline() # Encabezado (se descarta)

            field_num = len(line.strip().split(","))

            while True:

                line = infile.readline() # Leer cada línea del archivo .csv

                if not line:
                    break

                if len(line.strip()) == 0:
                    continue

                fields = line.strip().split(",")

                if len(fields) < field_num:
                    for i in range(len(fields), field_num):
                        fields.append(None)

                # Convertir la línea en objeto Prefetch y guardar en base de datos
                prefetch = Prefetch(evidencia=ev)

                prefetch.last_run_time = fields[0]
                prefetch.exe_file = fields[1]
                prefetch.pf_hash = fields[2]
                prefetch.pf_run_count = fields[3]
                prefetch.pf_file = fields[4]
                prefetch.pf_version = fields[5]
                prefetch.volume_count = fields[6]
                prefetch.volume_timestamp = fields[7]
                prefetch.volume_dev_path = fields[8]
                prefetch.volume_serial_number = fields[9]

                prefetch.save()
    except:

        ev.estado = get_object_or_404(EstadoEvidencia, nombre='Fallido')
        ev.save()

from Registry import Registry

def procesar_registro(ev, name):

    try:
        ev.estado = get_object_or_404(EstadoEvidencia, nombre='Procesando Registro')
        ev.save()

        archivos = ArchivoRegistro.objects.all()

        hive_dir = 'evidencia/' + name + '/' + name + '/Registry/Hive/'

        print(hive_dir)

        for archivo in archivos:

            print (archivo)

            if archivo.nombre == "NTUSER.DAT":

                usuarios = [d for d in os.listdir(hive_dir) if os.path.isdir(os.path.join(hive_dir, d))]

                for usuario in usuarios:
                    path_archivo = 'evidencia/' + name + '/' + name + '/Registry/Hive/' + usuario + '/' + archivo.nombre
                    guardarLlavesArchivo(ev, archivo, path_archivo, usuario)

            else:
                path_archivo = 'evidencia/' + name + '/' + name + '/Registry/Hive/' + archivo.nombre
                guardarLlavesArchivo(ev, archivo, path_archivo)
    except Exception as e:
        print(e)
        ev.estado = get_object_or_404(EstadoEvidencia, nombre='Fallido')
        ev.save()


def guardarLlavesArchivo(ev, archivo, path_archivo, usuario=None):

    print(archivo)

    if not os.path.isfile(path_archivo):
        return

    print(1)

    reg = Registry.Registry(path_archivo)
    llaves = LlaveRegistro.objects.filter(archivo=archivo)

    for llave in llaves:

        try:
            key = reg.open(llave.key)
        except Registry.RegistryKeyNotFoundException:
            print ("Couldn't find Run key. Exiting...")
            continue

        subllaves = SubllaveRegistro.objects.filter(key=llave)

        for subllave in subllaves:

            if subllave.llave_padre_aleatoria:

                valor = []

                for sk in key.subkeys():

                    for value in [v for v in sk.values() if v.name() == subllave.nombre]:

                        if llave.nombres and llave.datos:
                            valor.append(sk.name() + "\\" + value.name() + " = " + str(value.value()))
                        elif llave.nombres:
                            valor.append(sk.name() + "\\" + value.name())
                        elif llave.datos:
                            valor.append(sk.name() + "\\" + str(value.value()))

                valor = (', ').join(valor)

                registro = Registro(evidencia=ev, key=subllave, valor=valor, usuario_pc=usuario)
                registro.save()

            elif not subllave.nombre: # No está registrada una subllave específica; se quiere obtener todos los valores

                valor = []

                if llave.nombre_subllaves:

                    for nombre in key.subkeys():
                        valor.append(nombre.name())

                else:

                    for value in key.values():
                        if llave.nombres and llave.datos:
                            valor.append(value.name() + " = " + str(value.value()))
                        elif llave.nombres:
                            valor.append(value.name())
                        elif llave.datos:
                            valor.append(str(value.value()))

                valor = (', ').join(valor)

                registro = Registro(evidencia=ev, key=subllave, valor=valor, usuario_pc=usuario)
                registro.save()

            else:

                for value in [v for v in key.values() if v.name() == subllave.nombre]:
                    registro = Registro(evidencia=ev, key=subllave, valor=value.value(), usuario_pc=usuario)
                    registro.save()

# https://superuser.com/questions/1572038/ms-regedit-hex-to-date-conversion
def parseHexDate(value):
    n=list(value)
    l1=[]
    l2=[]
    for i in range(0,len(n),2):
        l1.append(n[i])
    for j in range(1,len(n),2):
        l2.append(n[j])

    fecha = ''

    l3=[str (x) + str (y) for x, y in zip (l2, l1)]
    print("Date (YYYY/MM/DD): ")
    for i in range(len(l3)):
        if i!=2 and i<4:
            res = int(l3[i], 16)
            fecha += str(res)

    return fecha

@app.task
def reprocesar_registro(name):

    caso, separator, ev_num = name.partition('-')
    ev = get_object_or_404(Evidencia, caso__ticket_id=caso, evidencia_num = ev_num)

    Registro.objects.filter(evidencia=ev).delete()

    procesar_registro(ev, name)

    ev.refresh_from_db()

    if not ev.estado.nombre == 'Fallido':
        ev.estado = get_object_or_404(EstadoEvidencia, nombre='Finalizado')
        ev.save()

@app.task
def reprocesar_prefetch(name):

    caso, separator, ev_num = name.partition('-')
    ev = get_object_or_404(Evidencia, caso__ticket_id=caso, evidencia_num = ev_num)

    Prefetch.objects.filter(evidencia=ev).delete()

    procesar_prefetch(ev, name)

    ev.refresh_from_db()

    if not ev.estado.nombre == 'Fallido':
        ev.estado = get_object_or_404(EstadoEvidencia, nombre='Finalizado')
        ev.save()
