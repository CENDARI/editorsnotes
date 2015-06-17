define(['backbone','models/message'],function(Backbone,MsgModel){

	Messages = Backbone.Collection.extend({
			model : MsgModel,
			url : cendari_root_url+'chat/api/'
	});

	return Messages;

});
