from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.shortcuts import render

from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

#from celery.result import AsyncResult

from general import writeFile, searchTable, csv2list, treeCsv, multiplesCsv, servFile, taskReady, servZip
from forms import InputForm
from models import  symTyperTask
from tasks import handleForm

import os
import time

# Create your views here.


def errorPage(request, template='upload.html'):
    return render(request, template)


def inputFormDisplay(request, template='upload.html'):
    """Displays input form that takes fasta and ids files."""
    if request.method == 'POST':
        form = InputForm(request.POST, request.FILES)
        if form.is_valid():
            # create UID
            sym_task = symTyperTask.objects.create()
            sym_task.UID = str(sym_task.id) + '.' + str(time.time())
            sym_task.save()
            parentDir = os.path.join(settings.SYMTYPER_HOME, sym_task.UID)

            os.makedirs(parentDir)
            os.system("""chmod 775 %s"""%(parentDir))
            fasta = os.path.join(parentDir, "input.fasta")
            samples = os.path.join(parentDir, "samples.ids")

            writeFile(request.FILES['fasta_File'], fasta)
            writeFile(request.FILES['sample_File'], samples)

            task = handleForm.delay(fasta, samples, "test", sym_task.UID)
            #sym_task.celeryUID = task.id
            #sym_task.save()

            return HttpResponseRedirect(reverse("index", args=[sym_task.UID]))
    else:
        form = InputForm()

    context = {'form': form,}

    return render(request, template, context)


def clades(request, id, template='clades.html'):
    """Displays clade results."""
    dirs = all_counts = detailed_counts = all_headers = detailed_headers = None

    try:
        sym_task = symTyperTask.objects.get(UID=id)
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse("form"))

    output = os.path.join(settings.SYMTYPER_HOME, str(id), "hmmer_parsedOutput")
    ready, redirect = taskReady(sym_task)
    if ready:
        #dirs = [d for d in os.listdir(output)
                #if os.path.isdir(os.path.join(output, d))]

        with open(os.path.join(output, "ALL_counts.tsv")) as tsv:
            all_counts = []
            all_lines = [line.strip().split() for line in tsv]
            all_headers = all_lines[0]

            for row in all_lines[1:]:
                total = hit = no_hit = low = ambiguous = percentages = 0
                site = row[0]
                for column in row[1:]:
                    total += int(column)

                if total != 0:
                    hit = round(float(row[1])/total * 100, 2)
                    no_hit = round(float(row[2])/total * 100, 2)
                    low = round(float(row[3])/total * 100, 2)
                    ambiguous = round(float(row[4])/total * 100, 2)
                percentages = [site, hit, no_hit, low, ambiguous]
                all_counts.append(dict(zip(all_headers, percentages)))

        with open(os.path.join(output, "DETAILED_counts.tsv")) as tsv:
            detailed_counts = []

            all_lines = [line.strip().split() for line in tsv]
            detailed_headers = all_lines[0][1:]

            for row in all_lines[1:]:
                data = []
                site = row[0]
                for column in row[1:]:
                    data.append(column)
                detailed_counts.append(dict(zip(detailed_headers, data)))

        paginator1 = Paginator(all_counts, 50)
        paginator2 = Paginator(detailed_counts, 50)

        page = request.GET.get('page')
        try:
            all_counts = paginator1.page(page)
            detailed_counts = paginator2.page(page)
        except PageNotAnInteger:
            all_counts = paginator1.page(1)
            detailed_counts = paginator2.page(1)
        except EmptyPage:
            all_counts_counts = paginator1.page(paginator.num_pages)
            detailed_counts = paginator2.page(paginator.num_pages)

    elif redirect:
        return redirect
    else:
        return HttpResponseRedirect(reverse("index", args=[sym_task.UID]))

    context = {
        'id': id,
        'title': "Clades",
        'dirs': dirs,
        'all_headers': all_headers,
        'all_counts': all_counts,
        'detailed_counts': detailed_counts,
        'detailed_headers': detailed_headers,
    }

    return render(request, template, context)


##
# Subtypes
##

def unique(request, id, template='subtypes.html'):
    """Displays subtypes results."""

    try:
        sym_task = symTyperTask.objects.get(UID=id)
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse("form"))

    output = os.path.join(settings.SYMTYPER_HOME, str(id), "blastResults")
    ready, redirect = taskReady(sym_task)
    if ready:
        counts, headers = csv2list(os.path.join(output, "UNIQUE_subtypes_count.tsv"))
        #shortnew_counts, shortnew_headers = csv2list(os.path.join(output, "SHORTNEW_subtypes_count.tsv"))
        #perfect_counts, perfect_headers = csv2list(os.path.join(output, "PERFECT_subtypes_count.tsv"))
    elif redirect:
        return redirect
    else:
        return HttpResponseRedirect(reverse("index", args=[sym_task.UID]))

    context = {
        #'shortnew_counts': shortnew_counts,
        #'shortnew_headers': shortnew_headers,
        #'unique_counts': unique_counts,
        #'unique_headers': unique_headers,
        #'perfect_counts': perfect_counts,
        #'perfect_headers': perfect_headers,
        'counts': counts,
        'headers': headers,
        'title': "Unique Subtypes",
        'id': id,
    }

    return render(request, template, context)


