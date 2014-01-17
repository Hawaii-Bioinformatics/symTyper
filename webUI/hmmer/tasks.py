'''
Created on Jul 5, 2013

@author: taylorak
'''
from celery.task import task
from django.conf import settings
import os
#from subprocess import call


@task(ignore_results=True)
def handleForm(fasta, sample, evalue, uid):
    sym_task = symTyperTask.objects.get(UID=uid)
    sym_task.celeryUID = current_task.request.id
    sym_task.save()

    parentDir = os.path.join(settings.SYMTYPER_HOME, uid)
    imageDir = os.path.join(settings.STATIC_ROOT, 'img', uid)

    os.chdir(parentDir)
    os.environ['PATH'] += os.pathsep + settings.BIN_PATH
    os.system("""chmod 775 %s"""%(parentDir)) 
    os.system("""%s --threads %s clade --i %s -s %s""" % (settings.SYMTYPER_PATH, settings.SYMTYPER_THREADS, fasta, sample))
    os.system("""%s  -t %s subtype -H hmmer_hits/ -s %s -b blast_output/ -r blastResults/ -f fasta """%(settings.SYMTYPER_PATH, settings.SYMTYPER_THREADS, sample))
    os.system("""%s  -t %s resolveMultipleHits -s %s -m blastResults/MULTIPLE/fasta/ -c resolveMultiples/"""%(settings.SYMTYPER_PATH, settings.SYMTYPER_THREADS, sample))
    os.system("""xvfb-run  %s  -t %s builPlacementTree -c resolveMultiples/correctedMultiplesHits/corrected -n /home/celery/symtyper/dbases/clades_phylogenies/ -o placementInfo"""%(settings.SYMTYPER_PATH, settings.SYMTYPER_THREADS))
    os.makedirs(imageDir)
    os.system("""chgrp -R www-data %s"""%(parentDir))
    os.system("""cp -r %s %s""" % (os.path.join(parentDir, 'placementInfo'), imageDir))
    os.system("""chmod -R 775 %s"""%(imageDir))
    os.system("""chgrp -R www-data %s"""%(imageDir))

    sym_task = symTyperTask.objects.get(UID=uid)
    sym_task.state = symTyperTask.DONE
    sym_task.save()
    
