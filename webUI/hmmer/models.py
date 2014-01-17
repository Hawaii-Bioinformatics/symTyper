from django.db import models
from django import forms
from django.contrib import admin


# Create your models here.

class symTyperTask(models.Model):
    NOT_DONE = 0
    DONE = 1
    ERROR = 2
    STATES=  ( (NOT_DONE, "Not Done",),
               (DONE, "Done",),
               (ERROR, "Error",),
             )

    celeryUID = models.TextField(null=True, blank=True)
    UID = models.TextField(null=True, blank=True)
    state = models.IntegerField(default = NOT_DONE, choices = STATES, blank = False, null = False)

    

class InputForm(forms.Form):
    fasta_File = forms.FileField()
    sample_File = forms.FileField()
    evalue = forms.FloatField(label = "E-Value", initial = 1e-05, )
    evalDiff = forms.FloatField(label = "E-value Difference", initial = 1e5)
 
    def __init__(self, *args, **kwargs):
       super(InputForm, self).__init__(*args, **kwargs)
       self.fields['evalue'].widget.attrs['readonly'] = True
       self.fields['evalDiff'].widget.attrs['readonly'] = True

    def clean_fasta_File(self):
        data = self.cleaned_data['fasta_File']
        if not data.name.endswith('.fasta'):
            raise forms.ValidationError("extension must be fasta")
        return data

    def clean_sample_File(self):
        data = self.cleaned_data['sample_File']
        if not data.name.endswith('.ids'):
            raise forms.ValidationError("extension must be ids")
        return data


class AdminSymTyperTask(admin.ModelAdmin):
    list_display = ['celeryUID', 'UID']


#admin.site.register(symTyperTask, AdminSymTyperTask)
