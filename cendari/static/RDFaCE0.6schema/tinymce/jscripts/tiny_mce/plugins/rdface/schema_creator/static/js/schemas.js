function showmore_schemas(){
	$('#more_schemas_btn').remove();
	$('.schema_hidden').show();
	$('#schema_search_menu').show();
}
function handleSearchMenu(term){
    $('#schema_menu .seond-level').each(function(i, element){
    	var str=$(element).text();
    	str=str.toLowerCase();
	    	var n=str.search(term.toLowerCase());
	    	if (n!=-1)
	    		$(element).addClass('found_node_menu');
	    	else
	    		$(element).css('display','none');
    });
    if(term==''){
    	$('#schema_menu .seond-level').css('display','');
    	$('.schema_hidden').show();
    }
}
function handleSearchMenuInline(term){
    $('#changetype_menu .seond-level').each(function(i, element){
    	var str=$(element).text();
    	str=str.toLowerCase();
	    	var n=str.search(term.toLowerCase());
	    	if (n!=-1)
	    		$(element).addClass('found_node_menu');
	    	else
	    		$(element).css('display','none');
    });
    if(term==''){
    	$('#changetype_menu .seond-level').css('display','');
    	$('.schema_hidden').show();
    }
}
function load_schemas(){
	var secondlevles=new Array();
	$.getJSON('selection.json', function(data) {
		all_schemas=data;
		$.each(data.types,function(i,v){
			if(v.level==1)
				$('#schema_menu').append('<li><a onclick="initiate_form(\''+v.id+'\')" tabindex="-1" href="#'+v.id+'" title="'+v.comment_plain+'">'+v.label+'</a></li>');
			else
				secondlevles.push('<li class="seond-level schema_hidden"><a onclick="initiate_form(\''+v.id+'\')" tabindex="-1" href="#'+v.id+'" title="'+v.comment_plain+'">'+v.label+'</a></li>');
		});
		$.each(data.datatypes,function(i,v){
			all_datatypes.push(i);
		});		
		$('#schema_menu').append('<li class="divider"></li>');
		$('#schema_menu').append('<li id="more_schemas_btn"><a tabindex="-1" onclick="showmore_schemas()" class="hand-pointer">More...</a></li>');
		$('#schema_menu').append('<li><a tabindex="-1"><input id="schema_search_menu" type="text" class="input span2 search-query" placeholder="Search for Schema" style="display:none;"></a></li>');
		$.each(secondlevles,function(i,v){
			$('#schema_menu').append(v);
		});	
		$('.dropdown-menu').show();
		$("#schema_search_menu").keyup(function(event){
			
			if(event.keyCode == 13){ // when enter is pressed
				handleSearchMenu($("#schema_search_menu").val().trim());
			}
			
			var k=$("#schema_search_menu").val().trim();
			setTimeout(function() {
				handleSearchMenu($("#schema_search_menu").val().trim());
			}, 300);
		});	
	});	
}
function initiate_form(schema){
	$('#page_header').hide();
	$('#schema_dropdown').hide();
	$('#action_area').append('<div id="second_page_btns"><center><a href="#types" class="btn" onclick="show_schemas();"> Back </a> <a class="btn btn-success" onclick="submit_schema_form();"> Insert </a></center></div>');	
	$('.nav-tabs').remove();
	$('.tab-content').remove();
	$('#action_area').append('<ul class="nav nav-tabs" id="schema_tabs"><li class="active"><a href="#properties" data-toggle="tab">Main</a></li></ul>');
	$('#action_area').append('<div class="tab-content" id="schema_tabs_content"><div class="tab-pane active" id="properties"></div>');
	create_form(schema,'','properties');
}
function create_form(schema,property,container){
	console.log("schema = " + schema);
	var tmp='';
	var selected=all_schemas.types[schema];
	var id;
	// if it is the main schema
	if(property==''){
		id=schema;
	}else{
		id=schema+'_'+property;
	}
	$('#'+container).append('<div id="schema_form_'+id+'"></div>');
	$('#schema_form_'+id).append('<h4><a href="'+selected.url+'" target="_blank">'+selected.label+'</a></h4><small id="schema_description" class="muted">-- '+selected.comment+'</small>');
	$('#schema_form_'+id).append('<form class="form-vertical well well-small" id="form_'+id+'"></form>');
	// add URI field for entity
	if(property==''){
		tmp='<div class="control-group">';
		tmp=tmp+'<label class="control-label" for="entity_freebase">Start typing the entity name to get suggestions from Wikipedia: </label>';
		tmp=tmp+'<div class="controls">';
		tmp=tmp+'<input type="text" id="entity_freebase" placeholder="Wikipedia name of the entity">';
		tmp=tmp+'<span class="add-on subschema-icon" onclick="form_suggestURI()" title="Search for Name"><i class="icon-search"></i></span>';
		tmp=tmp+'</div>';
		tmp=tmp+'</div>';
		$('#form_'+id).append(tmp);
		// freebase is no longer supported, here it is replaced with jQuery autocomplete 
		//FBSuggest(schema);
		// var dummyList = [
               	//	"a",
		//	"ab",
               	//	"b",
		//	"c",
		//	"cd",
		//	"d"
            	//]; 
		//Getting data from dummy list
		//$( "#entity_freebase" ).autocomplete({
  		//	source: dummyList,	
		//	minLength: 1,		 
		//	select: function( event, ui ) {
        	//		console.log( ui.item ?
          	//		"Selected: " + ui.item.value + " aka " + ui.item.id :
          	//		"Nothing selected, input was " + this.value );
      		//	}
		//});


		//Getting data from Geonames webservice
	   	//$( "#entity_freebase" ).autocomplete({
		//     	source: function( request, response ) {
		//		$.ajax({
		//	  		url: "http://gd.geobytes.com/AutoCompleteCity",
		//	  		dataType: "jsonp",
		//	  		data: {
		//	    			q: request.term
		//	  		},
		//	  		success: function( data ) {
		//	    			response( data );
		//	  		}
		//		});
		//      	},
		//      	minLength: 3,
		//      	select: function( event, ui ) {
		//		console.log( ui.item ?
		//	  		"Selected: " + ui.item.label :
		//	  		"Nothing selected, input was " + this.value);
		//      	},
		//      	open: function() {
		//		$( this ).removeClass( "ui-corner-all" ).addClass( "ui-corner-top" );
		//      	},
		//      	close: function() {
		//		$( this ).removeClass( "ui-corner-top" ).addClass( "ui-corner-all" );
		//      	}
	    	//});

		//Getting data from ElasticSearch
		$("#entity_freebase").autocomplete({
			source: function(request, response) {
				//Add accent folding later
				//query = {"query":{"match_all":{}}}
				if(schema='Thing'){
					query = 
					{
					    "from" : 0, "size" : 15,
					    "query": {
						"query_string": {
						    "query": request.term.toLowerCase()
						}
					    }
					}
				}else{
					query = 
					{
					    "from" : 0, "size" : 15,
					    "query": {
						"query_string": {
						    "query": request.term.toLowerCase()
						}
					    },
					    "filter": {
						"term": { "class": "http://schema.org/"+schema }
					    }
					}
				}

				$.ajax({
				    url: "http://localhost:9200/_search",
				    type: "POST",
				    dataType: "JSON",
				    data: JSON.stringify(query),
				    success: function(data) {
					//console.log("sent data= " + JSON.stringify(data));
				        response($.map(data.hits.hits, function(item) {
						title = JSON.stringify(item._source["title"])
						suggestion_title = title.substring(1, title.length-1)
						suggestion_id = item._source["uri"]
				            	return {
				                	label: suggestion_title,
				                	id: suggestion_id
				            	}
				        }));
				    },
				});
			},
		    	minLength: 2,
		      	select: function( event, ui ) {
				console.log( ui.item ?
			  		"Selected: " + ui.item.label :
			  		"Nothing selected, input was " + this.value);
		      	},
			focus: function( event, ui ) {
				console.log( ui.item ?
			  		"Hovered over: " + ui.item.label :
			  		"Nothing hovered over, input was " + this.value);
		      	},

		});		
		$('#entity_freebase').mouseover(function() {
			   $('#entity_freebase').tooltip({
			        placement : 'right',
			        title : 'resolvable URI of the entity'
			    });
		});
		tmp='<div class="control-group">';
		tmp=tmp+'<label class="control-label" for="entity_uri">Entity URI</label>';
		tmp=tmp+'<div class="controls">';
		tmp=tmp+'<input type="text" id="entity_uri" placeholder="URI of the entity">';
		tmp=tmp+'</div>';
		tmp=tmp+'</div>';
		$('#form_'+id).append(tmp);
	}
	// create form fields
	$.each(selected.properties, function(i,v){
			if(property==''){
				build_form_element(selected.id,v,'form_'+id,1);
			}else{
				build_form_element(property,v,'form_'+id,0);
			}
	});
	// end form
	$('#schema_form_'+id).linkify();
}
function show_schemas(){
	$('#second_page_btns').remove();
	$('#schema_tabs').remove();
	$('#schema_tabs_content').remove();
	$('#page_header').show();
	$('#schema_dropdown').show();	
}
function build_form_element(schema,property,container,is_initial){	
	var output='';
	output=output+'<div class="control-group">';
	output=output+'<label class="control-label" for="'+schema+'_'+property+'">'+all_schemas.properties[property].label+'</label>';
	output=output+'<div class="controls">';
	
	var selected=all_schemas.properties[property];
	if(property=='description'){
		output=output+'<textarea rows="2" id="'+schema+'_'+property+'" placeholder="'+property+'"></textarea>';
		$('#'+container).append(output);
		make_tooltip(schema,property);
		return 0;
	}
	// considers only one range for now
	var range=selected.ranges[0];
	switch(range){
	case 'Boolean':
		output=output+'<select id="'+schema+'_'+property+'"><option value=""></option><option value="True">True</option><option value="False">False</option></select>';
		$('#'+container).append(output);
		make_tooltip(schema,property);
		return 0;
		break;	
	case 'DateTime':
		output=output+'<div class="input-append date" id="datetimepicker_'+schema+'_'+property+'" data-date-format="yyyy-mm-dd hh:ii"><input size="16" type="text" id="'+schema+'_'+property+'"><span class="add-on"><i class="icon-th"></i></span></div>';
		$('#'+container).append(output);
		$('#datetimepicker_'+schema+'_'+property).datetimepicker();
		make_tooltip(schema,property);
		return 0;
		break;
	case 'Date':
		var nowTemp = new Date();
		var now=nowTemp.getFullYear()+'-'+nowTemp.getMonth()+'-'+nowTemp.getDate();
		output=output+'<div class="input-append date" id="datepicker_'+schema+'_'+property+'" data-date="'+now+'" data-date-format="yyyy-mm-dd"><input size="16" type="text" id="'+schema+'_'+property+'"><span class="add-on"><i class="icon-th"></i></span></div>';
		$('#'+container).append(output);
		$('#datepicker_'+schema+'_'+property).datepicker();
		make_tooltip(schema,property);
		return 0;
		break;		
	default:
		output=output+'<input type="text" id="'+schema+'_'+property+'" placeholder="'+property+'">';	
	}
	if(all_datatypes.indexOf(range) != -1){ 
	}else{
		if(is_initial)
			output=output+'<span class="add-on subschema-icon" onclick="add_sub_schema(\''+property+'\',\''+range+'\')" title="Add details"><a href="#schema_tabs"><i class="icon-plus"></i></a></span>';
		else
			output=output+'<span class="add-on subschema-icon" onclick="add_sub_schema(\''+schema+'_'+property+'\',\''+range+'\')" title="Add details"><a href="#schema_tabs"><i class="icon-plus"></i></a></span>';
	}
	$('#'+container).append(output);
	make_tooltip(schema,property);
}
function is_composite_property(prop){
	if(all_datatypes.indexOf(all_schemas['properties'][prop]['ranges'][0]) != -1){ 
		return 0;
	}else{
		return 1;
	}
}
function make_tooltip(schema,property){
	$('#'+schema+'_'+property).mouseover(function() {
		   $('#'+schema+'_'+property).tooltip({
		        placement : 'right',
		        title : all_schemas.properties[property].comment_plain
		    });
	});	
}
function build_changetype_box(current_type){
	var secondlevles=new Array();
	var output='<div id="changetype_menu" class="btn-group"><button class="btn dropdown-toggle btn-inverse" data-toggle="dropdown">'+current_type+' <span class="caret"></span> </button><ul class="dropdown-menu" style="text-align:left;">';
	// create list of schema types
	$.each(all_schemas.types,function(i,v){
		if(v.level==1 && v.id!=current_type)
			output=output+'<li><a onclick="EditEntities.changeType(\''+v.id+'\')" tabindex="-1" href="#'+v.id+'" title="'+v.comment_plain+'">'+v.label+'</a></li>';
		else
			secondlevles.push('<li class="seond-level schema_hidden"><a onclick="EditEntities.changeType(\''+v.id+'\')" tabindex="-1" href="#'+v.id+'" title="'+v.comment_plain+'">'+v.label+'</a></li>');
	});
	output=output+'<li class="divider"></li>';
	output=output+'<li id="more_schemas_btn"><a tabindex="-1" onclick="event.stopPropagation();showmore_schemas();" class="hand-pointer">More...</li>';
	output=output+'<li><a tabindex="-1" onclick="event.stopPropagation();"><input id="schema_search_menu" type="text" class="input span2 search-query" placeholder="Search for Schema" style="display:none;"></a></li>';
	$.each(secondlevles,function(i,v){
		output=output+v;
	});
	output=output+'</ul></div>';
	return output;
}

