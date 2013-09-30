# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'DialerSetting'
        db.create_table('dialer_setting', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True)),
            ('max_frequency', self.gf('django.db.models.fields.IntegerField')(default='100', null=True, blank=True)),
            ('callmaxduration', self.gf('django.db.models.fields.IntegerField')(default='1800', null=True, blank=True)),
            ('maxretry', self.gf('django.db.models.fields.IntegerField')(default='3', null=True, blank=True)),
            ('max_calltimeout', self.gf('django.db.models.fields.IntegerField')(default='45', null=True, blank=True)),
            ('max_number_campaign', self.gf('django.db.models.fields.IntegerField')(default=100)),
            ('max_number_subscriber_campaign', self.gf('django.db.models.fields.IntegerField')(default=100000)),
            ('blacklist', self.gf('django.db.models.fields.TextField')(default='', null=True, blank=True)),
            ('whitelist', self.gf('django.db.models.fields.TextField')(default='', null=True, blank=True)),
            ('created_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'dialer_settings', ['DialerSetting'])


    def backwards(self, orm):
        # Deleting model 'DialerSetting'
        db.delete_table('dialer_setting')


    models = {
        u'dialer_settings.dialersetting': {
            'Meta': {'object_name': 'DialerSetting', 'db_table': "'dialer_setting'"},
            'blacklist': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'callmaxduration': ('django.db.models.fields.IntegerField', [], {'default': "'1800'", 'null': 'True', 'blank': 'True'}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_calltimeout': ('django.db.models.fields.IntegerField', [], {'default': "'45'", 'null': 'True', 'blank': 'True'}),
            'max_frequency': ('django.db.models.fields.IntegerField', [], {'default': "'100'", 'null': 'True', 'blank': 'True'}),
            'max_number_campaign': ('django.db.models.fields.IntegerField', [], {'default': '100'}),
            'max_number_subscriber_campaign': ('django.db.models.fields.IntegerField', [], {'default': '100000'}),
            'maxretry': ('django.db.models.fields.IntegerField', [], {'default': "'3'", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'whitelist': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['dialer_settings']