from django.db import models
from django.contrib import admin



class symTyperTask(models.Model):
    NOT_STARTED = 0
    DONE = 1
    ERROR = 2
    RUNNING = 3
    STATES=  ( (NOT_STARTED, "Not Started",),
               (RUNNING, "Running",),
               (DONE, "Done",),
               (ERROR, "Error",),
             )

    celeryUID = models.TextField(null=True, blank=True)
    UID = models.TextField(null=True, blank=True)
    state = models.IntegerField(default = NOT_STARTED, choices = STATES, blank = False, null = False)
    modified = models.DateField(auto_now = True)
    created = models.DateField(auto_now_add = True)

class AdminSymTyperTask(admin.ModelAdmin):
    list_display = ['celeryUID', 'UID', 'created', 'modified']


#admin.site.register(symTyperTask, AdminSymTyperTask)
