import yaml
from django import forms

class InputForm(forms.Form):
    fasta_File = forms.FileField()
    sample_File = forms.FileField()
    clade_evalue = forms.FloatField(label = "E-Value", initial = 1e-20, )
    clade_evalDiff = forms.FloatField(label = "E-value Difference", initial = 1e5)
    subtype_evalue = forms.FloatField(label = "E-Value", initial = 1e-05, )
    resolveMulti_similarity = forms.FloatField(label = "Similarity", initial = 0.97, )


    def __init__(self, *args, **kwargs):
       super(InputForm, self).__init__(*args, **kwargs)
       self.fields['clade_evalue'].widget.attrs['readonly'] = True
       self.fields['clade_evalDiff'].widget.attrs['readonly'] = True
       self.fields['subtype_evalue'].widget.attrs['readonly'] = True
       self.fields['resolveMulti_similarity'].widget.attrs['readonly'] = True

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

    def yamlfyParams(self):
        """{clade_e-value: 1.0e-20, clade_e-value+differences: 100000.0, resolve+multiplie+hits_similarity: 0.97, subtype_e-value: 1.0e-05}"""
        return yaml.dump({ 'clade_e-value' : self.cleaned_data['clade_evalue'],
          'clade_e-value+differences' : self.cleaned_data['clade_evalDiff'],
          'resolve+multiplie+hits_similarity' : self.cleaned_data['resolveMulti_similarity'],
          'subtype_e-value' : self.cleaned_data['subtype_evalue']})
 
