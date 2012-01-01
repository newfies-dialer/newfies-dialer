# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Phonebook'
        db.create_table(u'dialer_phonebook', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=90)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='Phonebook owner', to=orm['auth.User'])),
            ('created_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('dialer_campaign', ['Phonebook'])

        # Adding model 'Contact'
        db.create_table(u'dialer_contact', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('phonebook', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dialer_campaign.Phonebook'])),
            ('contact', self.gf('django.db.models.fields.CharField')(max_length=90)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=120, null=True, blank=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=120, null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('country', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['prefix_country.Country'], null=True, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=120, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default='1', null=True, blank=True)),
            ('additional_vars', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('created_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('dialer_campaign', ['Contact'])

        # Adding unique constraint on 'Contact', fields ['contact', 'phonebook']
        db.create_unique(u'dialer_contact', ['contact', 'phonebook_id'])

        # Adding model 'Campaign'
        db.create_table(u'dialer_campaign', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('campaign_code', self.gf('django.db.models.fields.CharField')(default='FCNSJ', unique=True, max_length=20, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='Campaign owner', to=orm['auth.User'])),
            ('status', self.gf('django.db.models.fields.IntegerField')(default='2', null=True, blank=True)),
            ('callerid', self.gf('django.db.models.fields.CharField')(max_length=80, blank=True)),
            ('startingdate', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2011, 12, 25, 0, 46, 6, 758367))),
            ('expirationdate', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 1, 25, 0, 46, 6, 758445))),
            ('daily_start_time', self.gf('django.db.models.fields.TimeField')(default='00:00:00')),
            ('daily_stop_time', self.gf('django.db.models.fields.TimeField')(default='23:59:59')),
            ('monday', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('tuesday', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('wednesday', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('thursday', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('friday', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('saturday', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('sunday', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('frequency', self.gf('django.db.models.fields.IntegerField')(default='10', null=True, blank=True)),
            ('callmaxduration', self.gf('django.db.models.fields.IntegerField')(default='1800', null=True, blank=True)),
            ('maxretry', self.gf('django.db.models.fields.IntegerField')(default='0', null=True, blank=True)),
            ('intervalretry', self.gf('django.db.models.fields.IntegerField')(default='300', null=True, blank=True)),
            ('calltimeout', self.gf('django.db.models.fields.IntegerField')(default='45', null=True, blank=True)),
            ('aleg_gateway', self.gf('django.db.models.fields.related.ForeignKey')(related_name='A-Leg Gateway', to=orm['dialer_gateway.Gateway'])),
            ('voipapp', self.gf('django.db.models.fields.related.ForeignKey')(related_name='VoIP Application', to=orm['voip_app.VoipApp'])),
            ('extra_data', self.gf('django.db.models.fields.CharField')(max_length=120, blank=True)),
            ('created_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('dialer_campaign', ['Campaign'])

        # Adding M2M table for field phonebook on 'Campaign'
        db.create_table(u'dialer_campaign_phonebook', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('campaign', models.ForeignKey(orm['dialer_campaign.campaign'], null=False)),
            ('phonebook', models.ForeignKey(orm['dialer_campaign.phonebook'], null=False))
        ))
        db.create_unique(u'dialer_campaign_phonebook', ['campaign_id', 'phonebook_id'])

        # Adding model 'CampaignSubscriber'
        db.create_table(u'dialer_campaign_subscriber', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('contact', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dialer_campaign.Contact'], null=True, blank=True)),
            ('campaign', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dialer_campaign.Campaign'], null=True, blank=True)),
            ('last_attempt', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('count_attempt', self.gf('django.db.models.fields.IntegerField')(default='0', null=True, blank=True)),
            ('duplicate_contact', self.gf('django.db.models.fields.CharField')(max_length=90)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default='1', null=True, blank=True)),
            ('created_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('dialer_campaign', ['CampaignSubscriber'])

        # Adding unique constraint on 'CampaignSubscriber', fields ['contact', 'campaign']
        db.create_unique(u'dialer_campaign_subscriber', ['contact_id', 'campaign_id'])

    def backwards(self, orm):
        # Removing unique constraint on 'CampaignSubscriber', fields ['contact', 'campaign']
        db.delete_unique(u'dialer_campaign_subscriber', ['contact_id', 'campaign_id'])

        # Removing unique constraint on 'Contact', fields ['contact', 'phonebook']
        db.delete_unique(u'dialer_contact', ['contact', 'phonebook_id'])

        # Deleting model 'Phonebook'
        db.delete_table(u'dialer_phonebook')

        # Deleting model 'Contact'
        db.delete_table(u'dialer_contact')

        # Deleting model 'Campaign'
        db.delete_table(u'dialer_campaign')

        # Removing M2M table for field phonebook on 'Campaign'
        db.delete_table('dialer_campaign_phonebook')

        # Deleting model 'CampaignSubscriber'
        db.delete_table(u'dialer_campaign_subscriber')

    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'dialer_campaign.campaign': {
            'Meta': {'object_name': 'Campaign', 'db_table': "u'dialer_campaign'"},
            'aleg_gateway': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'A-Leg Gateway'", 'to': "orm['dialer_gateway.Gateway']"}),
            'callerid': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'}),
            'callmaxduration': ('django.db.models.fields.IntegerField', [], {'default': "'1800'", 'null': 'True', 'blank': 'True'}),
            'calltimeout': ('django.db.models.fields.IntegerField', [], {'default': "'45'", 'null': 'True', 'blank': 'True'}),
            'campaign_code': ('django.db.models.fields.CharField', [], {'default': "'RFANK'", 'unique': 'True', 'max_length': '20', 'blank': 'True'}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'daily_start_time': ('django.db.models.fields.TimeField', [], {'default': "'00:00:00'"}),
            'daily_stop_time': ('django.db.models.fields.TimeField', [], {'default': "'23:59:59'"}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'expirationdate': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 1, 25, 0, 46, 6, 785627)'}),
            'extra_data': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'}),
            'frequency': ('django.db.models.fields.IntegerField', [], {'default': "'10'", 'null': 'True', 'blank': 'True'}),
            'friday': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intervalretry': ('django.db.models.fields.IntegerField', [], {'default': "'300'", 'null': 'True', 'blank': 'True'}),
            'maxretry': ('django.db.models.fields.IntegerField', [], {'default': "'0'", 'null': 'True', 'blank': 'True'}),
            'monday': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'phonebook': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['dialer_campaign.Phonebook']", 'null': 'True', 'blank': 'True'}),
            'saturday': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'startingdate': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 12, 25, 0, 46, 6, 785486)'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': "'2'", 'null': 'True', 'blank': 'True'}),
            'sunday': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'thursday': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'tuesday': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'Campaign owner'", 'to': "orm['auth.User']"}),
            'voipapp': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'VoIP Application'", 'to': "orm['voip_app.VoipApp']"}),
            'wednesday': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'dialer_campaign.campaignsubscriber': {
            'Meta': {'unique_together': "(['contact', 'campaign'],)", 'object_name': 'CampaignSubscriber', 'db_table': "u'dialer_campaign_subscriber'"},
            'campaign': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dialer_campaign.Campaign']", 'null': 'True', 'blank': 'True'}),
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dialer_campaign.Contact']", 'null': 'True', 'blank': 'True'}),
            'count_attempt': ('django.db.models.fields.IntegerField', [], {'default': "'0'", 'null': 'True', 'blank': 'True'}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'duplicate_contact': ('django.db.models.fields.CharField', [], {'max_length': '90'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_attempt': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': "'1'", 'null': 'True', 'blank': 'True'}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'dialer_campaign.contact': {
            'Meta': {'unique_together': "(['contact', 'phonebook'],)", 'object_name': 'Contact', 'db_table': "u'dialer_contact'"},
            'additional_vars': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'contact': ('django.db.models.fields.CharField', [], {'max_length': '90'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['prefix_country.Country']", 'null': 'True', 'blank': 'True'}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'phonebook': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dialer_campaign.Phonebook']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': "'1'", 'null': 'True', 'blank': 'True'}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'dialer_campaign.phonebook': {
            'Meta': {'object_name': 'Phonebook', 'db_table': "u'dialer_phonebook'"},
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '90'}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'Phonebook owner'", 'to': "orm['auth.User']"})
        },
        'dialer_gateway.gateway': {
            'Meta': {'object_name': 'Gateway', 'db_table': "u'dialer_gateway'"},
            'addparameter': ('django.db.models.fields.CharField', [], {'max_length': '360', 'blank': 'True'}),
            'addprefix': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'count_call': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'count_in_use': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'failover': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'Failover Gateway'", 'null': 'True', 'to': "orm['dialer_gateway.Gateway']"}),
            'gateway_codecs': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'gateway_retries': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'gateway_timeouts': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'gateways': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'maximum_call': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'originate_dial_string': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'removeprefix': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'secondused': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': "'1'", 'null': 'True', 'blank': 'True'}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'prefix_country.country': {
            'Meta': {'object_name': 'Country', 'db_table': "'simu_country'"},
            'countrycode': ('django.db.models.fields.CharField', [], {'max_length': '240'}),
            'countryname': ('django.db.models.fields.CharField', [], {'max_length': '240'}),
            'countryprefix': ('django.db.models.fields.IntegerField', [], {'max_length': '12'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'voip_app.voipapp': {
            'Meta': {'object_name': 'VoipApp', 'db_table': "u'voip_app'"},
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'data': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'gateway': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dialer_gateway.Gateway']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '90'}),
            'type': ('django.db.models.fields.IntegerField', [], {'default': "'1'", 'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'VoIP App owner'", 'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['dialer_campaign']