function FBSuggest(entity_type) {
    var fb = Schema2Frebase[entity_type];

    if (fb) {
	$("#entity_freebase")
	    .suggest({filter: '(all type:'+fb+')',
		      key: 'AIzaSyD4Zfuwj7btEkqSPAK_Flq1nqvKr9lDN4U'})
	.bind("fb-select", function(e, data) {
	    console.log('fb-select: '+data.name+', '+data.id);
	    $('#entity_uri').val('http://rdf.freebase.com'+data.mid);
	})
	.bind("fb-select-new", function(e, val) {
	    console.log('fb-select-new: '+val);
	});
    } 
}
function form_suggestURI(){
	var term=$('#entity_freebase').val().trim();
	var str=term.toLowerCase();
	var n1=str.search('http://');
	var n2=str.search('www.');
	if (n1==-1 && term!=''){
		if(n2==-1){
			$('#entity_freebase').val(suggestURI(proxy_url,"api=Sindice&query="+term,true));
		}else{
			alert('Please type a keyword to search');
		}
	}else{
		alert('Please type a keyword to search');
	}
	
}
function add_sub_schema(s,range){
	if(!$('#tab_'+s).length){
		$('#schema_tabs').append('<li><a href="#tab_'+s+'" data-toggle="tab"> <button class="close" type="button" onclick="remove_schema_tab(\''+s+'\')">&times;</button> '+s+'</a></li>');
		$('#schema_tabs_content').append('<div class="tab-pane" id="tab_'+s+'"></div>');
		create_form(range,s,'tab_'+s);
	}
	$('#schema_tabs a[href=#tab_'+s+']').tab('show');
	$("#schema_tabs_content").animate({ scrollTop: 0 }, "fast");
}
function add_repeated_sub_schema(instances,s,range,is_composite){
	if(!$('#tab_'+s).length){
		$('#schema_tabs').append('<li><a href="#tab_'+s+'" data-toggle="tab"> <button class="close" type="button" onclick="remove_schema_tab(\''+s+'\')">&times;</button> '+s+'</a></li>');
		$('#schema_tabs_content').append('<div class="tab-pane" id="tab_'+s+'"></div>');
		$("#tab_"+s).append('<ul class="nav nav-tabs" id="schema_tabs_'+s+'"></ul>');
		$("#tab_"+s).append('<div class="tab-content" id="schema_tabs_content_'+s+'"></div>');
		if(is_composite){
			for (var i=0;i<instances.length;i++)
			{
				if(i==0){
					$("#schema_tabs_"+s).append('<li class="active"><a href="#tab_'+s+'_'+i+'" data-toggle="tab"> <button class="close" type="button" onclick="remove_repeated_schema_tab(\''+s+'\',\''+s+'_'+i+'\')">&times;</button> Value '+i+'</a></li>');
					$('#schema_tabs_content_'+s).append('<div class="tab-pane active" id="tab_'+s+'_'+i+'"></div>');
				}else{
					$("#schema_tabs_"+s).append('<li><a href="#tab_'+s+'_'+i+'" data-toggle="tab"> <button class="close" type="button" onclick="remove_repeated_schema_tab(\''+s+'\',\''+s+'_'+i+'\')">&times;</button> Value '+i+'</a></li>');
					$('#schema_tabs_content_'+s).append('<div class="tab-pane" id="tab_'+s+'_'+i+'"></div>');
				}	
				create_form(range,s+'_'+i,'tab_'+s+'_'+i);
				fillout_form_from_json(instances[i].value,s+'_'+i,'schema_form_'+s+'_'+i);
			}		
		}else{
			for (var i=0;i<instances.length;i++)
			{
				if(i==0){
					$("#schema_tabs_"+s).append('<li class="active"><a href="#tab_'+s+'_'+i+'" data-toggle="tab"> <button class="close" type="button" onclick="remove_repeated_schema_tab(\''+s+'\',\''+s+'_'+i+'\')">&times;</button> Value '+i+'</a></li>');
					$('#schema_tabs_content_'+s).append('<div class="tab-pane active" id="tab_'+s+'_'+i+'"></div>');
				}else{
					$("#schema_tabs_"+s).append('<li><a href="#tab_'+s+'_'+i+'" data-toggle="tab"> <button class="close" type="button" onclick="remove_repeated_schema_tab(\''+s+'\',\''+s+'_'+i+'\')">&times;</button> Value '+i+'</a></li>');
					$('#schema_tabs_content_'+s).append('<div class="tab-pane" id="tab_'+s+'_'+i+'"></div>');
				}	
				// todo: create appropriate form input
				// now we simplify it to a simple text box
				$('#tab_'+s+'_'+i).append('<input type="text" id="'+s+'_'+i+'" value="'+instances[i].value+'">');	
			}
		}
		
	}
}
function show_repeated_tab(s,is_composite){
	if(!$('#tab_'+s).length){
		alert('You have closed the related tab! Please close this window and click on the entity again!');
		//todo:add and fillout the schema tab again
	}else{
		$('#schema_tabs a[href=#tab_'+s+']').tab('show');
		$("#schema_tabs_content").animate({ scrollTop: 0 }, "fast");
	}
}
function remove_schema_tab(s){
	$('#schema_tabs a[href=#tab_'+s+']').parent().remove();
	$('#tab_'+s).remove();
	$('#schema_tabs a[href=#properties]').tab('show');
}
function remove_repeated_schema_tab(parent_tab,s){
	$('#schema_tabs_'+parent_tab+' a[href=#tab_'+s+']').parent().remove();
	$('#tab_'+s).remove();
	if(!$('#schema_tabs_content_'+parent_tab).find('.tab-pane').length){
		$('#schema_tabs a[href=#tab_'+parent_tab+']').parent().remove();
		$('#tab_'+parent_tab).remove();	
		$('#schema_tabs a[href=#properties]').tab('show');
	}else{
		$('#schema_tabs_'+parent_tab).tab('show');
	}
	
}
function submit_schema_form(){
	console.log(create_json_from_forms('properties'));
}
function create_json_from_forms(container){
	var output = {};
	var jsonObj = {};
	var div_name=$('#'+container).children().attr('id');
	var tmp=div_name.split("_");
	var schema=tmp[2];
	var property=tmp[(tmp.length)-1];
	var input_prefix='';
	var tab_prefix='';
	// main tab
	if(schema==property){
		input_prefix=schema;
		tab_prefix='tab_';
	}else{
		var tmp2=div_name.split("schema_form_"+schema+"_");
		input_prefix=tmp2[1];
		tab_prefix='tab_'+input_prefix+'_';
	}
	var selected=all_schemas.types[schema];
	var input_val;
	output['type']=schema;
	// check for entity URI manually
	if($('#'+container+' #entity_uri').length){
		var tmp=$('#'+container+' #entity_uri').val().trim();
		if(tmp!=''){
			// only for the main entity
			jsonObj['entity_uri']=({value:tmp,is_composite:0,is_repeated:0});
		}
	}
	// check existing form elements
	$.each(selected.properties,function(i,v){
		input_val=$('#'+container+' #'+input_prefix+'_'+v).val().trim();
		// simple properties
		if(input_val!='' && input_val!='Multiple values'){
			jsonObj[v]=({value:input_val,is_composite:0, is_repeated:0});
		}else{
			// repeated and composite properties
			if($('#'+tab_prefix+v).length){
				// check if it is composite or repeated
				var tmp2=tab_prefix.split('tab_')[1];
				if($('#schema_tabs_'+tmp2+v).length){
					var is_composite_prop=is_composite_property(v);
					jsonObj[v]=({is_composite:is_composite_prop, is_repeated:1});
					jsonObj[v]['instances']=[];
					// is repeated check maximum 50 repeated tabs
					for (var j=0;j<50;j++){
						if($('#tab_'+tmp2+v+'_'+j).length){
							if(is_composite_prop)
								jsonObj[v]['instances'][j]=({value:create_json_from_forms('tab_'+tmp2+v+'_'+j)});
							else
								jsonObj[v]['instances'][j]=({value:$('#tab_'+tmp2+v+'_'+j+' #'+tmp2+v+'_'+j).val().trim()});
						}else{
							break;
						}
					}
				}else{
					jsonObj[v]=({value:create_json_from_forms(tab_prefix+v), is_composite:1, is_repeated:0});
				}
				
			}
		}
	})
		output['properties']=jsonObj;
		return output;
}
function create_json_from_rdfa_annotations(pointer){
	var output = {};
	var jsonObj = {};
	var tmp=pointer.attr('typeof');
	tmp=tmp.split(':')[1];
	output['type']=tmp;
	$.each(pointer.children(),function(i,v){
		if($(v).attr('typeof') && $(v).attr('property')){
			// composite property
			tmp=$(v).attr('property');
			tmp=tmp.split(':')[1];
			if(jsonObj[tmp]){
				if(!jsonObj[tmp]['instances']){
					jsonObj[tmp]['instances']=[];
					jsonObj[tmp].is_composite=1;
					jsonObj[tmp].is_repeated=1;
					jsonObj[tmp]['instances'][0]=({value:jsonObj[tmp].value});
					delete jsonObj[tmp].value;
				}
				var tmp2=jsonObj[tmp]['instances'].length;
				jsonObj[tmp]['instances'][tmp2]=({value:create_json_from_rdfa_annotations($(v))});
			}else{
				jsonObj[tmp]=({value:create_json_from_rdfa_annotations($(v)), is_composite:1,is_repeated:0});
			}
		}
		// property with visible value
		if($(v).hasClass('r_prop') && $(v).attr('property')){
			tmp=$(v).attr('property');
			tmp=tmp.split(':')[1];
			if(jsonObj[tmp]){
				if(!jsonObj[tmp]['instances']){
					jsonObj[tmp]['instances']=[];
					jsonObj[tmp].is_composite=0;
					jsonObj[tmp].is_repeated=1;
					jsonObj[tmp]['instances'][0]=({value:jsonObj[tmp].value});
					delete jsonObj[tmp].value;
				}
				var tmp2=jsonObj[tmp]['instances'].length;
				jsonObj[tmp]['instances'][tmp2]=({value:$(v).html()});
			}else{
				jsonObj[tmp]=({value:$(v).html(),is_composite:0,is_repeated:0});
			}
		}	
		// property with invisible value
		if(($(v).prop("tagName").toLowerCase()=='meta') && $(v).attr('property')){
			tmp=$(v).attr('property');
			tmp=tmp.split(':')[1];
			if(jsonObj[tmp]){
				if(!jsonObj[tmp]['instances']){
					jsonObj[tmp]['instances']=[];
					jsonObj[tmp].is_composite=0;
					jsonObj[tmp].is_repeated=1;
					jsonObj[tmp]['instances'][0]=({value:jsonObj[tmp].value});
					delete jsonObj[tmp].value;
				}
				var tmp2=jsonObj[tmp]['instances'].length;
				jsonObj[tmp]['instances'][tmp2]=({value:$(v).attr('content')});
			}else{
				jsonObj[tmp]=({value:$(v).attr('content'),is_composite:0,is_repeated:0});
			}
		}	
	});
	// entity uri
	if(pointer.attr('resource')){
		jsonObj['entity_uri']=({value:pointer.attr('resource'),is_composite:0,is_repeated:0});
	}
	output['properties']=jsonObj;
	return output;
}
function create_json_from_microdata_annotations(pointer){
	var output = {};
	var jsonObj = {};
	var tmp=pointer.attr('itemtype');
	tmp=tmp.split('\/');
	output['type']=tmp[tmp.length-1];
	$.each(pointer.children(),function(i,v){
		if($(v).attr('itemtype') && $(v).attr('itemprop')){
			// composite property
			tmp=$(v).attr('itemprop');
			if(jsonObj[tmp]){
				if(!jsonObj[tmp]['instances']){
					jsonObj[tmp]['instances']=[];
					jsonObj[tmp].is_composite=1;
					jsonObj[tmp].is_repeated=1;
					jsonObj[tmp]['instances'][0]=({value:jsonObj[tmp].value});
					delete jsonObj[tmp].value;
				}
				var tmp2=jsonObj[tmp]['instances'].length;
				jsonObj[tmp]['instances'][tmp2]=({value:create_json_from_microdata_annotations($(v))});
			}else{
				jsonObj[tmp]=({value:create_json_from_microdata_annotations($(v)), is_composite:1,is_repeated:0});
			}
		}
		// property with visible value
		if($(v).hasClass('r_prop') && $(v).attr('itemprop')){
			tmp=$(v).attr('itemprop');
			if(jsonObj[tmp]){
				if(!jsonObj[tmp]['instances']){
					jsonObj[tmp]['instances']=[];
					jsonObj[tmp].is_composite=0;
					jsonObj[tmp].is_repeated=1;
					jsonObj[tmp]['instances'][0]=({value:jsonObj[tmp].value});
					delete jsonObj[tmp].value;
				}
				var tmp2=jsonObj[tmp]['instances'].length;
				jsonObj[tmp]['instances'][tmp2]=({value:$(v).html()});
			}else{
				jsonObj[tmp]=({value:$(v).html(),is_composite:0,is_repeated:0});
			}
		}	
		// property with invisible value
		if(($(v).prop("tagName").toLowerCase()=='meta') && $(v).attr('itemprop')){
			tmp=$(v).attr('itemprop');
			if(jsonObj[tmp]){
				if(!jsonObj[tmp]['instances']){
					jsonObj[tmp]['instances']=[];
					jsonObj[tmp].is_composite=0;
					jsonObj[tmp].is_repeated=1;
					jsonObj[tmp]['instances'][0]=({value:jsonObj[tmp].value});
					delete jsonObj[tmp].value;
				}
				var tmp2=jsonObj[tmp]['instances'].length;
				jsonObj[tmp]['instances'][tmp1]=({value:$(v).attr('content')});
			}else{
				jsonObj[tmp]=({value:$(v).attr('content'),is_composite:0,is_repeated:0});
			}
		}	
	});
	// entity uri
	if(pointer.attr('itemid')){
		jsonObj['entity_uri']=({value:pointer.attr('itemid'),is_composite:0,is_repeated:0});
	}
	output['properties']=jsonObj;
	return output;
}
function create_rdfa_tags_from_json(obj,pointer){
	$.each(obj.properties,function(i,v){
	if(i!='entity_uri'){
		if(pointer.find('>[property="schema:'+i+'"]').length){
			// we need to update exisiting tags
			if(v.is_repeated){
				// repeated
				if(v.is_composite){
					$.each(pointer.find('>[property="schema:'+i+'"]'),function(ii,vv){
						create_rdfa_tags_from_json(v.instances[ii].value,$(vv));				
					});	
				}else{
					$.each(pointer.find('>[property="schema:'+i+'"]'),function(ii,vv){
						var tagName=$(vv).prop("tagName").toLowerCase();
						if(tagName=='meta'){
							$(vv).attr('content',v.instances[ii].value);
						}else{
							$(vv).html(v.instances[ii].value);
						}				
					});
				}
			}else{
				// single instance
				if(v.is_composite){
					create_rdfa_tags_from_json(v.value,pointer.find('>[property="schema:'+i+'"]'));
				}else{
					var tagName=pointer.find('>[property="schema:'+i+'"]').prop("tagName").toLowerCase();
					if(tagName=='meta'){
						pointer.find('>[property="schema:'+i+'"]').attr('content',v.value);
					}else{
						pointer.find('>[property="schema:'+i+'"]').html(v.value);
					}
				}
			}
		}else{
			// we need to create meta tags
			if(v.is_repeated){
				if(v.is_composite){
					$.each(v.instances,function(ii,vv){
						pointer.append('<span id="inst_'+i+'_'+ii+'" property="schema:'+i+'" typeof="schema:'+v.instances[0].value.type+'"></span>');
						create_rdfa_tags_from_json(vv.value,pointer.find("#inst_'+i+'_'+ii+'"));
					})
				}else{
					$.each(v.instances,function(ii,vv){
						pointer.append('<meta property="schema:'+i+'" content="'+vv.value+'" />');
					})
				}
			}else{
				if(v.is_composite){
					pointer.append('<span property="schema:'+i+'" typeof="schema:'+v.value.type+'"></span>');
					create_rdfa_tags_from_json(v.value,pointer.find('[property="schema:'+i+'"]'));
				}else{
					pointer.append('<meta property="schema:'+i+'" content="'+v.value+'" />');
				}
			}
			
		}
	}
	})
}
function create_microdata_tags_from_json(obj,pointer){
	$.each(obj.properties,function(i,v){
	if(i!='entity_uri'){
		if(pointer.find('>[itemprop="'+i+'"]').length){
			// we need to update exisiting tags
			if(v.is_repeated){
				// repeated
				if(v.is_composite){
					$.each(pointer.find('>[itemprop="'+i+'"]'),function(ii,vv){
						create_microdata_tags_from_json(v.instances[ii].value,$(vv));				
					});	
				}else{
					$.each(pointer.find('>[itemprop="'+i+'"]'),function(ii,vv){
						var tagName=$(vv).prop("tagName").toLowerCase();
						if(tagName=='meta'){
							$(vv).attr('content',v.instances[ii].value);
						}else{
							$(vv).html(v.instances[ii].value);
						}				
					});
				}
			}else{
				// single instance
				if(v.is_composite){
					create_microdata_tags_from_json(v.value,pointer.find('>[itemprop="'+i+'"]'));
				}else{
					var tagName=pointer.find('>[itemprop="'+i+'"]').prop("tagName").toLowerCase();
					if(tagName=='meta'){
						pointer.find('>[itemprop="'+i+'"]').attr('content',v.value);
					}else{
						pointer.find('>[itemprop="'+i+'"]').html(v.value);
					}
				}
			}
		}else{
			// we need to create meta tags
			if(v.is_repeated){
				if(v.is_composite){
					$.each(v.instances,function(ii,vv){
						pointer.append('<span id="inst_'+i+'_'+ii+'" itemscope itemprop="'+i+'" itemtype="http://schema.org/'+v.instances[0].value.type+'"></span>');
						create_microdata_tags_from_json(vv.value,pointer.find("#inst_'+i+'_'+ii+'"));
					})
				}else{
					$.each(v.instances,function(ii,vv){
						pointer.append('<meta itemprop="'+i+'" content="'+vv.value+'" />');
					})
				}
			}else{
				if(v.is_composite){
					pointer.append('<span itemprop="'+i+'" itemscope itemtype="http://schema.org/'+v.value.type+'"></span>');
					create_microdata_tags_from_json(v.value,pointer.find('[itemprop="'+i+'"]'));
				}else{
					pointer.append('<meta itemprop="'+i+'" content="'+v.value+'" />');
				}
			}
			
		}
	}	
	})
}
function fillout_form_from_json(obj,property,form_container){
	// console.log(obj);
	var tmp;
        //if (obj.properties.name != null) {
	//    $('#entity_freebase').val(obj.properties.name.value);
	//}
	$.each(obj.properties,function(i,v){
		if(v.is_repeated){
			// number of instances
			if(v.is_composite){
				if(form_container=='properties'){
					$('#'+form_container+' #'+obj.type+'_'+i).parent().parent().addClass('info');
					$('#'+form_container+' #'+obj.type+'_'+i).next().remove();
					$('#'+form_container+' #'+obj.type+'_'+i).after('<span class="add-on subschema-icon" title="See multiple values" onclick="show_repeated_tab(\''+i+'\',1);"><a href="#schema_tabs"><i class="icon-book"></i></a></span>');
					$('#'+form_container+' #'+obj.type+'_'+i).prop('disabled', true);
					$('#'+form_container+' #'+obj.type+'_'+i).val('Multiple values');	
					add_repeated_sub_schema(v.instances,i,v.instances[0].value.type,1);
				}else{
					tmp=form_container.split('schema_form_'+obj.type+'_');
					tmp=tmp[1];	
					if(!tmp){
						// it is a repeated tab
						var tmp2=form_container.split('schema_form_')[1];
						$('#schema_form_'+obj.type+'_'+tmp2+' #'+tmp2+'_'+i).parent().parent().addClass('info');
						$('#schema_form_'+obj.type+'_'+tmp2+' #'+tmp2+'_'+i).next().remove();
						$('#schema_form_'+obj.type+'_'+tmp2+' #'+tmp2+'_'+i).after('<span class="add-on subschema-icon" title="See multiple values" onclick="show_repeated_tab(\''+property+'_'+i+'\',1);"><a href="#schema_tabs"><i class="icon-book"></i></a></span>');
						$('#schema_form_'+obj.type+'_'+tmp2+' #'+tmp2+'_'+i).prop('disabled', true);
						$('#schema_form_'+obj.type+'_'+tmp2+' #'+tmp2+'_'+i).val('Multiple values');
					}else{
						$('#'+form_container+' #'+tmp+'_'+i).parent().parent().addClass('info');
						$('#'+form_container+' #'+tmp+'_'+i).next().remove();
						$('#'+form_container+' #'+tmp+'_'+i).after('<span class="add-on subschema-icon" title="See multiple values" onclick="show_repeated_tab(\''+property+'_'+i+'\',1);"><a href="#schema_tabs"><i class="icon-book"></i></a></span>');
						$('#'+form_container+' #'+tmp+'_'+i).prop('disabled', true);
						$('#'+form_container+' #'+tmp+'_'+i).val('Multiple values');
					}
					add_repeated_sub_schema(v.instances,property+'_'+i,v.instances[0].value.type,1);
				}
			}else{
				if(i=='entity_uri'){
					$('#properties #entity_uri').val(v.value);
					// $('#'+form_container+'
					// #entity_uri').parent().parent().addClass('info');
				}else{
					if(form_container=='properties'){
						$('#'+form_container+' #'+obj.type+'_'+i).parent().parent().addClass('info');
						$('#'+form_container+' #'+obj.type+'_'+i).after('<span class="add-on subschema-icon" title="See multiple values" onclick="show_repeated_tab(\''+i+'\',0);"><a href="#schema_tabs"><i class="icon-book"></i></a></span>');
						$('#'+form_container+' #'+obj.type+'_'+i).prop('disabled', true);
						$('#'+form_container+' #'+obj.type+'_'+i).val('Multiple values');
						add_repeated_sub_schema(v.instances,i,all_schemas.properties[i].ranges[0],0);
					}else{
						tmp=form_container.split('schema_form_'+obj.type+'_');
						tmp=tmp[1];	
						if(!tmp){
							// it is a repeated tab
							var tmp2=form_container.split('schema_form_')[1];
							$('#schema_form_'+obj.type+'_'+tmp2+' #'+tmp2+'_'+i).parent().parent().addClass('info');
							$('#schema_form_'+obj.type+'_'+tmp2+' #'+tmp2+'_'+i).after('<span class="add-on subschema-icon" title="See multiple values" onclick="show_repeated_tab(\''+property+'_'+i+'\',0);"><a href="#schema_tabs"><i class="icon-book"></i></a></span>');
							$('#schema_form_'+obj.type+'_'+tmp2+' #'+tmp2+'_'+i).prop('disabled', true);
							$('#schema_form_'+obj.type+'_'+tmp2+' #'+tmp2+'_'+i).val('Multiple values');

						}else{
							$('#'+form_container+' #'+tmp+'_'+i).parent().parent().addClass('info');
							$('#'+form_container+' #'+tmp+'_'+i).after('<span class="add-on subschema-icon" title="See multiple values" onclick="show_repeated_tab(\''+property+'_'+i+'\',0);"><a href="#schema_tabs"><i class="icon-book"></i></a></span>');
							$('#'+form_container+' #'+tmp+'_'+i).prop('disabled', true);
							$('#'+form_container+' #'+tmp+'_'+i).val('Multiple values');
						}						

						add_repeated_sub_schema(v.instances,property+'_'+i,all_schemas.properties[i].ranges[0],0);
					}
					// $('#'+form_container+'
					// #'+obj.type+'_'+i).parent().parent().addClass('success');
				}
			}		
		}else{
			if(v.is_composite){
				if(form_container=='properties'){
					$('#'+form_container+' #'+obj.type+'_'+i).parent().parent().addClass('success');
					$('#'+form_container+' #'+obj.type+'_'+i).next().children().html('<i class="icon-star"></i>');
					add_sub_schema(i,v.value.type);
					fillout_form_from_json(v.value,i,'schema_form_'+v.value.type+'_'+i)
				}else{
					$('#'+form_container+' #'+tmp+'_'+i).parent().parent().addClass('success');
					$('#'+form_container+' #'+tmp+'_'+i).next().children().html('<i class="icon-star"></i>');
					add_sub_schema(property+'_'+i,v.value.type);
					fillout_form_from_json(v.value,property+'_'+i,'schema_form_'+v.value.type+'_'+property+'_'+i)
				}
			}else{
				if(i=='entity_uri'){
					$('#properties #entity_uri').val(v.value);
					$('#properties #entity_uri').parent().parent().addClass('success');
				}else{
					if(form_container=='properties'){
						$('#'+form_container+' #'+obj.type+'_'+i).val(v.value);
						$('#'+form_container+' #'+obj.type+'_'+i).parent().parent().addClass('success');
					}else{
						tmp=form_container.split('schema_form_'+obj.type+'_');
						tmp=tmp[1];
						if(!tmp){
							// it is a repeated tab
							var tmp2=form_container.split('schema_form_')[1];
							$('#schema_form_'+obj.type+'_'+tmp2+' #'+tmp2+'_'+i).val(v.value);
							$('#schema_form_'+obj.type+'_'+tmp2+' #'+tmp2+'_'+i).parent().parent().addClass('success');
						}else{
							$('#'+form_container+' #'+tmp+'_'+i).val(v.value);
							$('#'+form_container+' #'+tmp+'_'+i).parent().parent().addClass('success');
						}	
					}
				}
			}
		}
	});
}
