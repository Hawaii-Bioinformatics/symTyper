from django import template
from django.conf import settings
from hmmer.general import csv2list, taskReady
from hmmer.models import symTyperTask
import os

register = template.Library()


@register.inclusion_tag('navbar/navbar.html', takes_context=True)
def navbar(context, id):
    multiples = {}
    trees = {}
    letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']

    ## Subtypes
    output = os.path.join(settings.SYMTYPER_HOME, str(id), "data", "blastResults")
    unique_counts, unique_headers = csv2list(os.path.join(output, "UNIQUE_subtypes_count.tsv"))
    shortnew_counts, shortnew_headers = csv2list(os.path.join(output, "SHORTNEW_subtypes_count.tsv"))
    perfect_counts, perfect_headers = csv2list(os.path.join(output, "PERFECT_subtypes_count.tsv"))

    ## Multiples
    cPath = os.path.join(settings.SYMTYPER_HOME, str(id), "data", "resolveMultiples", "correctedMultiplesHits", "corrected")
    rPath = os.path.join(settings.SYMTYPER_HOME, str(id), "data", "resolveMultiples", "correctedMultiplesHits", "resolved")
    ## Trees
    tPath = os.path.join(settings.SYMTYPER_HOME, str(id), "data", "placementInfo")

    for letter in letters:

        if os.path.exists(os.path.join(cPath, str(letter))) or os.path.exists(os.path.join(rPath, str(letter))):
            multiples[letter] = True
        else:
            multiples[letter] = None

        if os.path.exists(os.path.join(tPath, str(letter), "treenodeCladeDist.tsv")):
            trees[letter] = True
        else:
            trees[letter] = None

    done = False

    if id:
        sym_task = symTyperTask.objects.get(UID=id)

        ready, redirect = taskReady(sym_task.celeryUID)
        if ready:
            done = True

    context = {
        'id': id,
        'unique_counts': unique_counts,
        'shortnew_counts': shortnew_counts,
        'perfect_counts': perfect_counts,
        'multiples': multiples,
        'trees': trees,
        'request': context['request'],
        'done': done,
    }

    return context
