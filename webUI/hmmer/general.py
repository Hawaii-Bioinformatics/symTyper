from celery.result import AsyncResult
from django.core.urlresolvers import reverse
from django.utils.encoding import smart_str
from django.http import HttpResponse, HttpResponseRedirect
from django.core.servers.basehttp import FileWrapper
import urllib
import os
import tempfile
import zipfile

from models import symTyperTask


def writeFile(origin, destination):
    """Writes origin file to new destination.

    Args:
        origin: file to be copied.
        destination: destination for copying.

    """
    with open(destination, 'w') as dest:
        for chunk in origin.chunks():
            dest.write(chunk)


def searchTable(tablePath, site):
    """Returns a single row from a csv.

    Args:
        tablePath: path to csv.
        site: site header of line to be copied.
    Returns:
        the row of csv in dict form.

    """
    site = str(site)
    with open(tablePath) as reader:
        try:
            headers = reader.next()
            keys = [header.split('_')[0] for header in headers.split()[1:]]
            for row in reader:
                row2 = row.split()
                if row2[0] == site:
                    return dict(zip(keys, row2[1:]))
        except:
            pass
    return {}


def csv2list(csvPath):
    """Turns csv file(for subtypes tab) into a dictionary.

    Args:
        csvPath: path to csv.
    Returns:
        counts: the csv in a dictionary.
        headers: the csv headers in a list.

    """
    try:
        with open(csvPath) as tsv:
            counts = []
            all = [line.strip().split() for line in tsv]
            headers = all[0]

            if len(headers) > 1:
                for row in all[1:]:
                    counts.append(dict(zip(headers, row)))
                return counts, headers
    except:
        pass
    return None, None


def treeCsv(csvPath):
    """Turns csv(for tree tab) into dictionary.

    Args:
        csvPath: path to csv.
    Returns:
        counts: the csv in a dictionary.
        headers: the csv headers in a list.

    """
    try:
        with open(csvPath) as tsv:
            counts = []
            all = [line.strip().split() for line in tsv]
            headers = all[0]
            headers.insert(0, 'node')

            if len(headers) > 1:
                for row in all[1:]:
                    if len(row) == len(headers):
                        counts.append(dict(zip(headers, row)))
                return counts, headers
    except:
        pass
    return None, None


def multiplesCsv(csvPath):
    """Turns csv(for multiples tab) into dictionary.

    Args:
        csvPath: path to csv.
    Returns:
        counts: the csv in a dictionary.
        headers: the csv headers in a list.

    """
    #try:
        #with open(csvPath) as tsv:
            #table = []
            #headers = []
            #first = True

            #for line in tsv:
                #row = []
                #splitTabs = line.strip().split('\t')
                #for tab in splitTabs:
                    #data = tab.strip().split(':', 1)
                    #if first:
                        #headers.append(data[0])
                    #row.append(data[1].strip())
                #table.append(dict(zip(headers, row)))
                #first = False
            #return table, headers
    #except:
        #pass
    #return None, None
    try:
        with open(csvPath) as tsv:
            header = []
            table = []
            breakdown = []
            subtypes = []
            first = True

            for line in tsv:
                row = []
                splitTabs = line.strip().split('\t')

                for tab in splitTabs[:3]:
                    data = tab.strip().split(':', 1)
                    if first:
                        header.append(data[0])
                    row.append(data[1].strip())
                table.append(dict(zip(header, row)))
                first = False

                for tab in splitTabs[3:4]:
                    dic = {}
                    data = tab.strip().split(':', 1)
                    splitSpace = data[1].split(' ')
                    for space in splitSpace:
                        info = space.split(':')
                        dic[info[0]] = int(info[1])
                    breakdown.append(dic)

                for tab in splitTabs[4:5]:
                    dic = {}
                    data = tab.strip().split(':', 1)
                    commaSpace = data[1].strip().split(',')
                    for comma in commaSpace[:-1]:
                        info = comma.strip().split(': ')
                        dic[info[0]] = int(info[1])
                    subtypes.append(dic)

            return table, header, breakdown, subtypes
    except:
        pass
    return None, None, None, None




def servZip(request, path):
    """Returns Downloadable zip file"""
    temp = tempfile.TemporaryFile()
    rootlen = len(path) + 1
    with zipfile.ZipFile(temp, 'w', zipfile.ZIP_DEFLATED) as myzip:
        for root, dirs, files in os.walk(path):
            myzip.write(root, root[rootlen:])
            for filename in files:
                myzip.write(os.path.join(root, filename), os.path.join(root, filename)[rootlen:])
    wrapper = FileWrapper(temp)
    response = HttpResponse(wrapper, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=%s.zip' % (smart_str(os.path.basename(path)))
    response['Content-Length'] = temp.tell()
    temp.seek(0)
    return response


def servFile(request, ready, filename, fPath, fsize):
    """Returns Downloadable file."""
    response = HttpResponse(mimetype='application/force-download')
    #if(not Status.SUCCESS):
    #    return response
    #response['Content-Type'] = contentType
    response['Content-Disposition'] = 'attachment; filename=%s' % (smart_str(filename))
    response['X-Sendfile'] = urllib.quote(fPath)
    response['Content-Transfer-Encoding'] = "binary"
    response['Expires'] = 0
    response['Accept-Ranges'] = 'bytes'
    response['Cache-Control'] = "private"
    response['Pragma'] = 'private'
    httprange = request.META.get("HTTP_RANGE", None)
    if(httprange):
        rng = httprange.split("=")
        cnt = rng[-1].split("-")
        response['Content-Length'] = fsize - int(cnt[0])
        response['Content-Range'] = str(httprange) + str(response['Content-Length']) + "/" + str(fsize)
    else:
        response['Content-Length'] = fsize
    with open(fPath) as outfile:
        buf = outfile.read(4096)
        while len(buf) == 4096:
            response.write(buf)
            buf = outfile.read(4096)
        while len(buf) == 4096:
            response.write(buf)
            buf = outfile.read(4096)
        if(len(buf) != 0):
            response.write(buf)
    return response


def taskReady(jobObj, redirect="error"):
    """Checks if celery task is ready.

    Args:
        celeryID: the id of a celery task.
        redirect: page to redirect to on error.
    Returns:
        True,None: celery task finished successfully.
        False, HttpResponseRedirect: celerytask failed.
        False,False: celery task is still processing.

    """
    #task = AsyncResult(jobObj.celeryUID)
    if jobObj.state == symTyperTask.DONE:
        return True, None
    elif jobObj.state == symTyperTask.ERROR:
        return False, HttpResponseRedirect(reverse(redirect))
    else:
        return False, None

    # if task.ready():
    #     if task.successful():
    #         return True, None
    #     else:
    #         return False, HttpResponseRedirect(reverse(redirect))
    # else:
    #     return False, None