def shortnew(request, id, template='subtypes.html'):
    """Displays subtypes results."""

    try:
        sym_task = symTyperTask.objects.get(UID=id)
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse("form"))

    output = os.path.join(settings.SYMTYPER_HOME, str(id), "blastResults")
    ready, redirect = taskReady(sym_task)
    if ready:
        counts, headers = csv2list(os.path.join(output, "SHORTNEW_subtypes_count.tsv"))
        #perfect_counts, perfect_headers = csv2list(os.path.join(output, "PERFECT_subtypes_count.tsv"))
    elif redirect:
        return redirect
    else:
        return HttpResponseRedirect(reverse("index", args=[sym_task.UID]))

    context = {
        'title': "Short New Subtypes",
        'counts': counts,
        'headers': headers,
        'id': id,
    }

    return render(request, template, context)


def perfect(request, id, template='subtypes.html'):
    """Displays subtypes results."""

    try:
        sym_task = symTyperTask.objects.get(UID=id)
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse("form"))

    output = os.path.join(settings.SYMTYPER_HOME, str(id), "blastResults")
    ready, redirect = taskReady(sym_task)
    if ready:
        counts, headers = csv2list(os.path.join(output, "PERFECT_subtypes_count.tsv"))
    elif redirect:
        return redirect
    else:
        return HttpResponseRedirect(reverse("index", args=[sym_task.UID]))

    context = {
        'title': "Perfect Subtypes",
        'counts': counts,
        'headers': headers,
        'id': id,
    }

    return render(request, template, context)



def multiplesCorrected(request, id, file, template='multiples.html'):
    """Displays corrected multiples results."""

    try:
        sym_task = symTyperTask.objects.get(UID=id)
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse("form"))

    corrected = os.path.join(settings.SYMTYPER_HOME, str(id), "resolveMultiples", "correctedMultiplesHits", "corrected")
    ready, redirect = taskReady(sym_task)
    if ready:
        corrected_counts, corrected_headers, corrected_breakdown, corrected_subtypes = multiplesCsv(os.path.join(corrected, file))

        if corrected_counts != None and corrected_subtypes != None and corrected_breakdown != None:
            paginator1 = Paginator(corrected_counts, 5)
            paginator2 = Paginator(corrected_breakdown, 5)
            paginator3 = Paginator(corrected_subtypes, 5)

            page = request.GET.get('page')
            try:
                counts = paginator1.page(page)
                breakdown = paginator2.page(page)
                subtypes = paginator3.page(page)
            except PageNotAnInteger:
                counts = paginator1.page(1)
                breakdown = paginator2.page(1)
                subtypes = paginator3.page(1)
            except EmptyPage:
                counts = paginator1.page(paginator.num_pages)
                breakdown = paginator2.page(paginator.num_pages)
                subtypes = paginator3.page(paginator.num_pages)

    elif redirect:
        return redirect
    else:
        return HttpResponseRedirect(reverse("status", args=[sym_task.UID]))

    context = {
        'counts': counts,
        'headers': corrected_headers,
        'breakdown': breakdown,
        'subtypes': subtypes,
        'id': id,
        'file': file,
    }

    return render(request, template, context)


def multiplesResolved(request, id, file, template='multiples.html'):
    """Displays resolved multiples results."""

    try:
        sym_task = symTyperTask.objects.get(UID=id)
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse("form"))

    resolved = os.path.join(settings.SYMTYPER_HOME, str(id), "resolveMultiples", "correctedMultiplesHits", "resolved")
    ready, redirect = taskReady(sym_task)
    if ready:

        resolved_counts, resolved_headers, resolved_breakdown, resolved_subtypes = multiplesCsv(os.path.join(resolved, file))

        if resolved_counts != None and resolved_subtypes != None  and resolved_breakdown != None:
            paginator1 = Paginator(resolved_counts, 5)
            paginator2 = Paginator(resolved_breakdown, 5)
            paginator3 = Paginator(resolved_subtypes, 5)

            page = request.GET.get('page')
            try:
                counts = paginator1.page(page)
                breakdown = paginator2.page(page)
                subtypes = paginator3.page(page)
            except PageNotAnInteger:
                counts = paginator1.page(1)
                breakdown = paginator2.page(1)
                subtypes = paginator3.page(1)
            except EmptyPage:
                counts = paginator1.page(paginator.num_pages)
                breakdown = paginator2.page(paginator.num_pages)
                subtypes = paginator3.page(paginator.num_pages)

    elif redirect:
        return redirect
    else:
        return HttpResponseRedirect(reverse("status", args=[sym_task.UID]))

    context = {
        'file': file,
        'counts': resolved_counts,
        'headers': resolved_headers,
        'breakdown': resolved_breakdown,
        'subtypes': resolved_subtypes,
        'id': id,
    }

    return render(request, template, context)


