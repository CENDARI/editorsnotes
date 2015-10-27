




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
	

	// Script: jQuery replaceText: String replace for your jQueries!
	//
	// *Version: 1.1, Last updated: 11/21/2009*
	// 
	// Project Home - http://benalman.com/projects/jquery-replacetext-plugin/
	// GitHub       - http://github.com/cowboy/jquery-replacetext/
	// Source       - http://github.com/cowboy/jquery-replacetext/raw/master/jquery.ba-replacetext.js
	// (Minified)   - http://github.com/cowboy/jquery-replacetext/raw/master/jquery.ba-replacetext.min.js (0.5kb)
	// 
	// About: License
	// 
	// Copyright (c) 2009 "Cowboy" Ben Alman,
	// Dual licensed under the MIT and GPL licenses.
	// http://benalman.com/about/license/
	// 
	// About: Examples
	// 
	// This working example, complete with fully commented code, illustrates one way
	// in which this plugin can be used.
	// 
	// replaceText - http://benalman.com/code/projects/jquery-replacetext/examples/replacetext/
	// 
	// About: Support and Testing
	// 
	// Information about what version or versions of jQuery this plugin has been
	// tested with, and what browsers it has been tested in.
	// 
	// jQuery Versions - 1.3.2, 1.4.1
	// Browsers Tested - Internet Explorer 6-8, Firefox 2-3.6, Safari 3-4, Chrome, Opera 9.6-10.1.
	// 
	// About: Release History
	// 
	// 1.1 - (11/21/2009) Simplified the code and API substantially.
	// 1.0 - (11/21/2009) Initial release
	$.fn.replaceText = function( search, replace, text_only ) {
		return this.each(function(){
			var node = this.firstChild,
			val,
			new_val,

			// Elements to be removed at the end.
			remove = [];

			// Only continue if firstChild exists.
			if ( node ) {

				// Loop over all childNodes.
				do {

					// Only process text nodes.
					if ( node.nodeType === 3 ) {

						// The original node value.
						val = node.nodeValue;

						// The new value.
						new_val = val.replace( search, replace );

						// Only replace text if the new value is actually different!
						if ( new_val !== val ) {

							if ( !text_only && /</.test( new_val ) ) {
								// The new value contains HTML, set it in a slower but far more
								// robust way.
								$(node).before( new_val );

								// Don't remove the node yet, or the loop will lose its place.
								remove.push( node );
							} else {
								// The new value contains no HTML, so it can be set in this
								// very fast, simple way.
								node.nodeValue = new_val;
							}
						}
					}

				} while ( node = node.nextSibling );
			}

			// Time to remove those elements!
			remove.length && $(remove).remove();
		});
	};  

	jQuery.fn.outerHTML = function(s) {
	    return s
	        ? this.before(s).remove()
	        : jQuery("<p>").append(this.eq(0).clone()).html();
	};

	$.fn.getAttributes = function() {
		var attributes = {}; 

		if( this.length ) {
			$.each( this[0].attributes, function( index, attr ) {
				attributes[ attr.name ] = attr.value;
			} ); 
		}

		return attributes;
	};

	var entity_types_converter = {
		"PERSON"		: "PER",	
		"EVENT"			: "EVT",
		"PERIOD"		: "EVT",
		"LOCATION"		: "PLA",
		"NATIONAL"		: "PLA",
		"WEBSITE"		: "PUB",
		"MEDIA"			: "PUB",
		"INSTITUTION"	: "ORG",
		"ORGANISATION"	: "ORG",
		"SPORT_TEAM"	: "ORG",
		"BUSINESS"		: "ORG"
	}	

	var rdface_schema_name ={
		"PER" : "Person" ,
		"PLA" : "Place" ,
		"ORG" : "Organization" ,
		"EVT" : "Event" ,
		"PUB" : "CreativeWork" ,
	}


	var rdface_class = {
		"ORG" : "r_organization",
		"EVT" : "r_event",
		"PLA" : "r_place",
		"PER" : "r_person"
	}


	//<span class="r_entity r_event" typeof="schema:Event">
	createBasicAttributes = function (type) {
		var attributes= {}
		var rdface_type = entity_types_converter[type]

		attributes['class'] = 'r_entity '+rdface_class[rdface_type]
		attributes['typeof'] = 'schema:'+rdface_schema_name[rdface_type]

		return attributes
	}

	createEntityTag= function(name,attributes){
		var span = $('<span>').append('<span class="r_prop r_name" property="schema:name">'+name+'</span>')

		for (var attrname in attributes){
			span.attr(attrname,attributes[attrname])
		}

		return span.outerHTML()
	}

	function escapeRegExp(string) {
	    return string.replace(/([.*+?^=!:${}()|\[\]\/\\])/g, "\\$1");
	}
	function replaceAll(string, find, replace) {
	  return string.replace(new RegExp(escapeRegExp(find), 'g'), replace);
	}
	
	function strSplitOnLength(data, your_desired_width) {
		if(data.length <= 0)
			return [];  // return an empty array

		var splitData = data.split(/([\s\n\r]+)/);
		var arr = [];
		var cnt = 0;
		for (var i = 0; i < splitData.length; ++i) {
			if (!arr[cnt]) arr[cnt] = '';  //Instantiate array entry to empty string if null or undefined
			if (your_desired_width < (splitData[i].length + arr[cnt].length))
				cnt++;
			arr[cnt] += splitData[i];
		}

		return arr;
	}

	// Load plugin specific language pack
	tinymce.PluginManager.requireLangPack('nerd');

	tinymce.create('tinymce.plugins.NerdPlugin', {
		/**
		 * Initializes the plugin, this will be executed after the plugin has been created.
		 * This call is done before the editor instance has finished it's initialization so use the onInit event
		 * of the editor instance to intercept that event.
		 *
		 * @param {tinymce.Editor} ed Editor instance that the plugin is initialized in.
		 * @param {string} url Absolute URL to where the plugin is located.
		 */
		init : function(ed, url) {
			// Register the command so that it can be invoked by using tinyMCE.activeEditor.execCommand('mceNerd');
			console.log("NERD: doing nerd stuff :D");
			ed.addCommand('mceNerd', function() {
				var content_text = $(ed.getContent()).text();
				var deferreds  = [];
				var split_text = strSplitOnLength(content_text,3000)

				nerd_url = cendari_root_url+'cendari/nerd'//?text='+encodeURIComponent($(ed.getContent()).text())
				for(var k=0;k<split_text.length;k++){
					deferreds.push(
						$.ajax({
					        url:nerd_url,
							data: { 
								text :split_text[k], 
								onlyNER : false,
								//				  	  shortText : $('#shortText').is(':checked'),
								nbest : false,
								sentence :false,
								format : "JSON",
								customisation : "generic" 
							},
					        contentType:false,
							beforeSend: function( xhr ) {
								// xhr.overrideMimeType( "text/plain; charset=x-user-defined" );
								ed.setProgressState(true);
							},
					        success: function(data){
					        },
					        error: function(xhr){
					        }
				     	})
						
					)
				}

				$.when.apply(this,deferreds)
					.done(function(){
						var entities = [];
						var content = ed.getContent();
						for(var i = 0; i < arguments.length; i++) {
							console.log(arguments[i]);
							entities= entities.concat(arguments[i][0]['entities'])
						}
						console.log("NERD",entities);
						console.log("NERD",entities.length);

			       		for(i=0;i<entities.length;i++){
					          		
			          		entities.skip=false;

			          		if(entity_types_converter.hasOwnProperty(entities[i].type)===-1){ //not one of the types we support
			          			entities.skip = true;
			          			continue;
			          		}
		          			var rdface_type = entity_types_converter[entities[i].type]
			          		var elements = [] 
			          		$(content).find('.r_entity').each(function(){
			          			if($(this).text().indexOf(entities[i].rawName)){
			          				elements.push(this)
			          			}
			          		})
			          		// $(content).find('.r_entity:contains('+entities[i].rawName+')')
			          		if(elements.length ===0 ){ // there is not already an  entity with this name so we can create the entity in the next step
			          			continue;
			          		}

			          		if($(elements[0]).attr('class').hasOwnProperty(rdface_class[rdface_type])===-1){ //there is an entity with this name but with different type, so we are not going to change it
			          			entities[i].skip=true;
			          			continue;
			          		}

			          		for(var j=0; j<elements.length;j++){
			          			var attributes = {}
			          			el_attributes = $(elements[j]).getAttributes()
			          			for (var attrname in el_attributes) { 
			          				if(!attributes.hasOwnProperty(attrname)){
			          					attributes[attrname] = el_attributes[attrname]; 
			          				}
			          			}

			          			// content.replace($(elements[j]).outerHTML(),$(elements[j]).text())
			          			content = replaceAll(content,$(elements[j]).outerHTML(),$(elements[j]).text())

			          		}
			          		entities[i].attributes_list = attributes
				        }

			          	var entities_served = []
			          	for(i=0;i<entities.length;i++){
			          		if(entities[i].skip){
			          			continue;
			          		}
			          		if (entities_served.indexOf(entities[i].rawName)!==-1){
			          			continue;
			          		}

			          		if(!entities[i].hasOwnProperty('attributes_list')){
			          			entities[i].attributes_list = createBasicAttributes(entities[i].type);
			          		}

			          		entiy_span = createEntityTag(entities[i].rawName,entities[i].attributes_list)

			          		content = replaceAll(content,entities[i].rawName,entiy_span);
			          		entities_served.push(entities[i].rawName);
			          	}
						
						$content = $(content);
						$content.find('.r_entity').has('.r_entity').each(function(){ 
							$(this).find('.r_entity').each(function(index) {
								var text = $(this).text();//get span content
								$(this).replaceWith(text);//replace all span with just content
							}); 
						})

			          	ed.setContent($content.html());
			          	while( $('.mceBlocker').length || $('.mceProgress').length )
			          		ed.setProgressState(false);
					})
					.fail(function (jqXHR, status, error){
						console.log("status text",status);
						console.log("error text",error);
						console.log("jqXHR object",jqXHR);
						while( $('.mceBlocker').length || $('.mceProgress').length )
							ed.setProgressState(false);
					})



			});

			// Register nerd button
			ed.addButton('nerd', {
				title : 'nerd.desc',
				cmd : 'mceNerd',
				image : url + '/img/nerd.png'
			});

			// Add a node change handler, selects the button in the UI when a image is selected
			ed.onNodeChange.add(function(ed, cm, n) {
				cm.setActive('nerd', n.nodeName == 'IMG');
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
				longname : 'Nerd plugin',
				author : 'Some author',
				authorurl : 'http://tinymce.moxiecode.com',
				infourl : 'http://wiki.moxiecode.com/index.php/TinyMCE:Plugins/nerd',
				version : "1.0"
			};
		}
	});

	// Register plugin
	tinymce.PluginManager.add('nerd', tinymce.plugins.NerdPlugin);
})();