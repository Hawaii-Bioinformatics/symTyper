# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'symTyperTask'
        db.create_table(u'hmmer_symtypertask', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('celeryUID', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('UID', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'hmmer', ['symTyperTask'])


    def backwards(self, orm):
        # Deleting model 'symTyperTask'
        db.delete_table(u'hmmer_symtypertask')


    models = {
        u'hmmer.symtypertask': {
            'Meta': {'object_name': 'symTyperTask'},
            'UID': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'celeryUID': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['hmmer']