def tree(request, id, file, template='tree.html'):
    """Displays treenode results."""
    try:
        sym_task = symTyperTask.objects.get(UID=id)
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse("form"))

    output = os.path.join(settings.SYMTYPER_HOME, str(id), "placementInfo")
    ready, redirect = taskReady(sym_task)
    if ready:
        counts, headers = treeCsv(os.path.join(output, file, "treenodeCladeDist.tsv"))
        if counts != None:
            paginator = Paginator(counts, 50)

            page = request.GET.get('page')
            try:
                counts = paginator.page(page)
            except PageNotAnInteger:
                counts = paginator.page(1)
            except EmptyPage:
                counts = paginator.page(paginator.num_pages)

    elif redirect:
        return redirect
    else:
        return HttpResponseRedirect(reverse("status", args=[sym_task.UID]))

    context = {
        'counts': counts,
        'headers': headers,
        'id': id,
        'file': file,
    }

    return render(request, template, context)


def chart(request, id, site):
    """Displays pie chart"""
    detailed_counts = None
    try:
        sym_task = symTyperTask.objects.get(UID=id)
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse("form"))

    output = os.path.join(settings.SYMTYPER_HOME, str(id), "hmmer_parsedOutput")
    ready, redirect = taskReady(sym_task)
    if ready:
        detailed_counts = searchTable(os.path.join(output, 'DETAILED_counts.tsv'),site)
    elif redirect:
        return redirect
    else:
        return HttpResponseRedirect(reverse("status", args=[sym_task.UID]))
    return render_to_response('chart.html', RequestContext(request, {'id': id, 'site': site, 'detailed_counts': detailed_counts}))


def index(request, id, template='index.html'):
    """Displays index page."""
    done = False

    try:
        sym_task = symTyperTask.objects.get(UID=id)
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse("form"))

    #output = os.path.join(settings.SYMTYPER_HOME, str(id), "hmmer_parsedOutput")
    ready, redirect = taskReady(sym_task)
    if ready:
        done = True
    elif redirect:
        return redirect
    else:
        pass
        #message = "pending..."
    context = {
            'done': done, 
            'id': id
            }
    return render(request, template, context)


def descriptiveStats(request, uid, template = "stats.html"):
    statsfile = open(os.path.join(settings.SYMTYPER_HOME, str(uid), "outputfile"))
    stats = eval(statsfile.read())
    statsfile.close()

    fullset =[ ('Total', stats['fastaFileSize'],) , ('Symbiodinium', stats['totalSymbioHits'],), ('Other', stats['totalNonSymbioHits'] ,) ]

    clade = []
    for k, v in stats['cladesCounts'].iteritems():
        clade.append( (k.split("_")[0].upper().replace("CLADE", "") , v,) )
    clade.sort(key = lambda x: x[0])
    clade.append( ('Total', sum( ( int(c[1]) for c in clade) ),)  )

    sbbrk = stats['subcladeBreakdown']
    subclade = [ ("Prefect", sbbrk['PERFECT'],), ("Unique", sbbrk['UNIQUE'],), 
                 ("Short New", sbbrk['SHORTNEW'],), ("Short", sbbrk['SHORT'],),
                 ("New", sbbrk['NEW'],), ("Multiple", sbbrk['MULTIPLE'],)]
    subclade.append( ("Total",  sum( (int(s[1]) for s in subclade) ), ) )
    
    multi = [("In Tree", stats['nbInTree'],), ("Resolved", stats['nbResolved'],) ]

    return render(request, template, dict(uid = uid, fullset = fullset, clade = clade, subclade = subclade, multi = multi)) 


def dlAll(request, id):
    try:
        sym_task = symTyperTask.objects.get(UID=id)
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse("form"))

    ready, redirect = taskReady(sym_task)
    if ready:
        fPath = os.path.join(settings.SYMTYPER_HOME, str(id), "hmmer_parsedOutput","ALL_counts.tsv")
        fsize = os.stat(fPath).st_size
        filename = "ALL_counts.tsv"
        return servFile(request, ready, filename, fPath, fsize)
    elif redirect:
        return redirect
    else:
        return HttpResponseRedirect(reverse("status", args=[sym_task.UID]))


