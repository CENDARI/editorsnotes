# vim: set tw=0:

from django.conf.urls import patterns, url, include
from django.contrib import admin
from django.conf import settings
from django.views.generic.base import RedirectView
from editorsnotes.main.views.auth import CustomBrowserIDVerify

from editorsnotes.main.views.topics import LegacyTopicRedirectView

from editorsnotes.admin.views.notes import NoteAdminView
#from editorsnotes.api.views.notes import NoteList


from cendari.views import NoteCendari,DocumentCendari, EditNoteAdminView, EditDocumentAdminView, EditTopicAdminView,  EditTranscriptAdminView
import cendari.views
import editorsnotes.admin.views
#admin.autodiscover()

# These will be intercepted by apache in production
urlpatterns = patterns('',
    (r'^favicon.ico$', RedirectView.as_view(url='/static/style/icons/favicon.ico')),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': settings.MEDIA_ROOT }),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': settings.STATIC_ROOT }),
    (r'^proxy$', 'editorsnotes.main.views.proxy'),
)


# Auth patterns
urlpatterns += patterns('',
    url(r'^accounts/logout/$', 'editorsnotes.main.views.auth.user_logout', name='user_logout_view'),
    url(r'^accounts/profile/$', 'editorsnotes.main.views.auth.user'),
    url(r'^accounts/profile/feedback/$', 'editorsnotes.main.views.auth.user_feedback', name='user_feedback_view'),
    url(r'^accounts/browserid/$', CustomBrowserIDVerify.as_view(), name='browserid_verify'),
    url(r'^user/(?P<username>[\w@\+\.\-]+)/$', 'editorsnotes.main.views.auth.user', name='user_view'),
)

#
# django-admin2 patterns
# 

USE_ADMIN2 = False
try:
    import djadmin2
    USE_ADMIN2 = True
except:
    pass

if USE_ADMIN2:
    import admin2
    urlpatterns += patterns('',
                            url(r'^admin2/', include(djadmin2.default.urls)))

# Base patterns
urlpatterns += patterns('editorsnotes.main.views.navigation',
    #url(r'^$', 'index', name='index_view'),
    url(r'^about/$', 'about', name='about_view'),
    url(r'^about/test/$', 'about_test'),
    url(r'^search/$', 'search', name='search_view'),
    url(r'^version/$', 'get_version', name='get_version'),
)

# Admin patterns
urlpatterns += patterns('',
    url(r'^projects/(?P<project_slug>[-\w]+)/', include('editorsnotes.admin.urls', namespace='admin', app_name='admin')),
    url(r'^projects/add/', 'editorsnotes.admin.views.projects.add_project', name='add_project_view'),
)

# Main model patterns
urlpatterns += patterns('',
    url(r'^', include('editorsnotes.main.urls')),
)

# API
urlpatterns += patterns('',
    url(r'^api/', include('editorsnotes.api.urls', namespace='api', app_name='api')),
    url(r'^api/metadata/topics/types/$', 'editorsnotes.api.views.topics.topic_types'),
)

urlpatterns += patterns('editorsnotes.djotero.views',
#    url(r'^document/upload/$', 'import_zotero', name='import_zotero_view'),
#    url(r'^document/upload/libraries/$', 'libraries', name='libraries_view'),
#    url(r'^document/upload/collections/$', 'collections', name='collections_view'),
#    url(r'^document/upload/items/$', 'items', name='items_view'),
#    url(r'^document/upload/continue/$', 'items_continue', name='items_continue_view'),
#    url(r'^document/upload/import/$', 'import_items', name='import_items_view'),
    url(r'^user/zotero_info$', 'update_zotero_info', name='update_zotero_info_view'),
    url(r'^api/metadata/documents/item_template/$', 'item_template', name='item_template_view'),
    url(r'^api/metadata/documents/item_types/$', 'item_types', name='item_types_view'),
    url(r'^api/metadata/documents/item_type_creators/$', 'item_type_creators', name='item_type_creators_view'),
    url(r'^api/document/archives/$', 'api_archives', name='api_archives_view'),
)
#urlpatterns += patterns('editorsnotes.refine.views',
#    url(r'^topics/clusters/$', 'show_topic_clusters', name='show_topic_clusters_view'),
#    url(r'^topics/merge/(?P<cluster_id>\d+)/$', 'merge_topic_cluster', name='merge_topic_cluster_view'),
#)

