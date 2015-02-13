/**
 * editor_plugin_src.js
 *
 * Copyright 2009, Moxiecode Systems AB
 * Released under LGPL License.
 *
 * License: http://tinymce.moxiecode.com/license
 * Contributing: http://tinymce.moxiecode.com/contributing
 */


function SubmitSuccesful(responseText, statusText) {    
	console.log('responseText',responseText);
	console.log('json',JSON.parse(responseText));      					             
	// //console.log(responseText);
	// responseJson = responseText;

	// if ( (responseJson == null) || (responseJson.length == 0) ){
	// 	$('#requestResult').html("<font color='red'>Error encountered while receiving the server's answer: response is empty.</font>");   
	// 	return;
	// }

	// if ($('#selectedService').attr('value') == 'processNERDQuery') {
	// 	responseJson = jQuery.parseJSON(responseJson);
	// }

	// var display = '<div class=\"note-tabs\"> \
	// <ul id=\"resultTab\" class=\"nav nav-tabs\"> \
	// <li class="active"><a href=\"#navbar-fixed-annotation\" data-toggle=\"tab\">Annotations</a></li> \
	// <li><a href=\"#navbar-fixed-json\" data-toggle=\"tab\">Response</a></li> \
	// </ul> \
	// <div class="tab-content"> \
	// <div class="tab-pane active" id="navbar-fixed-annotation">\n';   	

	// var nbest = false; 
	// if (responseJson.nbest == true)
	// 	nbest = true;

	// if (responseJson.sentences) {
	// 	display += '<div style="max-height:150px; overflow:auto;"><table id="sentenceIndex" class="table table-bordered table-condensed">';  
	// 	var m = 0;
	// 	var text = responseJson.text;
	// 	for(var sentence in responseJson.sentences) {    
	// 		if (m == 0) { 	
	// 			display += '<tr class="highlight" id="sent_'+m+'" rank="'+m+'" >'; 
	// 		}   
	// 		else {
	// 			display += '<tr id="sent_'+m+'" rank="'+m+'" >';     
	// 		}
	// 		display += '<td style="width:25px;height:13px;font-size:small;">'+m+'</td>'  
	// 		var start = responseJson.sentences[sentence].offsetStart;
	// 		var end = responseJson.sentences[sentence].offsetEnd;
	// 		display += '<td style="font-size:small;height:13px;color:#333;">'+text.substring(start,end)+'</td>';
	// 		display += '</tr>';               
	// 		m++;
	// 	}
	// 	display += '</table></div>\n'; 
	// }

	// display += '<pre style="background-color:#FFF;width:95%;" id="displayAnnotatedText">'; 

	// // this variable is used to keep track of the last annotation and avoid "overlapping"
	// // annotations in case of nbest results.
	// // in case of nbest results, we haveonly one annotation in the text, but this can
	// // lead to the visualisation of several info boxes on the right panel (one per entity candidate)
	// var lastMaxIndex = responseJson.text.length;
	// {    
	// 	display += '<table id="sentenceNER" style="width:100%;table-layout:fixed;" class="table">'; 
	// 	var string = responseJson.text;
	// 	if (!responseJson.sentences || (responseJson.sentences.length == 0)) {
	// 		display += '<tr style="background-color:#FFF;">';     
	// 		if (responseJson.entities) {
	// 			var currentAnnotationIndex = responseJson.entities.length-1;
	// 			for(var m=responseJson.entities.length-1; m>=0; m--) {
	// 				var entity = responseJson.entities[m];
	// 				var label = entity.type;	
	// 				if (!label)
	// 					label = entity.rawName;
	// 				var start = parseInt(entity.offsetStart,10);
	// 				var end = parseInt(entity.offsetEnd,10);       

	// 				if (start > lastMaxIndex) {
	// 					// we have a problem in the initial sort of the entities
	// 					// the server response is not compatible with the client 
	// 					console.log("Sorting of entities as present in the server's response not valid for this client.");
	// 				}
	// 				else if (start == lastMaxIndex) {
	// 					// the entity is associated to the previous map
	// 					entityMap[currentAnnotationIndex].push(responseJson.entities[m]);
	// 				}
	// 				else if (end > lastMaxIndex) {
	// 					end = lastMaxIndex;
	// 					lastMaxIndex = start;
	// 					// the entity is associated to the previous map
	// 					entityMap[currentAnnotationIndex].push(responseJson.entities[m]);
	// 				}
	// 				else {
	// 					string = string.substring(0,start) 
	// 					+ '<span id="annot-'+m+'" rel="popover" data-color="'+label+'">'
	// 					+ '<span class="label ' + label + '" style="cursor:hand;cursor:pointer;" >'
	// 					+ string.substring(start,end) + '</span></span>' + string.substring(end,string.length+1); 
	// 					lastMaxIndex = start;
	// 					currentAnnotationIndex = m;
	// 					entityMap[currentAnnotationIndex] = [];
	// 					entityMap[currentAnnotationIndex].push(responseJson.entities[m]);
	// 				}						
	// 			} 
	// 			//console.log(entityMap);
	// 			string = "<p>" + string.replace(/(\r\n|\n|\r)/gm, "</p><p>") + "</p>";
	// 			//string = string.replace("<p></p>", "");

	// 			display += '<td style="font-size:small;width:60%;border:1px solid #CCC;"><p>'+string+'</p></td>';
	// 			display += '<td style="font-size:small;width:40%;padding:0 5px; border:0"><span id="detailed_annot-0" /></td>';	
	// 		}
	// 		display += '</tr>';
	// 	}
	// 	else {
	// 		//for(var sentence in responseJson.sentences) 
	// 		{    
	// 			display += '<tr style="background-color:#FFF;">';  

	// 			display += '<td style="font-size:small;width:60%;border:1px solid #CCC;"><p><span id="sentence_ner">'+
	// 			" "+'</span></p></td>';
	// 			display += '<td style="font-size:small;width:40%;padding:0 5px; border:0"><span id="detailed_annot-0" /></td>';	
	// 			display += '</tr>';
	// 		}
	// 	}

	// 	display += '</table>\n';
	// }

	// display += '</pre>\n';

	// //$('#requestResult').html(display);  

	// display += '</div> \
	// 	<div class="tab-pane " id="navbar-fixed-json">\n';
	// // JSON visualisation component 	
	// // with pretty print
	// display += "<pre class='prettyprint' id='jsonCode'>";  

	// display += "<pre class='prettyprint lang-json' id='xmlCode'>";  
	// var testStr = vkbeautify.json(responseText);

	// display += htmll(testStr);

	// display += "</pre>"; 		
	// display += '</div></div></div>';					   												  

	// $('#requestResult').html(display);     
	// window.prettyPrint && prettyPrint();

	// if (responseJson.sentences) {
	// 	// bind the sentence table line with the appropriate sentence result display
	// 	var nbSentences = responseJson.sentences.length;
	// 	for(var p=0;p<nbSentences;p++) {
	// 		//$('#sent'+p).bind('click',viewSentenceResults());      
	// 		$('#sentenceIndex').on('click', 'tbody tr', function(event) {
	// 			$(this).addClass('highlight').siblings().removeClass('highlight');       
	// 			viewSentenceResults($(this).attr('rank'));
	// 		});
	// 	} 
	// 	viewSentenceResults('0');
	// }		

	// for (var key in entityMap) {
	// 	if (entityMap.hasOwnProperty(key)) {
	// 		$('#annot-'+key).bind('hover', viewEntity);  
	// 		$('#annot-'+key).bind('click', viewEntity);  	
	// 	}
	// }
	// $('#detailed_annot-0').hide();	

	// /*if (responseJson.entities) {
	// for(var m=responseJson.entities.length-1; m>=0; m--) {
	// $('#annot-'+m).bind('hover', viewEntity);  
	// $('#annot-'+m).bind('click', viewEntity); 
	// }
	// } 
	// $('#detailed_annot-0').hide();	 */
}

(function() {
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
			// Register the command so that it can be invoked by using tinyMCE.activeEditor.execCommand('mceExample');
			consoel.log('url',url);
			var proxy_url = url+'/php/proxy.php'
			var nerd_url = 'http://traces1.saclay.inria.fr:8090/service/processNERDText';
			console.log(proxy_url);
			window.ed = ed;
			ed.addCommand('mceNerd', function() {
				// console.log()
				$.ajax({
					type: 'GET',
					url: proxy_url,
					data: { 
						text : encodeURIComponent(ed.getContent()),
						onlyNER:"false",
						shortText:"false",
						nbest:"false",
						sentence:"false",
						format:"JSON",
						customisation:"generic"
					},
					//			  processData: false,
					success: SubmitSuccesful,
					error: AjaxError,
					contentType:false  
					//contentType: "multipart/form-data"
				});


			});

			// Register example button
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
				infourl : 'http://wiki.moxiecode.com/index.php/TinyMCE:Plugins/example',
				version : "1.0"
			};
		}
	});

	// Register plugin
	tinymce.PluginManager.add('nerd', tinymce.plugins.NerdPlugin);
})();