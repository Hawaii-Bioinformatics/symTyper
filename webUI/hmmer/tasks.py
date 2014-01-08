'''
Created on Jul 5, 2013

@author: taylorak
'''
from celery.task import task
from django.conf import settings
import os
#from subprocess import call


@task(ignore_results=True)
def handleForm(fasta, sample, uid):
    # parentDir):
    parentDir = os.path.join(settings.SYMTYPER_HOME, uid)
    #print parentDir
    imageDir = os.path.join(settings.PROJECT_ROOT, 'static', 'img', uid)
    #print imageDir

    #with open(os.path.join(parentDir, 'log')) as log:
    os.chdir(parentDir)
    os.system("""python /home/taylor/symTyper/symTyper.py --threads 12 clade --i %s -s %s""" % (fasta, sample))
#    log.write('finished clades/n')
    os.system("""python /home/taylor/symTyper/symTyper.py  -t 3 subtype -H data/hmmer_hits/ -s %s -b data/blast_output/ -r data/blastResults/ -f data/fasta"""%(sample))
    os.system("""python /home/taylor/symTyper/symTyper.py  -t 3 resolveMultipleHits -s %s -m data/blastResults/MULTIPLE/fasta/ -c data/resolveMultiples/"""%(sample))
    os.system("""python /home/taylor/symTyper/symTyper.py  -t 3 builPlacementTree -c data/resolveMultiples/correctedMultiplesHits/corrected -n /home/taylor/Clade_Trees/ -o data/placementInfo""")
    os.makedirs(imageDir)
    os.system("""cp -r %s %s""" % (os.path.join(parentDir,'data', 'placementInfo'), imageDir))