import editorsnotes.admin.views.projects

cendaripatterns = patterns('cendari.views',
    url(r'^$',                                                                              'index',                              name='index_view'),
    url(r'^cendari/browse/$',                                                               'browse_cendari',                     name='cendari_browse_view'),
    url(r'^cendari/about/$',                                                                'about_cendari',                      name='cendari_about_view'),
    url(r'^cendari/external/(?P<type>\w+)/$',                                               'iframe_view',                        name='iframe_view'),
    

    url(r'^cendari/(?P<project_slug>[-\w]+)/index$',                                           'index',                              name='index_project'),
    

    # Cendari Projects
    url(r'^cendari/projects/add/',                                                          'cendari_project_add',                name='add_project_view'),
    url(r'^cendari/projects/(?P<project_id>\d+)/$',                                          'cendari_project_change',            name='project_view'),
    url(r'^projects/(?P<project_slug>[-\w]+)/',                                                 include('editorsnotes.admin.urls',   namespace='admin', app_name='admin')),
    #url(r'^cendari/projects/add/$',                                                         cendari.views.change_project,        name='addproject_view'),
    #url(r'^cendari/projects/(?P<slug>[-_a-z0-9]+)/$',                                       EditProjectAdminView.as_view(),      name='project_view'),

	# Cendari Notes
    #url(r'^cendari/(?P<project_slug>[-\w]+)/notes/(?P<note_id>\d+)/$',                          EditNoteAdminView.as_view(),         name='note_view'),
   # url(r'^cendari/(?P<project_slug>[-\w]+)/notes/add/$',                                       EditNoteAdminView.as_view(),         name='addnote_view'),
    #url(r'^cendari/(?P<project_slug>[-\w]+)/notes/(?P<note_id>\d+)/$',                          NoteCendari.as_view(),                    name='note_view'),
    url(r'^cendari/(?P<project_slug>[-\w]+)/notes/add/$',                                       NoteCendari.as_view(),                name='addnote_view'),
    url(r'^cendari/(?P<project_slug>[-\w]+)/notes/(?P<note_id>\d+)/$',                          'editNoteCendari',                name='note_view'),
    url(r'^cendari/(?P<project_slug>[-\w]+)/notes/(?P<note_id>\d+)/read$',                          'readNoteCendari',                name='note_read'),
    url(r'^cendari/(?P<project_slug>[-\w]+)/notes/(?P<note_id>\d+)/rdfa/$', 'rdfa_view_note', name='rdfa_view_note'),


    # Cendari Documents
    url(r'^cendari/(?P<project_slug>[-\w]+)/documents/(?P<document_id>\d+)/transcript/$',       EditTranscriptAdminView.as_view(),   name='transcript_edit_view'),
    url(r'^cendari/(?P<project_slug>[-\w]+)/documents/(?P<document_id>\d+)/rdfa/$', 'rdfa_view_document', name='rdfa_view_document'),
   # url(r'^cendari/(?P<project_slug>[-\w]+)/documents/(?P<document_id>\d+)/$',                  EditDocumentAdminView.as_view(),     name='document_view'),
    url(r'^cendari/(?P<project_slug>[-\w]+)/documents/(?P<document_id>\d+)/$',                 'editDocumentCendari',                name='document_view'),
    url(r'^cendari/(?P<project_slug>[-\w]+)/documents/(?P<document_id>\d+)/read/$',                 'readDocumentCendari',                name='document_read'),
   # url(r'^cendari/(?P<project_slug>[-\w]+)/documents/add/$',                                   EditDocumentAdminView.as_view(),     name='adddocument_view'),
    url(r'^cendari/(?P<project_slug>[-\w]+)/documents/add/$',                                   DocumentCendari.as_view(),     name='adddocument_view'),

    # Cendari Topics
    #url(r'^cendari/(?P<project_slug>[-\w]+)/topics/add/$',                                      EditTopicAdminView.as_view(),        name='addtopic_view'),
    #url(r'^cendari/(?P<project_slug>[-\w]+)/topics/(?P<topic_node_id>\d+)/$',                   EditTopicAdminView.as_view(),        name='topic_view'),
    url(r'^cendari/(?P<project_slug>[-\w]+)/topics/(?P<topic_node_id>\d+)/$',                   'editEntityCendari',                  name='topic_view'),
	url(r'^cendari/topic/(?P<topic_node_id>[\w\-,]+)/$',                                        'edit_topic_node',                 name='topic_node_view'),

    
    # Cendari Resources Tree
    url(r'^cendari/(?P<project_slug>[-\w]+)/resources/$',                                       'resources',                         name='resources_view'),
    url(r'^cendari/(?P<project_slug>[-\w]+)/getResourcesData/sfield/(?P<sfield>[-\w]+)/$',	'getResourcesData',                  name='getResourcesData_view'),
    url(r'^cendari/(?P<project_slug>[-\w]+)/getLazyProjectData/sfield/(?P<sfield>[-\w]+)/$',    'getLazyProjectData',                name='getLazyProjectData_view'),
    url(r'^cendari/(?P<project_slug>[-\w]+)/getTopicType/topic_id/(?P<topic_id>\d+)/$',         'getTopicType',                      name='getTopicType_view'),
    url(r'^cendari/(?P<project_slug>[-\w]+)/getProjectID/new_slug/(?P<new_slug>[-\w]+)/$',         'getProjectID',                      name='getProjectID_view'),

	# Cendari Scans
    url(r'^cendari/(?P<project_slug>[-\w]+)/scan/(?P<scan_id>\d+)/$',                           'scan',                              name='scan_view'),
    url(r'^cendari/(?P<project_slug>[-\w]+)/scan/(?P<scan_id>\d+)/image/$',                           'scan_image',                   name='scan_image'),
    url(r'^cendari/(?P<project_slug>[-\w]+)/scan/(?P<scan_id>\d+)/tiff/$',                           'scan_tiffimage',                   name='scan_tiffimage'),
    
	# Cendari Jigsaw
#    url(r'^cendari/(?P<project_slug>[-\w]+)/importfromjigsaw/$',                                'import_from_jigsaw',                name='importfromjigsaw_view'),

	# Cendari Visualizations
	url(r'^cendari/(?P<project_slug>[-\w]+)/smallvis/$',                                        'small_vis',                         name='smallvis_view'),
    url(r'^cendari/(?P<project_slug>[-\w]+)/smallvisdata/$',                                    'small_vis_data_lazy',               name='smallvisdata_view'),
    
    url(r'^querySPARQL/(?P<q>[^/]*)/',                                                       'querySPARQL',                       name='querySPARQL'),

    url(r'^proxyRDFaCE/$',                                                                   'proxyRDFaCE',                       name='proxyRDFaCE'),

    # Cendari search
    url(r'^cendari/(?P<project_slug>[-\w]+)/search/$',                                          'search',                            name='cendari_search_view'),
    url(r'^cendari/faceted/$', 'faceted_search', name='cendari_faceted_search_view'),
    url(r'^cendari/(?P<project_slug>[-\w]+)/faceted/$', 'faceted_search', name='cendari_faceted_search_view'),
    url(r'^cendari/autocomplete_search/term/(?P<term>[-\w]+)/$', 'autocomplete_search', name = 'autocomplete_search_view'),

   # Cendari chat
   url(r'^chat/', include('djangoChat.urls')),
   url(r'^cendari/(?P<project_slug>[-\w]+)/chat/$',                                       'cendari_chat',                         name='cendari_chat_view'),

   #Cendari image browser
   url(r'^cendari/(?P<project_slug>[-\w]+)/documents/(?P<document_id>\d+)/image_browse/$', 'image_browse',name='image_browse'),

)

urlpatterns += cendaripatterns


