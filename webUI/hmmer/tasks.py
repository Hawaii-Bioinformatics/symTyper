'''
Created on Jul 5, 2013

@author: taylorak
'''
from celery.task import task
from django.conf import settings
from django.db.models import Q
from models import symTyperTask
from forms import InputForm
import datetime
import os
#from subprocess import call


@task(ignore_results=True)
def handleForm(fasta, sample, inputform, uid):
    sym_task = symTyperTask.objects.get(UID = uid)
    sym_task.celeryUID = handleForm.request.id
    sym_task.state = symTyperTask.RUNNING
    sym_task.save()

    parentDir = os.path.join(settings.SYMTYPER_HOME, uid)
    imageDir = os.path.join(settings.SYMTYPER_IMG, uid)

    os.chdir(parentDir)
    os.environ['PATH'] += os.pathsep + settings.BIN_PATH
    ret = os.system("""chmod 775 %s"""%(parentDir)) 
    ret = os.system("""%s -t %s clade -i %s -s %s --hmmdb %s """ % (settings.SYMTYPER_PATH, settings.SYMTYPER_THREADS, fasta, sample, settings.SYMTYPER_HMMDB))
    ret = os.system("""%s -t %s subtype -H hmmer_hits/ -s %s -b blast_output/ -r blastResults/ -f fasta --blastdb %s """%(settings.SYMTYPER_PATH, settings.SYMTYPER_THREADS, sample, settings.SYMTYPER_BLASTDB))
    ret = os.system("""%s -t %s resolveMultipleHits -s %s -m blastResults/MULTIPLE/ -c resolveMultiples/ """%(settings.SYMTYPER_PATH, settings.SYMTYPER_THREADS, sample))
    ret = os.system("""xvfb-run  %s -t %s buildPlacementTree -c resolveMultiples/correctedMultiplesHits/corrected -n %s -o placementInfo """%(settings.SYMTYPER_PATH, settings.SYMTYPER_THREADS, os.path.join(settings.SYMTYPER_DBASE, "clades_phylogenies") ) )
    ret = os.system("""%s -t %s stats --outputs_dir %s -i %s --out_file %s """%(settings.SYMTYPER_PATH, settings.SYMTYPER_THREADS, parentDir, fasta, os.path.join(parentDir,"outputfile")) )
    ret = os.system("""%s -t %s makeTSV --outputs_dir %s"""%(settings.SYMTYPER_PATH, settings.SYMTYPER_THREADS, parentDir)) 

    os.makedirs(imageDir)
    ret = os.system("""chgrp -R www-data %s """%(parentDir))
    ret = os.system("""ln -s %s %s """ % (os.path.join(parentDir, 'placementInfo'), imageDir))

    os.chdir(settings.SYMTYPER_HOME)
    ret = os.system("""zip -r %s.zip %s -x@%s """%(uid, uid, settings.ZIP_EXCLUDE))
    ret = os.system("""mv %s.zip %s """%(uid, os.path.join(parentDir, "all.zip")) )
    
    os.chdir(parentDir)
    ret = os.system("""zip -r trees.zip %s """%("placementInfo"))
    ret = os.system("""zip -r multiples.zip %s """%(os.path.join("resolveMultiples", "correctedMultiplesHits")) )
    ret = os.system("""zip -r subtypes.zip %s """%("blastResults"))
    ret = os.system("""zip -r clades.zip %s """%("hmmer_parsedOutput"))

    #os.system("""chmod -R 775 %s"""%(imageDir))
    #os.system("""chgrp -R www-data %s"""%(imageDir))

    sym_task = symTyperTask.objects.get(UID=uid)
    sym_task.state = symTyperTask.DONE
    sym_task.save()
    

@task(ignore_result=True)
def executeDeleteData(uid):
    job_directory = os.path.join(settings.SYMTYPER_HOME, uid)
    os.system("rm -r %s"%(job_directory))
    os.system("rm %s"%(os.path.join(settings.STATIC_ROOT, 'img', uid)))
    return True


@task()
def cleanupJobs(removeOlder):
    try:
        removeOlder = int(removeOlder)
    except:
        removeOlder = 10
    thresh = datetime.datetime.utcnow() - datetime.timedelta(days=removeOlder)
    
    for job_object in symTyperTask.objects.filter(Q(modified__lte = thresh)).exclude( Q(state = symTyperTask.RUNNING) | Q(state = symTyperTask.NOT_STARTED) ) :      
        executeDeleteData(str(job_object.UID))
    symTyperTask.objects.filter(Q(modified__lte = thresh)).exclude( Q(state = symTyperTask.RUNNING) | Q(state = symTyperTask.NOT_STARTED) ).delete()
    return True
