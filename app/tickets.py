import requests



def crear_ticket(caso):
    https_proxy = "http://connect.virtual.uniandes.edu.co:443"

    proxyDict = { "http" : https_proxy }

    url = "http://172.24.98.216/uvdesk/public/api/v1/ticket"
    headers = { 'Authorization' : 'Basic TO4EAJQFURNJZZCHHLJEC0BBPLT7VFSGGDB2PNEWRG8N4UWBWXU4DNGPXAR0FLS8'}

    user = caso.usuario_creador

    myobj = {
        "name": user.first_name + " " + user.last_name,
        "type": "2",
        "from": user.email,
        "subject": caso.titulo,
        "message": obtenerMensaje(caso),
        "actAsType": "customer",
    }

    r = requests.post(url, headers=headers, proxies=proxyDict, data = myobj)
    json_resp = r.json()
    print(json_resp)
    return json_resp['ticketId']

def anadir_respuesta(caso, archivos=None):
    https_proxy = "http://connect.virtual.uniandes.edu.co:443"

    proxyDict = { "http" : https_proxy }

    url = "http://172.24.98.216/uvdesk/public/api/v1/ticket/" + str(caso.ticket_id) + "/thread"
    headers = { 'Authorization' : 'Basic TO4EAJQFURNJZZCHHLJEC0BBPLT7VFSGGDB2PNEWRG8N4UWBWXU4DNGPXAR0FLS8'}

    user = caso.usuario_creador

    myobj = {
        "message": obtenerRespuesta(caso, archivos),
        "actAsType": "customer",
        "actAsEmail": "mankar91@gmail.com",
        "threadType": "reply"
    }

    r = requests.post(url, headers=headers, proxies=proxyDict, data = myobj)
    json_resp = r.json()
    print(json_resp)
    #return json_resp['ticketId']

def obtenerMensaje(caso):
    mensaje = "Se ha solicitado un nuevo caso desde la aplicación.\nTítulo: " + caso.titulo + "\nDescripción: " + caso.descripcion + "\n"
    return mensaje

def obtenerRespuesta(caso, evidencias):
    mensaje = "Se ha añadido nueva evidencia al caso desde la aplicación."
    for ev in evidencias:
        mensaje += "\nEvidencia: <a href='http://127.0.0.1:8000/descargar_evidencia/" + str(ev.id) +"'>" + str(ev) + "</a>"
    return mensaje
