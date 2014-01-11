# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'DialerSetting.sms_max_frequency'
        db.add_column('dialer_setting', 'sms_max_frequency',
                      self.gf('django.db.models.fields.IntegerField')(default='100', null=True, blank=True),
                      keep_default=False)

        # Adding field 'DialerSetting.sms_maxretry'
        db.add_column('dialer_setting', 'sms_maxretry',
                      self.gf('django.db.models.fields.IntegerField')(default='3', null=True, blank=True),
                      keep_default=False)

        # Adding field 'DialerSetting.sms_max_number_campaign'
        db.add_column('dialer_setting', 'sms_max_number_campaign',
                      self.gf('django.db.models.fields.IntegerField')(default=10),
                      keep_default=False)

        # Adding field 'DialerSetting.sms_max_number_subscriber_campaign'
        db.add_column('dialer_setting', 'sms_max_number_subscriber_campaign',
                      self.gf('django.db.models.fields.IntegerField')(default=10000),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'DialerSetting.sms_max_frequency'
        db.delete_column('dialer_setting', 'sms_max_frequency')

        # Deleting field 'DialerSetting.sms_maxretry'
        db.delete_column('dialer_setting', 'sms_maxretry')

        # Deleting field 'DialerSetting.sms_max_number_campaign'
        db.delete_column('dialer_setting', 'sms_max_number_campaign')

        # Deleting field 'DialerSetting.sms_max_number_subscriber_campaign'
        db.delete_column('dialer_setting', 'sms_max_number_subscriber_campaign')


    models = {
        u'dialer_settings.dialersetting': {
            'Meta': {'object_name': 'DialerSetting', 'db_table': "'dialer_setting'"},
            'blacklist': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'callmaxduration': ('django.db.models.fields.IntegerField', [], {'default': "'1800'", 'null': 'True', 'blank': 'True'}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_calltimeout': ('django.db.models.fields.IntegerField', [], {'default': "'45'", 'null': 'True', 'blank': 'True'}),
            'max_contact': ('django.db.models.fields.IntegerField', [], {'default': '1000000'}),
            'max_cpg': ('django.db.models.fields.IntegerField', [], {'default': '100'}),
            'max_frequency': ('django.db.models.fields.IntegerField', [], {'default': "'100'", 'null': 'True', 'blank': 'True'}),
            'max_subr_cpg': ('django.db.models.fields.IntegerField', [], {'default': '100000'}),
            'maxretry': ('django.db.models.fields.IntegerField', [], {'default': "'3'", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'sms_max_frequency': ('django.db.models.fields.IntegerField', [], {'default': "'100'", 'null': 'True', 'blank': 'True'}),
            'sms_max_number_campaign': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            'sms_max_number_subscriber_campaign': ('django.db.models.fields.IntegerField', [], {'default': '10000'}),
            'sms_maxretry': ('django.db.models.fields.IntegerField', [], {'default': "'3'", 'null': 'True', 'blank': 'True'}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'whitelist': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['dialer_settings']