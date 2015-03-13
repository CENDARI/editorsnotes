(function() {
	tinymce.PluginManager.requireLangPack("rdface");
	tinymce.create("tinymce.plugins.RdfacePlugin", {
		init : function(a, b) {
			toolbar:"demo",
			$.getJSON(b + '/schema_creator/selection.json', function(data) { 	// get selected schemas
				a.plugins.contextmenu.onContextMenu.add(function(th, menu, event) { // added first level schemas to context menu
					menu.removeAll(); //var add_entity = menu.addMenu({title : 'Add as Entity'}); // show only related entities	
					var parent_node = $(event);
					var has_rel = 0;
					var all_datatypes = [];
					$.each(data.types, function(i, v) {
						all_datatypes.push(v.id);
					});
					
					while (parent_node.length) {
						if (parent_node.hasClass('r_entity')) {
							has_rel = 1;
							var entity_type = getTypeOfEntity(parent_node, getCookie("annotationF"));
							$.each(data.types[entity_type].properties, function(i, v) {
								if (all_datatypes.indexOf(data.properties[v].ranges[0]) != -1) { // only show atomic properties
									//add_entity.add({title : data.properties[v].label, onclick: function(){
									menu.add({
										title : data.properties[v].label,
										onclick : function() {
											insert_entity(a, data.properties[v].ranges[0], b, data.properties[v].id);
										}
									});
								}
							});
							break;
						}
						parent_node = parent_node.parent();
					}
					parent_node = $(event);
					var del_node;
					//todo: enable deleting entities as well
					while (parent_node.length) {
						del_node = parent_node;
						if (parent_node.hasClass('r_prop') || parent_node.hasClass('r_entity')) {
							menu.add({
								title : 'Delete',
								onclick : function() {
									remove_annotation(del_node, getCookie("annotationF"));
									a.setContent(a.getContent());
								}
							});
							break;
						}
						parent_node = parent_node.parent();
					}
					if (!has_rel) {
						var others = {};
						$.each(data.types, function(i, v) {
							//	if(v.level==1){
							menu.add({
								title : v.label,
								onclick : function() {
									insert_entity(a, v.id, b, 0);
								}
							});
							//}else{
							//others[v.id] = v.label;
							//}
						});
						//more_entities = add_entity.addMenu({title : 'More...'});
						//	$.each(others,function(i,v){
						//	more_entities.add({title : v, onclick: function(){
						//		insert_entity(a,i,b,0);
						//	}});
						//	});
					}
					// add related properties based on the
					// selected schema
					var parent_node = $(event);
					while (parent_node.length) {
						if (parent_node.hasClass('r_entity')) {
							// get the type of entity
							var entity_type = getTypeOfEntity(parent_node, getCookie("annotationF"));
							var add_property = menu.addMenu({
								title : 'Add as Property'
							});
							$.each(data.types[entity_type].properties, function(i, v) {
								// only show atomic
								// properties
								if (all_datatypes.indexOf(data.properties[v].ranges[0]) == -1) {
									add_property.add({
										title : data.properties[v].label,
										onclick : function() {
											insert_property(a, data.properties[v].id, b);
										}
									});
								}
							});
							break;
						}
						parent_node = parent_node.parent();
					}
					// show/hide entities
					var browse_schema = menu.addMenu({
						title : 'All Entities'
					});
					browse_schema.add({
						title : "Show all",
						onclick : function() {
							show_entities(a, 'all');
						}
					});
					browse_schema.add({
						title : "Hide all",
						onclick : function() {
							show_entities(a, 'none');
						}
					});
					browse_schema.add({
						title : "Remove all",
						onclick : function() {
							remove_annotations(a, 0);
						}
					});
				});
			});
			a.addButton("Entities",{
				type: 'menubutton',
				title : "Entities",
				label: "Entities",
				name: "Entities",
				icon: false,
				 menu: [
                    {text: 'Show All', onclick: function() {show_entities(a, 'all');}},
                    {text: 'Hide All', onclick: function() {show_entities(a, 'none');}},
                    {text: 'Remove All', onclick: function() {remove_annotations(a, 0);}}
                ]
			});
			

			a.addButton("rdfaceHelp", {
				title : "RDFa Content Editor",
				cmd : "mceRdfaceHelp",
				image : b + "/img/rdface.png"
			});
			a.addButton("rdfaceRun", {
				title : "Automatic Content Annotation",
				cmd : "mceRdfaEnrich",
				image : b + "/img/connect.png"
			});
			a.addButton("rdfaceFacts", {
				title : "Fact Browser",
				cmd : "mceRdfaFacts",
				image : b + "/img/facts.png"
			});
			a.addButton("rdfaceSetting", {
				title : "Settings",
				cmd : "mceRdfaSetting",
				image : b + "/img/setting.png"
			});
			a.addCommand("mceRdfaEnrich", function() {
				// first we need to remove automatically
				// generated annotations
				remove_annotations(a, 1);
				activateAjaxIndicator(b);
				handleAutomaticAnnotation(a);
			});

			a.addCommand("mceRdfaFacts", function() {
				//show triple browser
				var aF = getCookie("annotationF");
				if (aF == "Microdata") {
					alert('Fact browser only works for RDFa format!');
				} else {
					//create triple browser on the fly
					if ($('#tripleBrowser').length) {
						refreshFacts();
					} else {
						//$('.mceEditor').parent().find('#tripleBrowser').remove();
						$('.mceEditor').parent().prepend('<div class="clearlooks2" style="z-index:192;width:308px; height:370px; left:420px;" id="tripleBrowser"><div class="mceWrapper mceMovable mceFocus"><div class="mceTop"><div class="mceLeft"></div><div class="mceCenter"></div><div class="mceRight"></div><span>Fact Browser</span></div><div class="mceMiddle"><div class="mceLeft"></div><span><iframe id="tripleFrame" height="345" width="300" frameborder="0" src="../jscripts/tiny_mce/plugins/rdface/facts.htm"> Your browser cannot display IFRAMEs</iframe></span><div class="mceRight"></div></div><div class="mceBottom"><div class="mceLeft"></div><div class="mceCenter"></div><div class="mceRight"></div><span>Statusbar text.</span></div><a class="mceMove" href="#"></a><a id="closeIcon" class="mceClose" href="#" onclick="$(\'#tripleBrowser\').remove();"></a></div></div>');
						$('#tripleBrowser').drags();
					}
				}

			});
			a.addCommand("mceRdfaSetting", function() {
				a.windowManager.open({
					file : b + "/setting.htm",
					width : 400 + parseInt(a.getLang("rdface.delta_width", 0)),
					height : 260 + parseInt(a.getLang("rdface.delta_height", 0)),
					inline : 1
				}, {
					plugin_url : b
				});
			});
			a.addCommand("mceRdfaceHelp", function() {
				a.windowManager.open({
					file : b + "/help.htm",
					width : 400 + parseInt(a.getLang("rdface.delta_width", 0)),
					height : 260 + parseInt(a.getLang("rdface.delta_height", 0)),
					inline : 1
				}, {
					plugin_url : b
				});
			});
			a.addCommand("editEntity", function(v1) {
				var entity_type, param;
				var aF = getCookie("annotationF");
				if (aF == "RDFa") {
					entity_type = v1.attr('typeof').split(':')[1];
					// send the content as parameter
					param = v1.find('span[property="schema:name"]').text();
				} else {
					entity_type = v1.attr('itemtype').split('http://schema.org/')[1];
					// send the content as parameter
					param = v1.find('span[itemprop="name"]').text();
				}
				var file, height, width;
				file = b + "/schema.htm";
				height = 500;
				width = 700;
				a.windowManager.open({
					file : file,
					width : width + parseInt(a.getLang("rdfa.delta_width", 0)),
					height : height + parseInt(a.getLang("rdfa.delta_height", 0)),
					inline : 1
				}, {
					plugin_url : b,
					entity_type : entity_type,
					selected_txt : param,
					annotationF : aF,
					pointer : v1
				});
			});
			a.addCommand("mceRdfaHighlight", function() {
				showTooltips(a, b);
			});
			a.onSetContent.add(function(ed, o) {
				showTooltips(a, b);
				refreshFacts();
			});
			a.onNodeChange.add(function(d, c, e) {
				showTooltips(a, b);
			});
			a.onLoadContent.add(function(ed, o) {
				//detect existing annotations
				//todo:check if they are in the scope of selected schemas or not
				var aF = getCookie("annotationF");
				adoptPrevAnnotations(ed, aF);
				showTooltips(a, b);
			});
			a.onSubmit.add(function(ed, e) {
				// remove the classes added for visualization in
				// the editor
			});
		},
		createControl : function(b, a) {
			return null;
		},
		getInfo : function() {
			return {
				longname : "RDFaCE Lite",
				author : "Ali Khalili",
				authorurl : "http://aksw.org/AliKhalili",
				infourl : "http://aksw.org/Projects/RDFaCE",
				version : "0.5"
			};
		}
	});
	tinymce.PluginManager.add("rdface", tinymce.plugins.RdfacePlugin);
})(); 
