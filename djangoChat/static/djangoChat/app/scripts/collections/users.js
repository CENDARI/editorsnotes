define(['backbone','models/user'],function(Backbone,usrModel){
	return Backbone.Collection.extend({
		url:cendari_root_url+'chat/api/users/',
		model:usrModel
	});
});