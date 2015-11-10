# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'TopicCluster'
        db.create_table(u'refine_topiccluster', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.User'], null=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('marked_for_merge', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('message', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'refine', ['TopicCluster'])

        # Adding M2M table for field topics on 'TopicCluster'
        db.create_table(u'refine_topiccluster_topics', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('topiccluster', models.ForeignKey(orm[u'refine.topiccluster'], null=False)),
            ('topic', models.ForeignKey(orm['main.topic'], null=False))
        ))
        db.create_unique(u'refine_topiccluster_topics', ['topiccluster_id', 'topic_id'])

        # Adding model 'DocumentCluster'
        db.create_table(u'refine_documentcluster', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.User'], null=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('marked_for_merge', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('message', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'refine', ['DocumentCluster'])

        # Adding M2M table for field documents on 'DocumentCluster'
        db.create_table(u'refine_documentcluster_documents', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('documentcluster', models.ForeignKey(orm[u'refine.documentcluster'], null=False)),
            ('document', models.ForeignKey(orm['main.document'], null=False))
        ))
        db.create_unique(u'refine_documentcluster_documents', ['documentcluster_id', 'document_id'])

        # Adding model 'BadClusterPair'
        db.create_table(u'refine_badclusterpair', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('obj1', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('obj2', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal(u'refine', ['BadClusterPair'])


    def backwards(self, orm):
        # Deleting model 'TopicCluster'
        db.delete_table(u'refine_topiccluster')

        # Removing M2M table for field topics on 'TopicCluster'
        db.delete_table('refine_topiccluster_topics')

        # Deleting model 'DocumentCluster'
        db.delete_table(u'refine_documentcluster')

        # Removing M2M table for field documents on 'DocumentCluster'
        db.delete_table('refine_documentcluster_documents')

        # Deleting model 'BadClusterPair'
        db.delete_table(u'refine_badclusterpair')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'djotero.cachedarchive': {
            'Meta': {'object_name': 'CachedArchive'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {})
        },
        u'djotero.cachedcreator': {
            'Meta': {'object_name': 'CachedCreator'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {})
        },
        u'djotero.zoterolink': {
            'Meta': {'object_name': 'ZoteroLink'},
            'cached_archive': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['djotero.CachedArchive']", 'null': 'True', 'blank': 'True'}),
            'cached_creator': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['djotero.CachedCreator']", 'null': 'True', 'blank': 'True'}),
            'date_information': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_synced': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {}),
            'zotero_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        u'licensing.license': {
            'Meta': {'object_name': 'License'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': "'80'"}),
            'symbols': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'url': ('django.db.models.fields.URLField', [], {'unique': 'True', 'max_length': '200'})
        },
        'main.citation': {
            'Meta': {'ordering': "['ordering']", 'object_name': 'Citation'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'created_citation_set'", 'to': "orm['main.User']"}),
            'document': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'citations'", 'to': "orm['main.Document']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'last_updater': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'last_to_update_citation_set'", 'to': "orm['main.User']"}),
            'notes': ('editorsnotes.main.fields.XHTMLField', [], {'null': 'True', 'blank': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'ordering': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'main.document': {
            'Meta': {'ordering': "['ordering', 'import_id']", 'unique_together': "(('project', 'description_digest'),)", 'object_name': 'Document'},
            'collection': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'parts'", 'null': 'True', 'to': "orm['main.Document']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'created_document_set'", 'to': "orm['main.User']"}),
            'description': ('editorsnotes.main.fields.XHTMLField', [], {}),
            'description_digest': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'edtf_date': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'import_id': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '64', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'default': "'English'", 'max_length': '32'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'last_updater': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'last_to_update_document_set'", 'to': "orm['main.User']"}),
            'ordering': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'documents'", 'to': "orm['main.Project']"}),
            'zotero_data': ('editorsnotes.djotero.fields.ZoteroField', [], {'null': 'True', 'blank': 'True'}),
            'zotero_link': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'zotero_item'", 'unique': 'True', 'null': 'True', 'to': u"orm['djotero.ZoteroLink']"})
        },
        'main.project': {
            'Meta': {'object_name': 'Project'},
            'default_license': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': u"orm['licensing.License']"}),
            'description': ('editorsnotes.main.fields.XHTMLField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': "'80'"}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'})
        },
        'main.topic': {
            'Meta': {'unique_together': "(('project', 'preferred_name'), ('project', 'topic_node'))", 'object_name': 'Topic'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'created_topic_set'", 'to': "orm['main.User']"}),
            'date': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'last_updater': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'last_to_update_topic_set'", 'to': "orm['main.User']"}),
            'merged_into': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Topic']", 'null': 'True', 'blank': 'True'}),
            'preferred_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'topics'", 'to': "orm['main.Project']"}),
            'rdf': ('cendari.fields.RDFField', [], {'null': 'True', 'blank': 'True'}),
            'summary': ('editorsnotes.main.fields.XHTMLField', [], {'null': 'True', 'blank': 'True'}),
            'topic_node': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'project_topics'", 'to': "orm['main.TopicNode']"})
        },
        'main.topicassignment': {
            'Meta': {'unique_together': "(('content_type', 'object_id', 'topic'),)", 'object_name': 'TopicAssignment'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'created_topicassignment_set'", 'to': "orm['main.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'topic': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'assignments'", 'null': 'True', 'to': "orm['main.Topic']"})
        },
        'main.topicnode': {
            'Meta': {'object_name': 'TopicNode'},
            '_preferred_name': ('django.db.models.fields.CharField', [], {'max_length': "'200'"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'created_topicnode_set'", 'to': "orm['main.User']"}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'last_updater': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'last_to_update_topicnode_set'", 'to': "orm['main.User']"}),
            'merged_into': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.TopicNode']", 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True', 'blank': 'True'})
        },
        'main.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'zotero_key': ('django.db.models.fields.CharField', [], {'max_length': "'24'", 'null': 'True', 'blank': 'True'}),
            'zotero_uid': ('django.db.models.fields.CharField', [], {'max_length': "'10'", 'null': 'True', 'blank': 'True'})
        },
        u'refine.badclusterpair': {
            'Meta': {'object_name': 'BadClusterPair'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'obj1': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'obj2': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        u'refine.documentcluster': {
            'Meta': {'object_name': 'DocumentCluster'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.User']", 'null': 'True', 'blank': 'True'}),
            'documents': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'in_cluster'", 'symmetrical': 'False', 'to': "orm['main.Document']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'marked_for_merge': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'message': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        u'refine.topiccluster': {
            'Meta': {'object_name': 'TopicCluster'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.User']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'marked_for_merge': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'message': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'topics': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'in_cluster'", 'symmetrical': 'False', 'to': "orm['main.Topic']"})
        }
    }

    complete_apps = ['refine']