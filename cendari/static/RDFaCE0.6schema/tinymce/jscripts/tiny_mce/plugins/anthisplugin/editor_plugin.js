/**
 * editor_plugin_src.js
 *
 * Copyright 2009, Moxiecode Systems AB
 * Released under LGPL License.
 *
 * License: http://tinymce.moxiecode.com/license
 * Contributing: http://tinymce.moxiecode.com/contributing
 */

(function() {
	// Load plugin specific language pack
	tinymce.PluginManager.requireLangPack('anthisplugin');

	tinymce.create('tinymce.plugins.AnthisPluginPlugin', {
		/**
		 * Initializes the plugin, this will be executed after the plugin has been created.
		 * This call is done before the editor instance has finished it's initialization so use the onInit event
		 * of the editor instance to intercept that event.
		 *
		 * @param {tinymce.Editor} ed Editor instance that the plugin is initialized in.
		 * @param {string} url Absolute URL to where the plugin is located.
		 */
		init : function(ed, url) {
			// Register the command so that it can be invoked by using tinyMCE.activeEditor.execCommand('mceExample');
			ed.addCommand('mceAnthisPlugin', function() {
				/*ed.windowManager.open({
					file : url + '/dialog.htm',
					width : 320 + parseInt(ed.getLang('anthisplugin.delta_width', 0)),
					height : 120 + parseInt(ed.getLang('anthisplugin.delta_height', 0)),
					inline : 1
				}, {
					plugin_url : url, // Plugin absolute URL
					some_custom_arg : 'custom arg' // Custom argument
				});*/
				alert('anthisplugin');		
				
			});

			// Register example button
			ed.addButton('anthisplugin', {
				title : 'anthisplugin.desc',
				cmd : 'mceAnthisPlugin',
				image : url + '/img/buttonRed.png'
			});
	

			// Add a node change handler, selects the button in the UI when a image is selected
			ed.onNodeChange.add(function(ed, cm, n) {
				cm.setActive('anthisplugin', n.nodeName == 'IMG');
			});
			
			
			ed.plugins.contextmenu.onContextMenu.add(function(th, menu, event) {
							menu.removeAll();
							menu.addMenu({title : 'Person'});
							menu.addMenu({title : 'Place'});
									/*var add_entity = menu.addMenu({title : 'Add as Entity'});
									// show only related entities
							         var parent_node=$(event);
							         var has_rel=0;
							         var all_datatypes=[];
							         $.each(data.types,function(i,v){
							        	all_datatypes.push(v.id);
									 })
							          while(parent_node.length){
							        	  if(parent_node.hasClass('r_entity')){
							        		  has_rel=1;
							        		  // get the type of entity
							        		  var entity_type=getTypeOfEntity(parent_node,getCookie("annotationF"));
							        		  $.each(data.types[entity_type].properties,function(i,v){
							        			  // only show atomic
													// properties
							        			  if(all_datatypes.indexOf(data.properties[v].ranges[0]) != -1){
							        				  add_entity.add({title : data.properties[v].label, onclick: function(){
															insert_entity(a,data.properties[v].ranges[0],b,data.properties[v].id);
														}}); 
							        			  }
							        		  })
							        		  break;
							        	  }
							        	  parent_node=parent_node.parent();
							          }
							         parent_node=$(event);
							         var del_node;
							         //todo: enable deleting entities as well
							          while(parent_node.length){
							        	  del_node=parent_node;
							        	  if(parent_node.hasClass('r_prop') || parent_node.hasClass('r_entity')){
												menu.add({title : 'Delete', onclick: function(){
													remove_annotation(del_node,getCookie("annotationF"));
													a.setContent(a.getContent());
												}});
							        		  break;
							        	  }
							        	  parent_node=parent_node.parent();   
							          }
							        if(!has_rel){
										var others={};
										$.each(data.types,function(i,v){
											if(v.level==1){
												add_entity.add({title : v.label, onclick: function(){
													insert_entity(a,v.id,b,0);
												}});
											}else{
												others[v.id]=v.label;
											}
										})
										more_entities = add_entity.addMenu({title : 'More...'});
										$.each(others,function(i,v){
											more_entities.add({title : v, onclick: function(){
												insert_entity(a,i,b,0);
											}});	
										});
							        }
									// add related properties based on the
									// selected schema
							         var parent_node=$(event);
							          while(parent_node.length){
							        	  if(parent_node.hasClass('r_entity')){
							        		  // get the type of entity
							        		  var entity_type=getTypeOfEntity(parent_node,getCookie("annotationF"));
							        		  var add_property = menu.addMenu({title : 'Add as Property'});
							        		  $.each(data.types[entity_type].properties,function(i,v){
							        			  // only show atomic
													// properties
							        			  if(all_datatypes.indexOf(data.properties[v].ranges[0]) == -1){
							        				  add_property.add({title : data.properties[v].label, onclick: function(){
															insert_property(a,data.properties[v].id,b);
														}}); 
							        			  }
							        		  })
							        		  break;
							        	  }
							        	  parent_node=parent_node.parent();
							          }
							          // show/hide entities
										var browse_schema = menu.addMenu({title : 'Entities'});
										browse_schema.add({title : "Show all", onclick: function(){
											show_entities(a,'all');

										}});
										browse_schema.add({title : "Hide all", onclick: function(){
											show_entities(a,'none');
										}});
										browse_schema.add({title : "Remove all", onclick: function(){
											remove_annotations(a,0);
										}});*/
								});
		},

		/**
		 * Creates control instances based in the incomming name. This method is normally not
		 * needed since the addButton method of the tinymce.Editor class is a more easy way of adding buttons
		 * but you sometimes need to create more complex controls like listboxes, split buttons etc then this
		 * method can be used to create those.
		 *
		 * @param {String} n Name of the control to create.
		 * @param {tinymce.ControlManager} cm Control manager to use inorder to create new control.
		 * @return {tinymce.ui.Control} New control instance or null if no control was created.
		 */
		createControl : function(n, cm) {
			return null;
		},

		/**
		 * Returns information about the plugin as a name/value array.
		 * The current keys are longname, author, authorurl, infourl and version.
		 *
		 * @return {Object} Name/value array containing information about the plugin.
		 */
		getInfo : function() {
			return {
				longname : 'AnthisPlugin plugin',
				author : 'Some author',
				authorurl : 'http://tinymce.moxiecode.com',
				infourl : 'http://wiki.moxiecode.com/index.php/TinyMCE:Plugins/example',
				version : "1.0"
			};
		}
	});

	// Register plugin
	tinymce.PluginManager.add('anthisplugin', tinymce.plugins.AnthisPluginPlugin);
})();