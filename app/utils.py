def naturalsize(count):
    fcount = float(count)
    k = 1024
    m = k * k
    g = m * k
    if fcount < k:
        return str(count) + 'B'
    if fcount >= k and fcount < m:
        return str(int(fcount / (k/10.0)) / 10.0) + 'KB'
    if fcount >= m and fcount < g:
        return str(int(fcount / (m/10.0)) / 10.0) + 'MB'
    return str(int(fcount / (g/10.0)) / 10.0) + 'GB'

import os
from django.conf import settings
from django.http import HttpResponse, Http404

def descargar(path):
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.microsoft.portable-executable ")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404

from .models import Prefetch
import csv

def descargarCSV(header, objects, filename):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s.csv' % filename
    response.write(u'\ufeff'.encode('utf8'))

    writer = csv.writer(response, delimiter = ";")
    writer.writerow([header])
    for obj in objects:
        writer.writerow([obj.toCsvFormat()])
    return response
