from django.db import models
from django import forms
from django.contrib import admin


# Create your models here.

class symTyperTask(models.Model):
    celeryUID = models.TextField(null=True, blank=True)
    UID = models.TextField(null=True, blank=True)


class InputForm(forms.Form):
    fasta_File = forms.FileField()
    sample_File = forms.FileField()

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


admin.site.register(symTyperTask, AdminSymTyperTask)
