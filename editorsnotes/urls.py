# vim: set tw=0:

from django.conf.urls import patterns, url, include
from django.conf import settings
from django.views.generic.base import RedirectView
from editorsnotes.main.views.auth import CustomBrowserIDVerify

# These will be intercepted by apache in production
urlpatterns = patterns('',
    (r'^favicon.ico$', RedirectView.as_view(url='/static/style/icons/favicon.ico')),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': settings.MEDIA_ROOT }),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': settings.STATIC_ROOT }),
    (r'^proxy$', 'editorsnotes.main.views.proxy'),
)

# Auth patterns
urlpatterns += patterns('',
  # CENDARI:old  url(r'^accounts/login/$', 'django.contrib.auth.views.login', { 'redirect_field_name': 'return_to' }),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', { 'redirect_field_name': 'return_to' }, name='user_login_view'),
    url(r'^accounts/logout/$', 'editorsnotes.main.views.auth.user_logout', name='user_logout_view'),
    url(r'^accounts/profile/$', 'editorsnotes.main.views.auth.user'),
    url(r'^accounts/profile/feedback/$', 'editorsnotes.main.views.auth.user_feedback', name='user_feedback_view'),
    url(r'^accounts/browserid/$', CustomBrowserIDVerify.as_view(), name='browserid_verify'),
    url(r'^user/(?P<username>[\w@\+\.\-]+)/$', 'editorsnotes.main.views.auth.user', name='user_view'),
)

# Base patterns
urlpatterns += patterns('editorsnotes.main.views.navigation',
    url(r'^$', 'index', name='index_view'),
    url(r'^about/$', 'about', name='about_view'),
    url(r'^about/test/$', 'about_test'),
    url(r'^search/$', 'search', name='search_view'),
    url(r'^version/$', 'get_version', name='get_version'),
)

# Admin patterns
urlpatterns += patterns('',
    url(r'^projects/(?P<project_slug>\w+)/', include('editorsnotes.admin.urls', namespace='admin', app_name='admin')),
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
   # CENDARI:old url(r'^api/document/template/', 'zotero_template'),
   # CENDARI:old url(r'^api/document/blank/$', 'get_blank_item', name='get_blank_item_view'),
   # CENDARI:old url(r'^api/document/itemtypes/$', 'get_item_types'),
   # CENDARI:old url(r'^api/document/csl/$', 'zotero_json_to_csl', name='zotero_json_to_csl_view'),
   # CENDARI:old url(r'^api/document/archives/$', 'api_archives', name='api_archives_view'),
)
#urlpatterns += patterns('editorsnotes.refine.views',
#    url(r'^topics/clusters/$', 'show_topic_clusters', name='show_topic_clusters_view'),
#    url(r'^topics/merge/(?P<cluster_id>\d+)/$', 'merge_topic_cluster', name='merge_topic_cluster_view'),
#)
