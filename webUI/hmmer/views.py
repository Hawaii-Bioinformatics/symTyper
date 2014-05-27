from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
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
from parse_hierarchy import parseHierarchyYAML


import os
import time
from collections import defaultdict
import yaml
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
        with open(os.path.join(output, "ALL_counts.tsv")) as tsv:
            # order is maintained and we don't really reorder, so why use zip and dict?
            all_headers = [ l for l in tsv.next().strip().split() ]
            all_counts = [ row.strip().split() for row in tsv ]

        with open(os.path.join(output, "DETAILED_counts.tsv")) as tsv:
            # remove the sample
            detailed_headers = tsv.next().strip().split()[1:]
            detailed_counts = [ zip(detailed_headers, row.strip().split()[1:]) for row in tsv ]

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
        #'detailed_headers': detailed_headers,
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
    ready, redirect = taskReady(sym_task)
    if ready:
        done = True
    elif redirect:
        return redirect
    else:
        pass
        #message = "pending..."

    if done:
        context = descriptiveStats(id)
        params = yaml.load(sym_task.params)
        parm = defaultdict(list)
        for k, v in params.iteritems():
            section, label = k.replace('+',' ').split("_")
            parm[section.title()].append( (label, v,))
        for k in parm:
            parm[k].sort(key = lambda x: x[0])

        context['done'] = done
        context['id'] = id
        context['params'] = dict(parm)
    else:
        context= {
            'done': done, 
            'id': id
            }
    return render(request, template, context)


def descriptiveStats(uid):
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
    subclade = [ ("Perfect", sbbrk['PERFECT'],), ("Unique", sbbrk['UNIQUE'],), 
                 ("Short New", sbbrk['SHORTNEW'],), ("Short", sbbrk['SHORT'],),
                 ("New", sbbrk['NEW'],), ("Multiple", sbbrk['MULTIPLE'],)]
    subclade.append( ("Total",  sum( (int(s[1]) for s in subclade) ), ) )
    
    multi = [("In Tree", stats['nbInTree'],), ("Resolved", stats['nbResolved'],) ]

    return dict(uid = uid, fullset = fullset, clade = clade, subclade = subclade, multi = multi)


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
        fPath = os.path.join(settings.SYMTYPER_HOME, str(id), "clades.zip")
        fsize = os.stat(fPath).st_size
        filename = settings.SYMTYPER_ZIP_FMT%(str(id), "clades")
        return servFile(request, ready, filename, fPath, fsize)
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
        fPath = os.path.join(settings.SYMTYPER_HOME, str(id), "subtypes.zip")
        fsize = os.stat(fPath).st_size
        filename = settings.SYMTYPER_ZIP_FMT%(str(id), "subtypes")
        return servFile(request, ready, filename, fPath, fsize)
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
        fPath = os.path.join(settings.SYMTYPER_HOME, str(id), "multiples.zip")
        fsize = os.stat(fPath).st_size
        filename = settings.SYMTYPER_ZIP_FMT%(str(id), "multiples")
        return servFile(request, ready, filename, fPath, fsize)

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
        fPath = os.path.join(settings.SYMTYPER_HOME, str(id), "trees.zip")
        fsize = os.stat(fPath).st_size
        filename = settings.SYMTYPER_ZIP_FMT%(str(id), "trees")
        return servFile(request, ready, filename, fPath, fsize)
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
        filename = settings.SYMTYPER_ZIP_FMT%(str(id), "all_results")
        return servFile(request, ready, filename, fPath, fsize)
    elif redirect:
        return redirect
    else:
        return HttpResponseRedirect(reverse("status", args=[sym_task.UID]))

def dlBiom(request, id):
    try:
        sym_task = symTyperTask.objects.get(UID=id)
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse("form"))

    ready, redirect = taskReady(sym_task)
    if ready:
        fPath = os.path.join(settings.SYMTYPER_HOME, str(id), "breakdown.biom")
        fsize = os.stat(fPath).st_size
        filename = "breakdown.biom"
        return servFile(request, ready, filename, fPath, fsize)
    elif redirect:
        return redirect
    else:
        return HttpResponseRedirect(reverse("status", args=[sym_task.UID]))



def biomGraph(request, uid, sample, template = "biom_graph.html"):   
    biof = os.path.join(settings.SYMTYPER_HOME, uid, "breakdown.biom")
    biom = open(biof)
    biom.next()
    sampleids = [l.split()[0].strip() for l in biom]
    biom.close()
    return render_to_response(template, RequestContext(request, dict(sampleids = sampleids, sample = sample, uid = uid, id = uid)  ))        

def biomGraphSXS(request, uid, sampleA, sampleB, template = "biom_graph_sxs.html"):   
    return render_to_response(template, RequestContext(request, dict(sampleA = sampleA, sampleB = sampleB,  uid = uid, id = uid)  ))        



def generateBiomSampleGraph(request, uid, sample):
    biof = os.path.join(settings.SYMTYPER_HOME, str(uid), "breakdown.biom")
    biom = open(biof)
    hdrs = biom.next().strip().split()
    hdrs = hdrs[1:] # remove the header 'sample'
    jdata = None
    for l in biom:
        if not l.startswith(sample):
            continue
        l = l.strip().split()
        sid = l[0]
        data = dict(zip(hdrs, l[1:]))
        jdata = parseHierarchyYAML(settings.HIERARCHY_YAML, sid, data)
        
        break
    return HttpResponse(jdata, content_type = "application/json")


