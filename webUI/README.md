#SymTyper Webpage#
A Bioinformatics Web Portal written in Django and themed with Bootstrap.  
##Overview
Web App for running SymTyper and viewing the outputs.
##Setup
In coral/settings.py change SYMTYPER_HOME and SYMTYPER_IMG to the directory where Symtyper should output it's results and the place where the placment tree images should be copied to.   
```
SYMTYPER_HOME = os.path.join(PROJECT_ROOT, "hmmer", "files") # Where Symtyper output goes
SYMTYPER_IMG = os.path.join(PROJECT_ROOT, "static", "img", "placement_trees") # Where placement tree image directory gets moved to
```
Install djcelery and a messaging broker like RabbitMQ. In coral/settings.py add djcelery to the list of INSTALLED_APPS and the following at the bottom of the file.  BROKER_URL will be different depending on how RabbitMQ is set up.  
```
import djcelery
djcelery.setup_loader()

BROKER_URL = 'amqp://worker:r@bb1t+w0rker+run@localhost:5672/portal'
```
##Usage
**Input fasta and ids file to run SymTyper.**  
![screenshot](https://raw.github.com/taylorak/coral/master/static/img/File_Form.png)  
**Use the navbar to view the outputs.**  
![screenshot](https://raw.github.com/taylorak/coral/master/static/img/Multiples.png)  
##Credits
Mahdi Belcaid, HIMB