def dlDetailed(request, id):
    try:
        sym_task = symTyperTask.objects.get(UID=id)
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse("form"))

    ready, redirect = taskReady(sym_task)
    if ready:
        fPath = os.path.join(settings.SYMTYPER_HOME, str(id), "hmmer_parsedOutput","DETAILED_counts.tsv")
        fsize = os.stat(fPath).st_size
        filename = "DETAILED_counts.tsv"
        return servFile(request, ready, filename, fPath, fsize)
    elif redirect:
        return redirect
    else:
        return HttpResponseRedirect(reverse("status", args=[sym_task.UID]))


def dlPerfect(request, id):
    try:
        sym_task = symTyperTask.objects.get(UID=id)
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse("form"))

    ready, redirect = taskReady(sym_task)
    if ready:
        fPath = os.path.join(settings.SYMTYPER_HOME, str(id), "blastResults","PEFECT_subtypes_count.tsv")
        fsize = os.stat(fPath).st_size
        filename = "PERFECT_subtypes_counts.tsv"
        return servFile(request, ready, filename, fPath, fsize)
    elif redirect:
        return redirect
    else:
        return HttpResponseRedirect(reverse("status", args=[sym_task.UID]))


def dlUnique(request, id):
    try:
        sym_task = symTyperTask.objects.get(UID=id)
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse("form"))

    ready, redirect = taskReady(sym_task)
    if ready:
        fPath = os.path.join(settings.SYMTYPER_HOME, str(id), "blastResults","UNIQUE_subtypes_count.tsv")
        fsize = os.stat(fPath).st_size
        filename = "UNIQUE_subtypes_count.tsv"
        return servFile(request, ready, filename, fPath, fsize)
    elif redirect:
        return redirect
    else:
        return HttpResponseRedirect(reverse("status", args=[sym_task.UID]))


def dlShortnew(request, id):
    try:
        sym_task = symTyperTask.objects.get(UID=id)
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse("form"))

    ready, redirect = taskReady(sym_task)
    if ready:
        fPath = os.path.join(settings.SYMTYPER_HOME, str(id), "blastResults","SHORTNEW_subtypes_count.tsv")
        fsize = os.stat(fPath).st_size
        filename = "SHORTNEW_subtypes__count.tsv"
        return servFile(request, ready, filename, fPath, fsize)
    elif redirect:
        return redirect
    else:
        return HttpResponseRedirect(reverse("status", args=[sym_task.UID]))


def dlClades(request, id):
    try:
        sym_task = symTyperTask.objects.get(UID=id)
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse("form"))

    ready, redirect = taskReady(sym_task)
    if ready:
        path = os.path.join(settings.SYMTYPER_HOME, str(id), "hmmer_parsedOutput")
        return servZip(request, path)
    elif redirect:
        return redirect
    else:
        return HttpResponseRedirect(reverse("status", args=[sym_task.UID]))


def dlSubtypes(request, id):
    try:
        sym_task = symTyperTask.objects.get(UID=id)
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse("form"))

    ready, redirect = taskReady(sym_task)
    if ready:
        path = os.path.join(settings.SYMTYPER_HOME, str(id), "blastResults")
        return servZip(request, path)
    elif redirect:
        return redirect
    else:
        return HttpResponseRedirect(reverse("status", args=[sym_task.UID]))


def dlMultiples(request, id):
    try:
        sym_task = symTyperTask.objects.get(UID=id)
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse("form"))

    ready, redirect = taskReady(sym_task)
    if ready:
        path = os.path.join(settings.SYMTYPER_HOME, str(id), "resolveMultiples", "correctedMultiplesHits")
        return servZip(request, path)
    elif redirect:
        return redirect
    else:
        return HttpResponseRedirect(reverse("status", args=[sym_task.UID]))


def dlTree(request, id):
    try:
        sym_task = symTyperTask.objects.get(UID=id)
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse("form"))

    ready, redirect = taskReady(sym_task)
    if ready:
        path = os.path.join(settings.SYMTYPER_HOME, str(id), "placementInfo")
        return servZip(request, path)
    elif redirect:
        return redirect
    else:
        return HttpResponseRedirect(reverse("status", args=[sym_task.UID]))

def dlEverything(request, id):
    try:
        sym_task = symTyperTask.objects.get(UID=id)
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse("form"))

    ready, redirect = taskReady(sym_task)
    if ready:
        fPath = os.path.join(settings.SYMTYPER_HOME, str(id), "all.zip")
        fsize = os.stat(fPath).st_size
        filename = "symtyper_%s_all_results.zip"%(str(id))
        return servFile(request, ready, filename, fPath, fsize)
    elif redirect:
        return redirect
    else:
        return HttpResponseRedirect(reverse("status", args=[sym_task.UID]))


