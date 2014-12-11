# import editorsnotes.search.index
# import editorsnotes.search as old
# 
# class CendariENIndex(object):
#     def __init__(self, en):
#         self.en = en
#  
#     @property
#     def document_types(self):
#         return self.en.document_types
#  
#     def put_mapping(self):
#         self.en.put_type_mappings()
#  
#     def get_name(self):
#         return self.en.get_name()
#  
#     def get_settings(self):
#         self.en.get_settings()
#  
#     def put_type_mappings(self):
#         self.en.put_type_mappings()
#  
#     def exists(self):
#         return self.en.exists()
#  
#     def create(self):
#         return self.en.create()
#  
#     def delete(self):
#         return self.en.delete()
#  
#     def register(self, model, adapter=None, highlight_fields=None,
#                  display_field=None):
#         self.en.register(model, adapter, highlight_fields, display_field)
#  
#     def data_for_object(self, obj):
#         return self.en.data_for_object(obj)
#  
#     def search_model(self, model, query, **kwargs):
#         return self.en.search_model(model, query, **kwargs)
#  
#     def search(self, query, highlight=False, **kwargs):
#         #print "search query="+query
#         if isinstance(query, basestring):
#             prepared_query = {
#                 'query': {
#                     'query_string': { 'query': query,
#                                       'fields': ['display_title'] }
#                 },
#             }
#             if 'project' in kwargs:
#                 prepared_query['filter'] = {
#                     'term': { 'serialized.project.name': kwargs['project'] } 
#                 }
#                 del kwargs['project']
#                 #print prepared_query
#  
#         else:
#             prepared_query = query
#          
#         return self.en.search(prepared_query, highlight, **kwargs)
#  
# old.en_index = CendariENIndex(old.en_index)
