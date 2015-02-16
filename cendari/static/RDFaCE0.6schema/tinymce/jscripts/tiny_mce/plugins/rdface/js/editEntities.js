tinyMCEPopup.requireLangPack();
var EditEntities = {
	init : function() {
		var plugin_url=tinyMCEPopup.getWindowArg('plugin_url');	
		var entity_type=tinyMCEPopup.getWindowArg('entity_type');
		var pointer=tinyMCEPopup.getWindowArg('pointer');
		//var selected_txt=tinyMCEPopup.getWindowArg('selected_txt');
		var selected_txt=pointer.html();
		var annotationF=tinyMCEPopup.getWindowArg('annotationF');
		//load schemas
		$.getJSON(plugin_url+'/schema_creator/selection.json', function(data) {
			all_schemas=data;
			$.each(data.datatypes,function(i,v){
				all_datatypes.push(i);
			})	
			$('#button_area').append('<a class="btn" onclick="EditEntities.update();"> Update </a> <a class="btn btn-danger" onclick="EditEntities.delete();"> Delete </a> '+build_changetype_box(entity_type));
			$("#schema_search_menu").keyup(function(event){
				if(event.keyCode == 13){ //when enter is pressed
					handleSearchMenuInline($("#schema_search_menu").val().trim());
				}
				var k=$("#schema_search_menu").val().trim();
				setTimeout(function() {
					handleSearchMenuInline($("#schema_search_menu").val().trim());
				}, 300);
			});				
			$('#action_area').append('<ul class="nav nav-tabs" id="schema_tabs"><li class="active"><a href="#properties" data-toggle="tab">Main</a></li></ul>');
			$('#action_area').append('<div class="tab-content" id="schema_tabs_content"><div class="tab-pane active" id="properties"></div>');
			
			//check the relationship between entity and its parent entity
			var tmp=pointer.parent();
			var e_type;
			var current_rel='';
			var rel_properties=[];
			while(tmp.length){
				if(tmp.hasClass('r_entity')){
					//console.log(tmp);
					if(annotationF=='RDFa'){
						e_type=tmp.attr('typeof');
						e_type=e_type.split(':')[1];
						current_rel=pointer.attr('property');
						if(current_rel)
							current_rel=current_rel.split(':')[1];
					}else{
						e_type=tmp.attr('itemtype');
						e_type=e_type.split('http://schema.org/')[1];
						current_rel=pointer.attr('itemprop');
					}
					$.each(all_schemas['types'][e_type]['properties'],function(i,v){
						if(all_schemas['properties'][v]['ranges'][0]==entity_type){
							rel_properties.push(all_schemas['properties'][v]['id']);
							//console.log(all_schemas['properties'][v]['label']);
						}	
					})	
					//console.log(current_rel);
					if(rel_properties.length){
						//console.log(rel_properties);
						$('#schema_tabs_content').css('height','300px');
						$('#schema_tabs_content').css('max-height','300px');
						var lis='';
						if(current_rel)
							lis='<option value="'+current_rel+'" >'+all_schemas['properties'][current_rel]['label']+'</option>';
						$.each(rel_properties,function(index,value){
							if(value!=current_rel)
								lis +='<option value="'+value+'" >'+all_schemas['properties'][value]['label']+'</option>';
						})
						lis ='<select id="rel_property">'+lis+'</select>'
						$('#action_area').append('<br/><div style="margin: 2px 0 2px 0;padding: 2px 0 0 10px;" class="alert alert-info">Relation to the parent entity: '+lis+'</div>');
					}else{
						$('#schema_tabs_content').css('height','305px');
						$('#schema_tabs_content').css('max-height','305px');
						$('#action_area').append('<br/><div class="alert alert-error">Notice: "'+entity_type+'" is not a related property of "'+e_type+'".</div>');
					}
					break;
				}
				tmp=tmp.parent();
			}
			create_form(entity_type,'','properties');
			//fillout form based on the json values coming from the annotation
			var obj;
			if(annotationF=='RDFa')
				obj=create_json_from_rdfa_annotations(pointer);
			else
				obj=create_json_from_microdata_annotations(pointer);
			//console.log(obj);
			fillout_form_from_json(obj,'','properties');
			$('#schema_tabs a[href=#properties]').tab('show');
		});		
	},
	update : function() {
	    value = '{project:' + window.parent.cendari_js_project_slug + '}';
	    trace.event("_user","edit_entity.update", "centre.rdface", value);
		var entity_type=tinyMCEPopup.getWindowArg('entity_type');
		var pointer=tinyMCEPopup.getWindowArg('pointer');
		//var selected_txt=tinyMCEPopup.getWindowArg('selected_txt');
		var selected_txt=pointer.html();
		var annotationF=tinyMCEPopup.getWindowArg('annotationF');
		//change annotation to manual
		pointer.removeClass("automatic");	
		var rel_property='';
		if($('#rel_property').length){
			rel_property=$('#rel_property').val();
		}
		//console.log(rel_property);
		var obj=create_json_from_forms('properties');
		//console.log(obj);
		if(annotationF=="RDFa"){
			create_rdfa_tags_from_json(obj,pointer)
			if(rel_property!=''){
				pointer.attr('property','schema:'+rel_property);
			}
			//entity_uri must be handled differently
			if(obj.properties.entity_uri){
				pointer.attr('resource',obj.properties.entity_uri.value)
			}
		}else{
			create_microdata_tags_from_json(obj,pointer)
			//add realtion
			if(rel_property!=''){
				pointer.attr('itemprop',rel_property);
				pointer.attr('itemscope','');
			}
			//entity_uri must be handled differently
			if(obj.properties.entity_uri){
				pointer.attr('itemid',obj.properties.entity_uri.value)
			}			
		}
		pointer.css("background-color","");
		pointer.find('.tooltip').remove();
		tinyMCEPopup.editor.nodeChanged();
		//refreshFacts();
		tinyMCEPopup.close();
	},
	delete : function() {
		console.log("deleting entity");
	    value = '{project:' + window.parent.cendari_js_project_slug + '}';
	    //trace.event("_user","delete_entity.update", "centre.rdface", value);
		var pointer=tinyMCEPopup.getWindowArg('pointer');
		//var selected_txt=tinyMCEPopup.getWindowArg('selected_txt');
		var selected_txt=pointer.html();
		var annotationF=tinyMCEPopup.getWindowArg('annotationF');
		remove_annotation(pointer,annotationF);
		pointer.find('.tooltip').remove();
		tinyMCEPopup.editor.nodeChanged();
		tinyMCEPopup.editor.setContent(tinyMCEPopup.editor.getContent());
		tinyMCEPopup.close();
	},
	changeType : function(type) {
	    value = '{project:' + window.parent.cendari_js_project_slug + '}';
	    //trace.event("_user","change_type_entity.update", "centre.rdface", value);
		var pointer=tinyMCEPopup.getWindowArg('pointer');
		var annotationF=tinyMCEPopup.getWindowArg('annotationF');
		var answer = confirm("Changing the type will remove the value of the current properties. Are you sure you want to do it?");
		if (answer) {
			//yes
			//change annotation to manual
			pointer.removeClass("automatic");		
			//var selected_txt=tinyMCEPopup.getWindowArg('selected_txt');
			var selected_txt=pointer.html();
			//remove and insert
			remove_annotation(pointer,annotationF);
			pointer.attr('class','r_entity r_'+type.toLowerCase());
			
			if(annotationF=="RDFa"){
				pointer.attr('typeof','schema:'+type);
				if(pointer.children().length==1)
					pointer.children().attr("property",'schema:name').attr('class','r_prop r_name');
			}else{
				pointer.attr('itemtype','http://schema.org/'+type);
				if(pointer.children().length==1)
					pointer.children().attr("itemprop",'name').attr('class','r_prop r_name');			
			}
			//fix for Chrome
			pointer.css("background-color","");
			pointer.find('.tooltip').remove();
			tinyMCEPopup.editor.nodeChanged();
			tinyMCEPopup.editor.setContent(tinyMCEPopup.editor.getContent());
			tinyMCEPopup.close();
		} else {
			return 0;// no
		}
	}
};

// console.log(window.parent.cendari_js_project_slug);

tinyMCEPopup.onInit.add(EditEntities.init, EditEntities);
