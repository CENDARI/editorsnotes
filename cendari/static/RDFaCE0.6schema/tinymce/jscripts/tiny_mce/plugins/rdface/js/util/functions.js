//set RDFa as default annotation format
if(!getCookie("annotationF")){
	// set RDFa as default annotation format
	setCookie("annotationF","RDFa",30);
}
//set Sindice as default search engine
if(!getCookie("uriSuggestor")){
	// set RDFa as default annotation format
	setCookie("uriSuggestor","Sindice",30);
}
//creates random light colors
function get_random_color() {
    var letters = 'ABCDE'.split('');
    var color = '#';
    for (var i=0; i<3; i++ ) {
        color += letters[Math.floor(Math.random() * letters.length)];
    }
    return color;
}
function adoptPrevAnnotations(editor,format){
	//for RDFa and Microdata
	//ToDo: does not work if user uses 'vocab' attribute

	var tmp;
	if(format=='RDFa'){
		$.each($(editor.getDoc()).find('*[typeof]'), function(key,value){
			tmp=$(value).attr('typeof');
			tmp='r_'+tmp.split(':')[1].toLowerCase();
			if(!$(value).hasClass('r_entity')){
				$(value).addClass('r_entity');
			}
			//specific entity class
			if(!$(value).hasClass(tmp)){
				$(value).addClass(tmp);
			}
		});		
	}else{
		$.each($(editor.getDoc()).find('*[itemtype]'), function(key,value){
			tmp=$(value).attr('itemtype');
			tmp='r_'+tmp.split('http://schema.org/')[1].toLowerCase();
			if(!$(value).hasClass('r_entity')){
				$(value).addClass('r_entity');
			}
			//specific entity class
			if(!$(value).hasClass(tmp)){
				$(value).addClass(tmp);
			}
		});			
	}
}

function refreshFacts(){
	if($('#tripleFrame').length)
		$('#tripleFrame').attr('src', $('#tripleFrame').attr('src'));
}
function syncWithFacts(subject,predicate,object){
	if($('#tripleFrame').length){
		var found=0;
			if(subject){
				$.each($('#tripleFrame').contents().find('.fact-triple'), function(key, value) {
					if ($(value).find('.fact-predicate').html().trim()=='rdf:type') {
						if($(value).find('.fact-subject').html().trim()==shortenURI(subject)){
							var target_offset = $(value).offset();
							var target_top = target_offset.top;
							$("#tripleFrame").contents().find('html, body').animate({scrollTop:target_top}, 500);
							$(value).css("background-color","#eeff22");
							found=1;
						}
					}
				});
			}
			if(!found){
				$.each($('#tripleFrame').contents().find('.fact-triple'), function(key, value) {
					if ($(value).find('.fact-predicate').html().trim()=='schema:name') {
						if($(value).find('.fact-object').text().trim()=='"'+decodeURIComponent(object)+'"'){
							var target_offset = $(value).offset();
							var target_top = target_offset.top;
							$("#tripleFrame").contents().find('html, body').animate({scrollTop:target_top}, 500);
							$(value).css("background-color","#eeff22");
							found=1;
						}
					}
				});			
			}
	}
}
function unhighlightFacts(){
	if($('#tripleFrame').length){
		$('#tripleFrame').contents().find('.fact-triple').css("background-color","");
	}
}
function shortenURI(uri){
	var namespaceArr = new Array();
	// add some default namespaces
	//TODO: add more...
	namespaceArr.push(Array("rdf","http://www.w3.org/1999/02/22-rdf-syntax-ns#"));
	namespaceArr.push(Array("rdfs", "http://www.w3.org/2000/01/rdf-schema#"));
	namespaceArr.push(Array("dbpedia", "http://dbpedia.org/resource/"));
	namespaceArr.push(Array("schema", "http://schema.org/"));
	var uri_short;
	// shorten namespace address
	$.each(namespaceArr, function(i, value) {
		uri_short = uri.replace(
				namespaceArr[i][1],
				namespaceArr[i][0] + ":");
		if (uri_short != uri) {
			return false;
		}
	});
	return uri_short;
}
//show or hide selected entities
function show_entities(editor,c){
	if(c=='none'){
		$.each($(editor.getDoc()).find('.r_entity'), function(index, value) { 
			if($.browser.webkit == true){
				//Problem with Chrome: removing background color doesn't work!
				$(this).css('background-color','#fff');
			}else{
				$(this).css('background','none');
			}
			$(this).removeClass('r_entity').addClass('r_entity_h');		
		});		
		$.each($(editor.getDoc()).find('.r_prop'), function(index, value) { 
			if($.browser.webkit == true){
				//Problem with Chrome: removing background color doesn't work!
				$(this).css('background-color','#fff');
			}else{
				$(this).css('background','none');
			}
			$(this).removeClass('r_prop').addClass('r_prop_h');		
		});
	}else if(c=='all'){
		$.each($(editor.getDoc()).find('.r_entity_h'), function(index, value) {
			$(this).removeClass('r_entity_h').addClass('r_entity').removeAttr("style");		
		});		
		$.each($(editor.getDoc()).find('.r_prop_h'), function(index, value) {
			$(this).removeClass('r_prop_h').addClass('r_prop').removeAttr("style");		
		});	
	}else{
	//split the selected types
	}
	editor.setContent(editor.getContent());
}
function remove_annotation(pointer,format){
		pointer.find('.tooltip').remove();
		pointer.find('.tooltip-t').remove();
	if(format=="RDFa"){
		pointer.css("background-color","");
		pointer.removeAttr("typeof").removeAttr("class").removeAttr("resource").removeAttr("property");
		pointer.find('>[property]').each(function(i,v){
			remove_annotation($(v),'RDFa')
		});
	}else{
		pointer.css("background-color","");
		pointer.removeAttr("itemtype").removeAttr("class").removeAttr("itemid").removeAttr("itemscope").removeAttr("itemprop");
		pointer.find('>[itemprop]').each(function(i,v){
			remove_annotation($(v),'Microdata')
		});	
	}
	//remove spans wich have no attribute
	pointer.find('span').each(function(i,v){
		if(!$(v)[0].attributes.length){
			//$(v).unwrap();
			$(v).replaceWith($(v).html());
		}
	});
	//remove pointer tags as well if necessary
	var tagName=pointer.prop("tagName").toLowerCase();
	if(tagName=='span' && !$(pointer)[0].attributes.length){
		//pointer.unwrap();
		pointer.replaceWith(pointer.html());
	}
}
function remove_annotations(editor,only_automatic){
	var tmp;
	var aF=getCookie("annotationF");
		$(editor.getDoc()).find('.tooltip').remove();
		$(editor.getDoc()).find('.tooltip-t').remove();
		if(only_automatic){
			$(editor.getDoc()).find('.automatic').each(function(i,v){
				remove_annotation($(v),aF);
			});	
		}else{
			$(editor.getDoc()).find('.r_entity').each(function(i,v){
				remove_annotation($(v),aF);
			});		
		}
		// remove namespaces as well
		var ns=editor.dom.get('namespaces');
		if(ns){
			editor.setContent(ns.innerHTML);
		}
}
//Insert RDFa/Microdata attributes to HTML DOM tree
function insert_entity(editor,entity_type,b,has_rel){
	activateAjaxIndicator(b);

	// Cendari code E.G. aviz
	var maxWordsAllowed = 50;

	var selectedContent = editor.selection.getContent();
	//console.log(selectedContent);
	if(!selectedContent){
		alert('Please select some text first!');
		return null;
	}
	var selectedContentText=editor.selection.getContent({format : 'text'})
	var selectedNode = editor.selection.getNode();
	var nodeContent = selectedNode.innerHTML;

	// remove tinymce redundant data-mcs-href attribute
	nodeContent = nodeContent.replace(/\s(data-mce-href=)".*?"/g, "");
	nodeContent = nodeContent.replace(/\s(xmlns=)".*?"/g, "");
	// get an URI for entity 
	var uri='';
	//var uri=suggestURI(proxy_url,"api="+getCookie("uriSuggestor")+"&query="+selectedContent,true);
	// Annotation methods
	// if there is no need to add new tag
	if(getCookie("annotationF")=="RDFa"){
		/*if ((selectedContent == nodeContent) || (selectedContentText==$(selectedContent).html())) {
					//alert("if!!!");

			editor.dom.setAttrib(selectedNode,"typeof",'schema:'+entity_type);
			if(uri){
				editor.dom.setAttrib(selectedNode,"resource",uri);
			}
			if(has_rel){
				editor.dom.setAttrib(selectedNode,"property",'schema:'+has_rel);
			}
			editor.dom.setAttrib(selectedNode,"class",'r_entity r_'+entity_type.toLowerCase());
			if(countWords(nodeContent)<6){
			alert("count");
				selectedNode.innerHTML="<span class='r_prop r_name' property='schema:name'>"+nodeContent+"</span> &nbsp;&nbsp;";}
			
		} */
		//else {
		//						alert("else!!!");

			// we need to add a new neutral html tag which involves
			// our annotation attributes
			// to do this we also need to check whether there is a paragraph or
			// not (to use DIV or SPAN)
			var temp = ' class="r_entity r_'+entity_type.toLowerCase()+'" typeof="schema:'+entity_type+'"';
			if(uri){
				temp=temp+' resource="'+uri+'"';
			}
			if(has_rel){
				temp=temp+' property="schema:'+has_rel+'"';
			}
			var annotatedContent;

			// Cendari code E.G. aviz
			if(countWords(selectedContent)<maxWordsAllowed){
				annotatedContent = "<span" + temp + "><span class='r_prop r_name' property='schema:name'>" + selectedContent
				+ "</span></span>";
			}else{
				annotatedContent = "<span" + temp + ">" + selectedContent
				+ "</span>";
			}
			if ((editor.selection.getRng().startContainer.data != editor.selection
					.getRng().endContainer.data)
					|| editor.selection.getRng().commonAncestorContainer.nodeName == "BODY") {
				annotatedContent = "<div" + temp + ">" + selectedContent
				+ "</div>";
			}
			// editor.selection.setContent(annotatedContent);
			
			annotatedContent+="&nbsp;&nbsp;";
			editor.execCommand('mceInsertRawHTML', false,annotatedContent);
		//}
		// add namespaces 
		var ns =editor.dom.get('namespaces');
		var tmp='';
		var nsStart;
		var nsEnd;
		$.each(vocabularies, function(key, val) {
			var nsURI = popular_prefixes[val];
			tmp += val + ': ' + nsURI+ ' ';
		});			
		if(ns){
			txt=ns.innerHTML;
			nsStart = "";
			nsEnd="";
		}else{
			nsStart = "<div id='namespaces' prefix='" + tmp + "'>";
			nsEnd="</div>";
		}	
		editor.setContent(nsStart+editor.getContent()+"&nbsp;&nbsp;"+nsEnd);
	}
	else{

		/*if ((selectedContent == nodeContent) || (selectedContentText==$(selectedContent).html())) {
			editor.dom.setAttrib(selectedNode,"itemtype",'http://schema.org/'+entity_type);
			if(uri){
				editor.dom.setAttrib(selectedNode,"itemid",uri);
			}
			if(has_rel){
				editor.dom.setAttrib(selectedNode,"itemprop",has_rel);
				//todo fix the bug
				editor.dom.setAttrib(selectedNode,"itemscope",' ');
			}
			editor.dom.setAttrib(selectedNode,"class",'r_entity r_'+entity_type.toLowerCase());
			if(countWords(nodeContent)<6)
				selectedNode.innerHTML="<span class='r_prop r_name' itemprop='name'>"+nodeContent+"</span>";
		} */
		//else {
			// we need to add a new neutral html tag which involves
			// our annotation attributes
			// to do this we also need to check whether there is a paragraph or
			// not (to use DIV or SPAN)
			var temp = ' class="r_entity r_'+entity_type.toLowerCase()+'" itemscope itemtype="http://schema.org/'+entity_type+'"';
			if(uri){
				temp=temp+' itemid="'+uri+'"';
			}
			if(has_rel){
				temp=temp+' itemscope itemprop="'+has_rel+'"';
			}
			var annotatedContent;
			if(countWords(selectedContent)<6){
				annotatedContent = "<span" + temp + "><span class='r_prop r_name' itemprop='name'>" + selectedContent
				+ "</span></span>";
			}else{
				annotatedContent = "<span" + temp + ">" + selectedContent
				+ "</span>";
			}
			if ((editor.selection.getRng().startContainer.data != editor.selection
					.getRng().endContainer.data)
					|| editor.selection.getRng().commonAncestorContainer.nodeName == "BODY") {
				annotatedContent = "<div" + temp + ">" + selectedContent
				+ "</div>";
			}
			// editor.selection.setContent(annotatedContent);
			annotatedContent+="&nbsp;&nbsp;";
			editor.execCommand('mceInsertRawHTML', false,annotatedContent);
		//}
		editor.setContent(editor.getContent());
	}
	editor.nodeChanged();
}
//Insert related attributes to HTML DOM tree
function insert_property(editor,property,b){

	activateAjaxIndicator(b);
	var selectedContent = editor.selection.getContent();
	if(!selectedContent){
		alert('Please select some text first!');
		return null;
	}
	var selectedContentText=editor.selection.getContent({format : 'text'})
	var selectedNode = editor.selection.getNode();
	var nodeContent = selectedNode.innerHTML;
	// remove tinymce redundant data-mcs-href attribute
	nodeContent = nodeContent.replace(/\s(data-mce-href=)".*?"/g, "");
	nodeContent = nodeContent.replace(/\s(xmlns=)".*?"/g, "");

	// Annotation methods
	// if there is no need to add new tag
	if(getCookie("annotationF")=="RDFa"){
		if ((selectedContent == nodeContent) || (selectedContentText==$(selectedContent).html())) {
			editor.dom.setAttrib(selectedNode,"property",'schema:'+property);
			editor.dom.setAttrib(selectedNode,"class",'r_prop r_'+property.toLowerCase());
		} else {
			// we need to add a new neutral html tag which involves
			// our annotation attributes
			// to do this we also need to check whether there is a paragraph or
			// not (to use DIV or SPAN)
			var temp = ' class="r_prop r_'+property.toLowerCase()+'" property="schema:'+property+'"';

			var annotatedContent = "<span" + temp + ">" + selectedContent
			+ "</span>";
			if ((editor.selection.getRng().startContainer.data != editor.selection
					.getRng().endContainer.data)
					|| editor.selection.getRng().commonAncestorContainer.nodeName == "BODY") {
				annotatedContent = "<div" + temp + ">" + selectedContent
				+ "</div>";
			}
			// editor.selection.setContent(annotatedContent);
			editor.execCommand('mceInsertRawHTML', false,annotatedContent);
		}
		editor.setContent(editor.getContent());
	}else{
		if ((selectedContent == nodeContent) || (selectedContentText==$(selectedContent).html())) {
			editor.dom.setAttrib(selectedNode,"itemprop",property);
			editor.dom.setAttrib(selectedNode,"class",'r_prop r_'+property.toLowerCase());
		} else {
			// we need to add a new neutral html tag which involves
			// our annotation attributes
			// to do this we also need to check whether there is a paragraph or
			// not (to use DIV or SPAN)
			var temp = ' class="r_prop r_'+property.toLowerCase()+'" itemprop="'+property+'"';
			var annotatedContent = "<span" + temp + ">" + selectedContent
			+ "</span>";
			if ((editor.selection.getRng().startContainer.data != editor.selection
					.getRng().endContainer.data)
					|| editor.selection.getRng().commonAncestorContainer.nodeName == "BODY") {
				annotatedContent = "<div" + temp + ">" + selectedContent
				+ "</div>";
			}
			// editor.selection.setContent(annotatedContent);
			editor.execCommand('mceInsertRawHTML', false,annotatedContent);
		}
		editor.setContent(editor.getContent());
	}
	editor.nodeChanged();
}
function countWords(sentence){
	var s = sentence;
	s = s.replace(/(^\s*)|(\s*$)/gi,"");
	s = s.replace(/[ ]{2,}/gi," ");
	s = s.replace(/\n /,"\n");
	return s.split(' ').length;
}
//show dynamic tooltips
function showTooltips(editor,b){
	var xOffset = -10; // x distance from mouse
	var yOffset = 10; // y distance from mouse
	$.each($(editor.getDoc()).find('.r_entity'), function(index, value) { 
		// show tooltips if word count <6 
		if(countWords($(value).text())<6){
			$(this).unbind('click').click(function(e) {
				e.stopPropagation();
				editor.execCommand('editEntity',$(this));
			});	
			$(this).unbind('mouseover').mouseover(function(e) {								
				e.stopPropagation();
				var top = (e.pageY + yOffset); var left = (e.pageX + xOffset);
				$(this).css("background-color","orange");
				//synchronuize with fact browser if it is open
				syncWithFacts($(this).attr('resource'),$(this).attr('typeof'),encodeURIComponent($(this).text()));
				$(this).css("cursor","pointer");
				$(this).append(' <span id="typeof'+index+'" class="tooltip"><img id="arrow'+index+'" class="arrow"/>'+prepareTooltipContent($(this),0)+'</span>');
				$(editor.getDoc()).find('span#typeof'+index+' #arrow'+index).attr("src", b + "/img/arrow.png");
				$(editor.getDoc()).find('span#typeof'+index).css("top", top+"px").css("left", left+"px");
			});
			$(this).unbind('mousemove').mousemove(function(e) {
				var top = (e.pageY + yOffset);
				var left = (e.pageX + xOffset);
				$(editor.getDoc()).find('span#typeof'+index+' #arrow'+index).attr("src", b + "/img/arrow.png");
				$(editor.getDoc()).find('span#typeof'+index).css("top", top+"px").css("left", left+"px"); 
			});										
			$(this).unbind('mouseout').mouseout(function() {
				$(this).css("background-color","");
				$(this).css("cursor","");
				$(editor.getDoc()).find('span#typeof'+index).remove();
				$(this).html($(this).html().trim());//remove one space
				unhighlightFacts()
			});	
	   }else{
		   //we should show an appended icon to edit the entity
			$(this).unbind('mouseover').mouseover(function(e) {								
				//e.stopPropagation();
				var position = $(this).position();
				if(position.top<10){
					if($(editor.getDoc()).find('#inline_edit_btn'+index).length){
						$(editor.getDoc()).find('#inline_edit_btn'+index).css('left',position.left).css('top',$(this).height()+10);
					}else{
						$(this).before('<div id="inline_edit_btn'+index+'" style="position:absolute;z-index:199;left:'+(position.left)+'px;top:'+($(this).height()+10)+'px;"><a class="btn small">Edit '+getTypeOfEntity($(this),getCookie("annotationF"))+'</a></div>');
					}	
				}else{
					if($(editor.getDoc()).find('#inline_edit_btn'+index).length){
						$(editor.getDoc()).find('#inline_edit_btn'+index).css('left',position.left).css('top',position.top-25);
					}else{
						$(this).before('<div id="inline_edit_btn'+index+'" style="position:absolute;z-index:199;left:'+(position.left)+'px;top:'+(position.top-25)+'px;"><a class="btn small">Edit '+getTypeOfEntity($(this),getCookie("annotationF"))+'</a></div>');
					}
				}
			});
			$(this).unbind('mousemove').mousemove(function(e) {
				//e.stopPropagation();
				var position = $(this).position();
				if(position.top<10){
					if($(editor.getDoc()).find('#inline_edit_btn'+index).length){
						$(editor.getDoc()).find('#inline_edit_btn'+index).css('left',position.left).css('top',$(this).height()+10);
					}else{
						$(this).before('<div id="inline_edit_btn'+index+'" style="position:absolute;z-index:199;left:'+(position.left)+'px;top:'+($(this).height()+10)+'px;"><a class="btn small">Edit '+getTypeOfEntity($(this),getCookie("annotationF"))+'</a></div>');
					}	
				}else{
					if($(editor.getDoc()).find('#inline_edit_btn'+index).length){
						$(editor.getDoc()).find('#inline_edit_btn'+index).css('left',position.left).css('top',position.top-25);
					}else{
						$(this).before('<div id="inline_edit_btn'+index+'" style="position:absolute;z-index:199;left:'+(position.left)+'px;top:'+(position.top-25)+'px;"><a class="btn small">Edit '+getTypeOfEntity($(this),getCookie("annotationF"))+'</a></div>');
					}
				}
			});										
			$(this).unbind('mouseout').mouseout(function(e) {
				//e.stopPropagation();
				var refObj=$(this);
			    var timeoutId = setTimeout(function(){
			    	$(editor.getDoc()).find('#inline_edit_btn'+index).remove();
			    }, 800);
			    $(editor.getDoc()).find('#inline_edit_btn'+index).mouseover(function(ev) {
			    	ev.stopPropagation();
			    	clearTimeout(timeoutId);
				});
			    $(editor.getDoc()).find('#inline_edit_btn'+index).mouseout(function(ev) {
			    	ev.stopPropagation();
			    	$(editor.getDoc()).find('#inline_edit_btn'+index).remove();
				});	
			    $(editor.getDoc()).find('#inline_edit_btn'+index).click(function(ev) {								
					ev.stopPropagation();
					if($(editor.getDoc()).find('#inline_edit_btn'+index).length){
						$(editor.getDoc()).find('#inline_edit_btn'+index).remove();
						editor.execCommand('editEntity',refObj);
					}
				});
			});
		   
	   }

	});
	$.each($(editor.getDoc()).find('.r_prop'), function(index, value) {
		$(this).unbind('mouseover').mouseover(function(e) {								
			e.stopPropagation();
			var top = (e.pageY + yOffset); var left = (e.pageX + xOffset);
			$(this).css("background-color","#FFFC00");
			$(this).append(' <span id="typeof'+index+'" class="tooltip"><img id="arrow'+index+'" class="arrow"/>'+prepareTooltipContent($(this),1)+'</span>');
			$(editor.getDoc()).find('span#typeof'+index+' #arrow'+index).attr("src", b + "/img/arrow.png");
			$(editor.getDoc()).find('span#typeof'+index).css("top", top+"px").css("left", left+"px");
		});
		$(this).unbind('mousemove').mousemove(function(e) {
			var top = (e.pageY + yOffset);
			var left = (e.pageX + xOffset);
			$(editor.getDoc()).find('span#typeof'+index+' #arrow'+index).attr("src", b + "/img/arrow.png");
			$(editor.getDoc()).find('span#typeof'+index).css("top", top+"px").css("left", left+"px"); 
		});										
		$(this).unbind('mouseout').mouseout(function() {
			$(this).css("background-color","");
			$(editor.getDoc()).find('span#typeof'+index).remove();
			$(this).html($(this).html().trim());//remove one space
		});	
	});
}
//creating contents of tooltips
function prepareTooltipContent(entityObj,is_property){
	if(getCookie("annotationF")=="RDFa"){
		if(is_property){
			output=entityObj.attr('property').split(':')[1];
		}else{
			var entityType=getTypeOfEntity(entityObj,'RDFa');
			var output="<ul class='tooltip-t' style='list-style: none;text-align:left;margin:0 0 0 0;padding-left: 1em;text-indent: -1em;'>";
			if(entityObj.attr('property')){
				output +="<li>"+entityObj.attr('property').split(':')[1]+"</li>";
			}
			output +="<li>Type: <b>"+entityType+"</b></li>";
			output +="</ul>";		
		}
	}else{
		if(is_property){
			output=entityObj.attr('itemprop');
		}else{
			var entityType=getTypeOfEntity(entityObj,'Microdata');
			var output="<ul class='tooltip-t' style='list-style: none;text-align:left;margin:0 0 0 0;padding-left: 1em;text-indent: -1em;'>";
			if(entityObj.attr('itemprop')){
				output +="<li>"+entityObj.attr('itemprop')+"</li>";
			}
			output +="<li>Type: <b>"+entityType+"</b></li>";
			output +="</ul>";	
		}

	}
	return output;
}
function getTypeOfEntity(entityObj,ann_type){
	if(ann_type=="RDFa"){
		return entityObj.attr('typeof').split(':')[1];
	}else{
		return entityObj.attr('itemtype').split('http://schema.org/')[1];
	}	
}
function connectEnricherAPI(url,request_data){
/***  Enable Cross site request ***/
$(document).ajaxSend(function(event, xhr, settings) {
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    function sameOrigin(url) {
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }
    function safeMethod(method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    }
});	
/** **** **/
	var dataReceived;
	$.ajax({
		type : "POST",
		async: false,
		url : url,
		data : request_data,
		contentType: "application/x-www-form-urlencoded",
		dataType: "json",
		success : function(data) {
			dataReceived =  data;
		},
		error: function(xhr, txt, err){ 
			//alert("xhr: " + xhr + "\n textStatus: " +txt + "\n errorThrown: " + err+ "\n url: " + url);
			dataReceived=0;
		},
	});
	return dataReceived;
}
//top: returns only the top entity not all
function suggestURI(proxy_url,request_data,top){
	var dataReceived=connectEnricherAPI(proxy_url,request_data);
	if(dataReceived){
		//dataReceived = eval("(" + dataReceived + ")");
		if(dataReceived['totalResults']){
			if(top){
				return dataReceived.entries[0].link;
			}else{
				return dataReceived;
			}
		}	
	}
	return null;
}
function setCookie(c_name,value,exdays)
{
	$.cookie(c_name, value, { expires: exdays, path: '/' });
}
function getCookie(c_name)
{
	return $.cookie(c_name);
}
//Ontos predefined entities
var ontos_personURI = "http://www.ontosearch.com/2008/02/ontosminer-ns/domain/common/english#Person";
var ontos_organizationURI1 = "http://www.ontosearch.com/2008/02/ontosminer-ns/domain/common/english#Commercial_Organization";
var ontos_organizationURI2 = "http://www.ontosearch.com/2008/02/ontosminer-ns/domain/common/english#State_Organization";
var ontos_organizationURI3 = "http://www.ontosearch.com/2008/02/ontosminer-ns/domain/common/english#Mass_Media";
var ontos_organizationURI4 = "http://www.ontosearch.com/2008/02/ontosminer-ns/domain/common/english#Military_Organization";
var ontos_organizationURI5 = "http://www.ontosearch.com/2008/02/ontosminer-ns/domain/common/english#Investment_Organization";
var ontos_organizationURI6 = "http://www.ontosearch.com/2008/02/ontosminer-ns/domain/common/english#Educational_Organization";
var ontos_organizationURI7 = "http://www.ontosearch.com/2008/02/ontosminer-ns/domain/common/english#Government_Organization";
var ontos_organizationURI8 = "http://www.ontosearch.com/2008/02/ontosminer-ns/domain/common/english#Party";
var ontos_locationURI = "http://www.ontosearch.com/2008/02/ontosminer-ns/domain/common/english#Location";
var ontos_labelURI="http://sofa.semanticweb.org/sofa/v1.0/system#__LABEL_REL";
//Ontos position attributes
var ontos_annotation = "http://www.ontosearch.com/2007/12/annotation-ns#entity";
var ontos_startPosition = "http://www.ontosearch.com/2007/12/annotation-ns#plainStart";
var ontos_endPosition = "http://www.ontosearch.com/2007/12/annotation-ns#plainEnd";
vocabularies=new Array("rnews","foaf","dbpedia","schema");
//maps rNews types to Schema.org types
function mapTypeToSchema(p) {
	var output;
	switch (p) {
	case "Place":
		output = "http://schema.org/Place";
	break;
	case "Organization":
		output = "http://schema.org/Organization";
	break;
	case "Person":
		output = "http://schema.org/Person";
	break;	
	default:
		output = null;
	}
	return output;
}
//Mapping to rNews, foaf vocabulary
function mapToVocabulary(p) {
	var output;
	switch (p) {
	// typeof
	case "person":
	case "PERSON":
	case "Person":
	case "http://schema.org/Person":
	case ontos_personURI:
		output = "schema:Person";
		break;	
	case "organization":
	case "ORGANIZATION":
	case "CRIMINAL_ORGANIZATION":
	case "EDUCATIONAL_ORG":
	case "ENTERTAINMENT_ORG":
	case "GOVERNMENT_ORG":
	case "MEDIA_ORG":
	case "MILITARY_ORG":
	case "NON_GOVERNMENT_ORG":
	case "RELIGIOUS_ORG":
	case "COMMERCIAL_ORG":
	case "Company":
	case "Organization":
	case "http://schema.org/Organization":
	case ontos_organizationURI1:
	case ontos_organizationURI2:
	case ontos_organizationURI3:
	case ontos_organizationURI4:
	case ontos_organizationURI5:
	case ontos_organizationURI6:
	case ontos_organizationURI7:	
	case ontos_organizationURI8:	
		output = "schema:Organization";
		break;	
	case "location":
	case "Location":
	case "CITY":
	case "COUNTRY":
	case "City":
	case "Town":	
	case "Country":
	case "http://schema.org/Place":
	case ontos_locationURI:
		output = "schema:Place";
		break;	
	case "name":
	case "http://sofa.semanticweb.org/sofa/v1.0/system#__LABEL_REL":
		output = "schema:name";
		break;
	case "http://www.ontosearch.com/2008/02/ontosminer-ns/domain/common/english#FirstName":
		output = "schema:givenName";
		break;
	case "http://www.ontosearch.com/2008/02/ontosminer-ns/domain/common/english#FamilyName":
		output = "schema:familyName";
		break;
	case "http://www.ontosearch.com/2008/02/ontosminer-ns/domain/common/english#Gender":
		output = "schema:gender";
		break;
	default:
		output = null;
	} 
	return output;
}
function mapOutputToStandard(api,txt,proxy_url,exclude_arr){
	var entities = new Array();
	api = "DBpedia"; // hack to use DBpedia format > to be improved
	switch(api){
	case "Alchemy":
		entities=mapAlchemyOutputToStandard(txt,proxy_url,exclude_arr);
		break;
	case "Extractiv":
		entities=mapExtractivOutputToStandard(txt,proxy_url,exclude_arr);
		break;
	case "Calais":
		entities=mapCalaisOutputToStandard(txt,proxy_url,exclude_arr);
		break;
	case "Ontos":
		entities=mapOntosOutputToStandard(txt,proxy_url,exclude_arr);
		break;	
	case "Evri":
		entities=mapEvriOutputToStandard(txt,proxy_url,exclude_arr);
		break;	
	case "Saplo":
		entities=mapSaploOutputToStandard(txt,proxy_url,exclude_arr);
		break;	
	case "Lupedia":
		entities=mapLupediaOutputToStandard(txt,proxy_url,exclude_arr);
		break;			
	case "DBpedia":
		entities=mapDBpediaOutputToStandard(txt,proxy_url,exclude_arr);
		break;	
	}
	return entities;
}
function makeRDFaTriples(entities) {
	var entitiesRDFa = new Array();
	$.each(entities, function(key, val) {
		var annotations=new Array();
		annotations.push(Array("rdf:type",mapToVocabulary(val["type"])));
		val['type']=mapToVocabulary(val["type"]);
		$.each(val["properties"], function(i, v) {
			if(mapToVocabulary(v[0])){
				annotations.push(Array(mapToVocabulary(v[0]),v[1]));
			}
		});
		entitiesRDFa.push(annotations);
	});
	return entitiesRDFa;
}
function sortDESC(a, b){ return (b-a); }
//flag for text replacement, used to limit replacement to only one entity
var foundFlag=0;
function replaceText(oldText, newText, node){ 
	node = node || document.body; // base node 
	var childs = node.childNodes, i = 0;
	var temp;
	while(node = childs[i]){ 
		if (node.nodeType == 3){ // text node found, do the replacement
			if (node.textContent) {
				temp=node.textContent;
				if(!foundFlag){
					node.textContent = node.textContent.replace(oldText, newText);
				}
				if(temp!=node.textContent){
					foundFlag=1;
				}
			} else { // support to IE
				node.nodeValue = node.nodeValue.replace(oldText, newText);
			}
		} else { // not a text mode, look forward
			replaceText(oldText, newText, node); 
		} 
		i++; 
	} 
}
function enrichText(entities,txt,editor,text_based_replace,recEntities) {
	//handle overwriting of triples
	//get the list of exisitng annotated entities and add them to block arr to prevent overwriting them
	var notOverwrite=new Array();
	$.each($(editor.getDoc()).find('.r_entity'), function(index, value) {
		if(!$(this).hasClass("automatic")){
			notOverwrite.push(tinymce.trim($(this).text()));
		}
	});
	//-----------------------------
	var output= new Array();
	var enriched_text = txt;
	var extra_triples = '';
	if(!text_based_replace){
		//prepare positioning functions
		var sortArr=new Array();
		var nosortArr=new Array();
		$.each(entities, function(key, val) {
			nosortArr.push(val['start']);
		});
		$.each(nosortArr, function(ii, vv) {
			sortArr.push(vv);
		});
		sortArr.sort(sortDESC);
		var entitiesFinal=new Array();
		$.each(sortArr, function(i, v) {
			$.each(nosortArr, function(ii, vv) {
				if (vv == v) {
					var entityExtend=new Array();
					entityExtend["start"]=entities[ii]["start"];
					entityExtend["end"]=entities[ii]["end"];
					entityExtend["exact"]=entities[ii]["exact"];
					entityExtend["properties"]=entities[ii]["properties"];
					entityExtend["label"]=entities[ii]["label"];
					entityExtend["type"]=entities[ii]['type'];
					entityExtend["uri"]=entities[ii]['uri'];
					entitiesFinal.push(entityExtend);
				}
			});
		});
		entities=entitiesFinal;	
	}
	// Mapping to our desired vocabulary, here:rNews
	var entitiesRDFa = new Array();
	entitiesRDFa = makeRDFaTriples(entities);	
	//replace the entities
	$.each(entities, function(key, val) {
	//limit the results to entities selected by user
	if(recEntities.indexOf(val['type'].split(':')[1])!=-1){
		var selectedContent=val['label'];
		var start=val['start'];
		var end=val['end'];
		if(!text_based_replace){
			var selectedContent=val['exact'];
		}
		if(notOverwrite.indexOf(selectedContent)==-1){
			var subjectURI='';
			var dataReceived;
			if(val['uri']){
				subjectURI=val['uri'];
			}else{
				// get an URI
				//var data = "api="+getCookie("uriSuggestor")+"&query=" + selectedContent;
				//subjectURI=suggestURI(proxy_url,data,true);
			}
			var tmp2='';
			var annotatedContent,extra_triples;
			extra_triples='';
			//different replacement for RDFa and Microdata
			if(getCookie("annotationF")=="RDFa"){
				//replacement for RDFa
				if (subjectURI){
					tmp2="resource="+subjectURI;
				}
				$.each(entitiesRDFa[key], function(ii, vv) {
					if (vv[0]=="rdf:type"){
						var entity_type=vv[1].split(':')[1];
						entity_type='r_'+entity_type.toLowerCase()
						var temp = tmp2 + " typeof='"
						+ vv[1] + "'";
						annotatedContent = "<span class='r_entity "+entity_type+" automatic' " + temp + ">";

					}else{
						if(vv[0]=="schema:name"){
							extra_triples = extra_triples + "<span property='schema:name'>"+selectedContent+"</span>";
						}else{
							extra_triples = extra_triples + "<span property='" + vv[0]
							+ "' content='" + vv[1] + "'></span>";
						}
					}
				});
			}else{
				//replacement for Micodata Schema.org format
				if (subjectURI){
					tmp2="itemid="+subjectURI;
				}
				$.each(entitiesRDFa[key], function(ii, vv) {
					if (vv[0]=="rdf:type"){
						var entity_type=vv[1].split(':')[1];
						entity_type='r_'+entity_type.toLowerCase()
						var temp = tmp2 + " itemtype='"
						+ mapTypeToSchema(vv[1].split(':')[1]) + "'";
						annotatedContent = "<span itemscope class='r_entity "+entity_type+" automatic' " + temp + ">";

					}else{
						if(vv[0]=="schema:name"){
							extra_triples = extra_triples + "<span itemprop='name'>"+selectedContent+"</span>";
						}else{
							if(vv[0]=="schema:point"){
								extra_triples = extra_triples + "<meta itemprop='latitude' content='" + vv[1].split(' ')[0] + "'><meta itemprop='longitude' content='" + vv[1].split(' ')[1]  + "'>";
							}else{
								extra_triples = extra_triples + "<meta itemprop='" + vv[0].split(':')[1]
							+ "' content='" + vv[1] + "'>";
							}
						}
					}
				});				
			}
			annotatedContent=annotatedContent+extra_triples+"</span>";
			if(!text_based_replace){
				enriched_text=enriched_text.substring(0,start)+annotatedContent+enriched_text.substring(end,enriched_text.length+1);
			}else{
				foundFlag=0;
				replaceText(selectedContent, annotatedContent, $(editor.getDoc()).find('body')[0]);
			}
		}
	}
	});
	if(text_based_replace){
		var tmp=$(editor.getDoc()).find('body').html();
		tmp=tmp.replace(/&lt;/g,"<");
		tmp=tmp.replace(/&gt;/g,">");
		enriched_text=tmp;
	}
	return enriched_text;
}
function mapCalaisOutputToStandard(txt,proxy_url,exclude_arr){
	var excludeFlag=false;
	if(exclude_arr){
		excludeFlag=true;
	}
	var dataReceived;
	var data = encodeURIComponent(txt);
	data = "api=Calais&query=" + data;
	dataReceived=connectEnricherAPI(proxy_url,data);
	//terminate if an error occured
	if(!dataReceived)
		return 0;
	var entities = new Array();
	var entitiesComplete = new Array();
	// this step must be done manually for each NLP API
	$.each(dataReceived, function(key, val) {
		var entity = new Array();
		var properties=new Array();
		if (val['_typeGroup']=="entities"){
			// separate desired entities
			if((val['_type']=="Person")|| (val['_type']=="City")|| (val['_type']=="Country")|| (val['_type']=="Company")|| (val['_type']=="Organization")){
				entity["type"]=val['_type'];
				entity["label"]=val['instances'][0]['exact'];
				entity["uri"]='';
				if(val['resolutions']){
					entity["uri"]=val['resolutions'][0]['id'];
					if((val['_type']=="Country") || (val['_type']=="City")){
						//properties.push(Array("rnews:point",val['resolutions'][0]['latitude']+' '+ val['resolutions'][0]['longitude']));
						//properties.push(Array("rnews:addressCountry",val['resolutions'][0]['containedbycountry']));
					}
				}
				$.each(val['instances'], function(i, v) {
					entity["start"]=parseInt(v['offset']);
					entity["end"]=parseInt(v['offset']+v['length']);
					entity["exact"]=txt.substring(entity["start"], entity["end"]);
				});
				// add a property
				properties.push(Array("name",val['name']));
				entity["properties"]=properties;
				entitiesComplete.push(entity);
				if(excludeFlag){
					if(exclude_arr.indexOf(entity['label']) ==-1){
						entities.push(entity);	
					}
				}else{
					entities.push(entity);
				}
			}
		}
	});
	return Array(entities,entitiesComplete);
}
function mapOntosOutputToStandard(txt,proxy_url,exclude_arr){
	var excludeFlag=false;
	if(exclude_arr){
		excludeFlag=true;
	}
	var data = JSON.stringify( {
		get : 'process',
		ontology : 'common.english',
		format : 'NTRIPLES',
		text : txt
	});
	data = encodeURIComponent(data);
	data = "api=Ontos&query=" + data;
	var dataReceived;
	dataReceived=connectEnricherAPI(proxy_url,data);
	//terminate if an error occured
	if(!dataReceived)
		return 0;	
	var results = dataReceived["result"];
	var entities = new Array();
	var entitiesComplete = new Array();
	// this step must be done manually for each NLP API
	$.each(results, function(key, val) {
		var entity = new Array();
		// separate desired entities
		if((val['o'] == ontos_personURI)|| (val['o'] == ontos_organizationURI1) || (val['o'] == ontos_organizationURI2) || (val['o'] == ontos_organizationURI3) || (val['o'] == ontos_organizationURI4) || (val['o'] == ontos_organizationURI5) || (val['o'] == ontos_organizationURI6) || (val['o'] == ontos_organizationURI7) || (val['o'] == ontos_organizationURI8)|| (val['o'] == ontos_locationURI)){
			entity["type"]=val['o'];
			entity["uri"]=val['s'];
			entities.push(entity);
		}
	});
	var entitiesAnn = new Array();
	var tmp;
	// find and store all relations related to predefined
	// entities
	// && find
	// annotation entity of them
	var del_arr=new Array();
	$.each(entities, function(i, v) {
		properties = new Array();
		var pos=new Array();
		var tempArr=new Array();
		$.each(results, function(key, val) {
			if (val['s'] == v["uri"] || val['o'] == v["uri"]) {
				// get annotation entity
				if (val['p'] == ontos_annotation) {
					pos.push(val['s']);
				}else{
					tmp=val['o'].replace(/(\^\^)<.*?>/g,"");
					tmp=tmp.substr(1, tmp.length - 2);
					if(tempArr.indexOf(val['p'])==-1){
						properties.push(Array(val['p'],tmp));
					}
					tempArr.push(val['p']);
					if(val['p'] ==ontos_labelURI){
						v["label"]=tmp;
					}
				}

			}
		});
		entitiesAnn[i] = pos;
		v["properties"]=properties;
	});
	var start,end;
	var entities2=new Array();
	$.each(entities, function(i, v) {
		start="";
		end="";
		v["start"]=new Array();
		$.each(entitiesAnn[i], function(keyy, vall) {
			$.each(results, function(key, val) {
				if (val['s'] == vall) {
					if (val['p'] == ontos_startPosition) {
						tmp=val['o'].replace(/(\^\^)<.*?>/g, "");
						start=tmp.substr(1, tmp.length - 2) ;
					}
					if (val['p'] == ontos_endPosition) {
						tmp=val['o'].replace(/(\^\^)<.*?>/g, "");
						end=tmp.substr(1, tmp.length - 2) ;
					}
				}
			});
			if(start && end){
				v["start"].push(start);
				v["exact"]=txt.substring(start, end);
				//create new array for replacement
				var entityExtend=new Array();
				entityExtend["start"]=parseInt(start);
				entityExtend["end"]=parseInt(end);
				entityExtend["exact"]=txt.substring(start, end);
				entityExtend["properties"]=v["properties"];
				entityExtend["label"]=v["label"];
				entityExtend["type"]=v['type'];
				entityExtend["uri"]=v['uri'];
				entities2.push(entityExtend);
			}
		});
	});
	entities=entities2;
	entitiesComplete=entitiesComplete.concat(entities);
	if(excludeFlag){
		clearEntities=new Array();
		$.each(entities, function(i, v) {
			if(exclude_arr.indexOf(v["label"]) ==-1){
				clearEntities.push(v);
			}
		});
		entities=clearEntities;
	}
	return Array(entities,entitiesComplete);
}
function mapDBpediaOutputToStandard(txt,proxy_url,exclude_arr){
	var excludeFlag=false;
	if(exclude_arr){
		excludeFlag=true;
	}
	var dataReceived;
	var data = encodeURIComponent(txt);
	data = "api=DBpedia&query=" + data;
	dataReceived=connectEnricherAPI(proxy_url,data);
	//terminate if an error occured
	if(!dataReceived)
		return 0;	
	var entities = new Array();
	var entitiesComplete = new Array();
	// this step must be done manually for each NLP API
	var includeArr=new Array();
	$.each(dataReceived['Resources'], function(key, val) {
		var entity = new Array();
		var properties=new Array();
		// separate desired entities
		var tmp=val['@types'];
		var personReg = new RegExp("Person");
		var orgReg = new RegExp("Organisation");
		var locationReg = new RegExp("Place");
		var m1 = personReg.exec(tmp);
		var m2 = orgReg.exec(tmp);
		var m3 = locationReg.exec(tmp);
		if ((m1 != null) || (m2 != null) || (m3 != null)) {
			if(includeArr.indexOf(val['@surfaceForm']) ==-1){
				includeArr.push(val['@surfaceForm']);
				if (m1 != null){
					entity["type"]="Person";
				}
				if (m2 != null){
					entity["type"]="Organization";
				}
				if (m3 != null){
					entity["type"]="Location";
				}
				entity["label"]=val['@surfaceForm'];
				entity["uri"]=val['@URI'];
				// add a property
				properties.push(Array("name",val['@surfaceForm']));
				entity["start"]=parseInt(val['@offset']);
				entity["end"]=parseInt(val['@offset'])+val['@surfaceForm'].length;
				entity["exact"]=txt.substring(entity["start"], entity["end"]);
				entity["properties"]=properties;
				entitiesComplete.push(entity);
				if(excludeFlag){
					if(exclude_arr.indexOf(entity['label']) ==-1){
						entities.push(entity);	
					}
				}else{
					entities.push(entity);
				}
			}
		}
	});
	return Array(entities,entitiesComplete);
}
function mapAlchemyOutputToStandard(txt,proxy_url,exclude_arr){
	var excludeFlag=false;
	if(exclude_arr){
		excludeFlag=true;
	}
	var dataReceived;
	var data = encodeURIComponent(txt);
	data = "api=Alchemy&query=" + data;
	dataReceived=connectEnricherAPI(proxy_url,data);
	//terminate if an error occured
	if(!dataReceived)
		return 0;
	var entities = new Array();
	var entitiesComplete = new Array();
	// this step must be done manually for each NLP API
	$.each(dataReceived['entities'], function(key, val) {
		var entity = new Array();
		var positions=new Array();
		var properties=new Array();
		// separate desired entities
		if((val['type']=="Person")|| (val['type']=="City")|| (val['type']=="Country")|| (val['type']=="Organization")|| (val['type']=="Company")){
			entity["type"]=val['type'];
			entity["label"]=val['text'];
			entity["uri"]='';
			if(val['disambiguated']){
				entity["uri"]=val['disambiguated']['dbpedia'];
			}
			// add a property
			properties.push(Array("name",val['text']));
			//Alchemy does not return positions!
			entity["positions"]=positions;
			entity["properties"]=properties;
			entitiesComplete.push(entity);
			if(excludeFlag){
				if(exclude_arr.indexOf(entity['label']) ==-1){
					entities.push(entity);	
				}
			}else{
				entities.push(entity);
			}
		}
	});
	return Array(entities,entitiesComplete);
}
function mapExtractivOutputToStandard(txt,proxy_url,exclude_arr){
	var excludeFlag=false;
	if(exclude_arr){
		excludeFlag=true;
	}
	var dataReceived;
	var data = encodeURIComponent(txt);
	data = "api=Extractiv&query=" + data;
	dataReceived=connectEnricherAPI(proxy_url,data);
	//terminate if an error occured
	if(!dataReceived)
		return 0;	
	var entities = new Array();
	var entitiesComplete = new Array();
	// to prevent duplicates
	var labels=new Array();
	// this step must be done manually for each NLP API
	$.each(dataReceived['entities'], function(key, val) {
		var entity = new Array();
		var properties=new Array();
		// separate desired entities
		if((val['type']=="PERSON")|| (val['type']=="CITY")|| (val['type']=="COUNTRY")|| (val['type'].split("_")[1]=="ORG")|| (val['type'].split("_")[1]=="ORGANIZATION")){
			if(!val['pronoun']){
				// check duplicates
				if(labels.indexOf(val['text'])== -1){
					labels.push(val['text']);
					entity["type"]=val['type'];
					entity["label"]=val['text'];
					//entity["start"]=val['offset'];
					//entity["end"]=val['offset']+val['len']-1;
					entity["uri"]='';
					if(val['links']){
						entity["uri"]=val['links'][0];
					}
					// add a property
					properties.push(Array("name",val['text']));
					//Extractiv only returns positions by text content so ignores html content
					entity["properties"]=properties;
					entitiesComplete.push(entity);	
					if(excludeFlag){
						if(exclude_arr.indexOf(entity['label']) ==-1){
							entities.push(entity);	
						}
					}else{
						entities.push(entity);
					}
				}
			}
		}
	});
	return Array(entities,entitiesComplete);
}
function mapEvriOutputToStandard(txt,proxy_url,exclude_arr){
	var excludeFlag=false;
	if(exclude_arr){
		excludeFlag=true;
	}
	var dataReceived;
	var data = encodeURIComponent(txt);
	data = "api=Evri&query=" + data;
	dataReceived=connectEnricherAPI(proxy_url,data);
	//terminate if an error occured
	if(!dataReceived)
		return 0;	
	var entities = new Array();
	var entitiesComplete = new Array();
	// this step must be done manually for each NLP API
	$.each(dataReceived['graph']['entities']['entity'], function(key, val) {
		var entity = new Array();
		var positions=new Array();
		var properties=new Array();
		// separate desired entities
		if((val['@href'].split("/")[1]=="person")|| (val['@href'].split("/")[1]=="location")|| (val['@href'].split("/")[1]=="organization")){
			entity["type"]=val['@href'].split("/")[1];
			entity["label"]=val['name']['$'];
			entity["uri"]='http://api.evri.com'+val['@href'];
			// add a property
			properties.push(Array("name",val['name']['$']));
			//Evri does not return positions of entities
			entity["positions"]=positions;
			entity["properties"]=properties;
			entitiesComplete.push(entity);
			if(excludeFlag){
				if(exclude_arr.indexOf(entity['label']) ==-1){
					entities.push(entity);	
				}
			}else{
				entities.push(entity);
			}
		}
	});
	return Array(entities,entitiesComplete);
}
function mapLupediaOutputToStandard(txt,proxy_url,exclude_arr){
	var excludeFlag=false;
	if(exclude_arr){
		excludeFlag=true;
	}
	var dataReceived;
	var data = encodeURIComponent(txt);
	data = "api=Lupedia&query=" + data;
	dataReceived=connectEnricherAPI(proxy_url,data);
	//terminate if an error occured
	if(!dataReceived)
		return 0;
	var entities = new Array();
	var entitiesComplete = new Array();
	// this step must be done manually for each NLP API
	$.each(dataReceived, function(key, val) {
		var entity = new Array();
		var properties=new Array();
			// separate desired entities
			var temp=val['instanceClass'].split('/');
			var ent_type=temp[temp.length-1];
			if((ent_type=="Person")|| (ent_type=="City")|| (ent_type=="Town")|| (ent_type=="Town")|| (ent_type=="Country")|| (ent_type=="Company")|| (ent_type=="Organization")){
				entity["type"]=ent_type;
				entity["start"]=val['startOffset'];
				entity["end"]=val['endOffset'];
				entity["label"]=txt.substring(entity["start"],entity["end"]);
				entity["exact"]=entity["label"];
				entity["uri"]=val['instanceUri']?val['instanceUri']:'';
				// add a property
				properties.push(Array("name",val['label']));
				entity["properties"]=properties;
				entitiesComplete.push(entity);
				if(excludeFlag){
					if(exclude_arr.indexOf(entity['label']) ==-1){
						entities.push(entity);	
					}
				}else{
					entities.push(entity);
				}
		}
	});
	return Array(entities,entitiesComplete);
}
function mapSaploOutputToStandard(txt,proxy_url,exclude_arr){
	var excludeFlag=false;
	if(exclude_arr){
		excludeFlag=true;
	}
	var dataReceived;
	var data = encodeURIComponent(txt);
	data = "api=Saplo&query=" + data;
	dataReceived=connectEnricherAPI(proxy_url,data);
	//terminate if an error occured
	if(!dataReceived)
		return 0;	
	var entities = new Array();
	var entitiesComplete = new Array();
	// this step must be done manually for each NLP API
	$.each(dataReceived['result']['tags'], function(key, val) {
		var entity = new Array();
		var positions=new Array();
		var properties=new Array();
		// separate desired entities
		if((val['category']=="person")|| (val['category']==="location")|| (val['category']==="organization")){
			entity["type"]=val['category'];
			entity["label"]=val['tag'];
			entity["uri"]='';
			// add a property
			properties.push(Array("name",val['tag']));
			//Evri does not return positions of entities
			entity["positions"]=positions;
			entity["properties"]=properties;
			entitiesComplete.push(entity);
			if(excludeFlag){
				if(exclude_arr.indexOf(entity['label']) ==-1){
					entities.push(entity);	
				}
			}else{
				entities.push(entity);
			}
		}
	});
	return Array(entities,entitiesComplete);
}
function handleAutomaticAnnotation(editor){
var a=editor;
var entities= new Array();
var selectedArray = new Array();
var recEntities = new Array();
var combination="no";
//get the content
var txt = a.getContent();
//var raw_txt= $(a.getDoc()).text();
// add namespaces 
var ns =a.dom.get('namespaces');
var tmp='';
var nsStart;
var nsEnd;
$.each(vocabularies, function(key, val) {
	var nsURI = popular_prefixes[val];
	tmp += val + ': ' + nsURI+ ' ';
});			
if(ns){
	txt=ns.innerHTML;
	nsStart = "";
	nsEnd="";
}else{
	nsStart = "<div id='namespaces' prefix='" + tmp + "'>";
	nsEnd="</div>";
}
//determine if replacement is based on the positions or only is working by text replacement
var text_based_replace=1;
//entities to be recognized
if(!getCookie("recEntities")){
	// set all entities to be found
	recEntities.push("Place");
	recEntities.push("Person");
	recEntities.push("Organization");
	setCookie("recEntities","Place,Person,Organization",30);
}else{
	recEntities=getCookie("recEntities").split(",");
}
if(!getCookie("NLPAPI")){
	// set DBPedia as default API
	selectedArray.push("Alchemy");
	setCookie("NLPAPI","Alchemy",30);
}else{
	selectedArray=getCookie("NLPAPI").split(",");
}
if(getCookie("combination")){
	combination=getCookie("combination");
}
var API_name;
if(selectedArray.length==1){
	API_name=selectedArray[0];
}else{
	API_name="multiple";
}
var entity= new Array();
if(API_name=="multiple"){
	// chain the output result of different APIs
	var i,exclude_arr=false;
	//errors in APIS
	var error_index=new Array();
	for (i=0; i<selectedArray.length; i++) {
		try
		{
			entity[i]=mapOutputToStandard(selectedArray[i],txt,proxy_url,exclude_arr);
			if(!entity[i]){
				$('table img[alt="Automatic Content Annotation"]').parent().append("<p class='auto-tooltip'>Error in receiving information from <b>"+selectedArray[i]+"</b>!</p>");
				error_index.push(i);
				continue;
			}
			$('table img[alt="Automatic Content Annotation"]').parent().append("<p class='auto-tooltip'>Information received from <b>"+selectedArray[i]+"</b></p>");
			entities=entities.concat(entity[i][0]);
			exclude_arr=new Array();
			$.each(entities, function(key, val) {
				exclude_arr.push(val['label']);
			});
		}
		catch(err)
		{
			//Handle errors
			//$("span#ann_result").append("->Error in receiving information from <font color='red'>"+selectedArray[i]+"</font>!<br> ");
			return false;
		}
	}
	var isThere,entityType;
	for (i=0; i<selectedArray.length; i++) {
		$.each(entities, function(key, val) {
		if(error_index.indexOf(key)==-1){
			isThere=0;
			entityType=0;
			if(error_index.indexOf(i)==-1){
				$.each(entity[i][1], function(key2, val2) {
					if (val2['label']==val['label']){
						isThere=1; 
						entityType=val2['type'];
					}
				});  
				val[selectedArray[i]]= new Array(isThere,entityType); 
			}
		}
	});
	}
	//apply combination strategy
	if(combination!="no"){
		var agreementNo;
		switch(combination){
		case "two":
			agreementNo=2;
			break;
		case "three":
			agreementNo=3;
			break;
		case "four":
			agreementNo=4;
			break;
		case "five":
			agreementNo=5;
			break;
		}					
		var entities_filtered= new Array();
		var location_count,org_count,person_count;
		$.each(entities, function(key, val) {
		if(error_index.indexOf(key)==-1){
			var countAgree=0;
			var temp_arr= new Array();
			for (i=0; i<selectedArray.length; i++) {
				if((error_index.indexOf(i)==-1) && val[selectedArray[i]][0]){
					temp_arr.push(mapToVocabulary(val[selectedArray[i]][1]));
				}
			}
			location_count=0;
			org_count=0;
			person_count=0;
			$.each(temp_arr, function(k, v) {
				if(v=="schema:Place"){
					location_count++;
				}
				if(v=="schema:Person"){
					person_count++;
				}
				if(v=="schema:Organization"){
					org_count++;
				}
			});
			if(location_count>agreementNo-1 || person_count>agreementNo-1 || org_count>agreementNo-1){
				entities_filtered.push(val);
			}
		}
		});
		entities=entities_filtered;
	}
}else{
	if(API_name=="Calais"){
		text_based_replace=0;
		entities=mapOutputToStandard(API_name,txt,proxy_url,false)[0];
	}
	if(API_name=="Ontos"){
		text_based_replace=0;
		entities=mapOutputToStandard(API_name,txt,proxy_url,false)[0];
	}			
	if(API_name=="DBpedia"){
		//dbpedia works only on raw text
		entities=mapOutputToStandard(API_name,txt,proxy_url,false)[0];
	}
	if(API_name=="Alchemy"){
		// no offsets returned
		entities=mapOutputToStandard(API_name,txt,proxy_url,false)[0];
	}
	if(API_name=="Extractiv"){
		//works only on raw text
		entities=mapOutputToStandard(API_name,txt,proxy_url,false)[0];
	}
	if(API_name=="Evri"){
		// no offsets returned
		entities=mapOutputToStandard(API_name,txt,proxy_url,false)[0];
	}
	if(API_name=="Lupedia"){
		text_based_replace=0;
		entities=mapOutputToStandard(API_name,txt,proxy_url,false)[0];
	}				
	if(API_name=="Saplo"){
		// no offsets returned
		entities=mapOutputToStandard(API_name,txt,proxy_url,false)[0];
	}								
}
// ------------------------------------------------------------
// enrich the text
var enriched_text=enrichText(entities,txt,a,text_based_replace,recEntities);
// -------------------------------------------------
if(getCookie("annotationF")=="RDFa"){
	a.setContent(nsStart+enriched_text+nsEnd);
}else{
	a.setContent(enriched_text);
}

a.nodeChanged();
//a.execCommand('mceRdfaHighlight',false,'');
}
function activateAjaxIndicator(b){
//animate the button --selected by image alt
/* Gets called when request starts */
	$('table img[alt="Automatic Content Annotation"]').ajaxStart(function() {
		$(this).attr('src',b + "/img/ajax.gif");
	});
/* Gets called when request complete */
	$('table img[alt="Automatic Content Annotation"]').ajaxComplete(function() {
		$(this).attr('src',b + "/img/connect.png");
		$('.auto-tooltip').remove();
	});
}
//list of popular namespace prefixes
var popular_prefixes ={ 
		  "rnews": "http:\/\/www.iptc.org\/std\/rNews\/1.0\/",
		  "foaf": "http:\/\/xmlns.com\/foaf\/0.1\/",
		  "dc": "http:\/\/purl.org\/dc\/elements\/1.1\/",
		  "schema": "http:\/\/schema.org\/",
		  "owl": "http:\/\/www.w3.org\/2002\/07\/owl#",
		  "rdf": "http:\/\/www.w3.org\/1999\/02\/22-rdf-syntax-ns#",
		  "rdfs": "http:\/\/www.w3.org\/2000\/01\/rdf-schema#",
		  "dbp": "http:\/\/dbpedia.org\/property\/",
		  "d2rq": "http:\/\/www.wiwiss.fu-berlin.de\/suhl\/bizer\/D2RQ\/0.1#",
		  "swrc": "http:\/\/swrc.ontoware.org\/ontology#",
		  "test2": "http:\/\/this.invalid\/test2#",
		  "skos": "http:\/\/www.w3.org\/2004\/02\/skos\/core#",
		  "sioc": "http:\/\/rdfs.org\/sioc\/ns#",
		  "ex": "http:\/\/example.org\/",
		  "nie": "http:\/\/www.semanticdesktop.org\/ontologies\/2007\/01\/19\/nie#",
		  "xhtml": "http:\/\/www.w3.org\/1999\/xhtml\/vocab#",
		  "xsd": "http:\/\/www.w3.org\/2001\/XMLSchema#",
		  "content": "http:\/\/purl.org\/rss\/1.0\/modules\/content\/",
		  "xs": "http:\/\/www.w3.org\/2001\/XMLSchema#",
		  "sioct": "http:\/\/rdfs.org\/sioc\/types#",
		  "exif": "http:\/\/www.w3.org\/2003\/12\/exif\/ns#",
		  "bio": "http:\/\/purl.org\/vocab\/bio\/0.1\/",
		  "rss": "http:\/\/purl.org\/rss\/1.0\/",
		  "geo": "http:\/\/www.w3.org\/2003\/01\/geo\/wgs84_pos#",
		  "dcterms": "http:\/\/purl.org\/dc\/terms\/",
		  "umbel": "http:\/\/umbel.org\/umbel#",
		  "swc": "http:\/\/data.semanticweb.org\/ns\/swc\/ontology#",
		  "rel": "http:\/\/purl.org\/vocab\/relationship\/",
		  "dct": "http:\/\/purl.org\/dc\/terms\/",
		  "xhv": "http:\/\/www.w3.org\/1999\/xhtml\/vocab#",
		  "rev": "http:\/\/purl.org\/stuff\/rev#",
		  "psych": "http:\/\/purl.org\/vocab\/psychometric-profile\/",
		  "void": "http:\/\/rdfs.org\/ns\/void#",
		  "pimo": "http:\/\/www.semanticdesktop.org\/ontologies\/2007\/11\/01\/pimo#",
		  "vann": "http:\/\/purl.org\/vocab\/vann\/",
		  "log": "http:\/\/www.w3.org\/2000\/10\/swap\/log#",
		  "cc": "http:\/\/creativecommons.org\/ns#",
		  "daml": "http:\/\/www.daml.org\/2001\/03\/daml+oil#",
		  "biol": "http:\/\/purl.org\/NET\/biol\/ns#",
		  "mo": "http:\/\/purl.org\/ontology\/mo\/",
		  "label": "http:\/\/purl.org\/net\/vocab\/2004\/03\/label#",
		  "gpt": "http:\/\/purl.org\/vocab\/riro\/gpt#",
		  "dbpedia": "http:\/\/dbpedia.org\/resource\/",
		  "doap": "http:\/\/usefulinc.com\/ns\/doap#",
		  "akt": "http:\/\/www.aktors.org\/ontology\/portal#",
		  "jdbc": "http:\/\/d2rq.org\/terms\/jdbc\/",
		  "event": "http:\/\/purl.org\/NET\/c4dm\/event.owl#",
		  "ical": "http:\/\/www.w3.org\/2002\/12\/cal\/icaltzd#",
		  "dctype": "http:\/\/purl.org\/dc\/dcmitype\/",
		  "coref": "http:\/\/www.rkbexplorer.com\/ontologies\/coref#",
		  "doclist": "http:\/\/www.junkwork.net\/xml\/DocumentList#",
		  "math": "http:\/\/www.w3.org\/2000\/10\/swap\/math#",
		  "dir": "http:\/\/schemas.talis.com\/2005\/dir\/schema#",
		  "akts": "http:\/\/www.aktors.org\/ontology\/support#",
		  "courseware": "http:\/\/courseware.rkbexplorer.com\/ontologies\/courseware#",
		  "usgov": "http:\/\/www.rdfabout.com\/rdf\/schema\/usgovt\/",
		  "scovo": "http:\/\/purl.org\/NET\/scovo#",
		  "dailymed": "http:\/\/www4.wiwiss.fu-berlin.de\/dailymed\/resource\/dailymed\/",
		  "drugbank": "http:\/\/www4.wiwiss.fu-berlin.de\/drugbank\/resource\/drugbank\/",
		  "lib": "http:\/\/schemas.talis.com\/2005\/library\/schema#",
		  "scv": "http:\/\/purl.org\/NET\/scovo#",
		  "frbre": "http:\/\/purl.org\/vocab\/frbr\/extended#",
		  "dummy": "http:\/\/hello.com\/",
		  "audio": "http:\/\/purl.org\/media\/audio#",
		  "sdl": "http:\/\/purl.org\/vocab\/riro\/sdl#",
		  "xen": "http:\/\/buzzword.org.uk\/rdf\/xen#",
		  "contact": "http:\/\/www.w3.org\/2000\/10\/swap\/pim\/contact#",
		  "resex": "http:\/\/resex.rkbexplorer.com\/ontologies\/resex#",
		  "atom": "http:\/\/www.w3.org\/2005\/Atom\/",
		  "ad": "http:\/\/schemas.talis.com\/2005\/address\/schema#",
		  "imm": "http:\/\/schemas.microsoft.com\/imm\/",
		  "kwijibo": "http:\/\/kwijibo.talis.com\/",
		  "ok": "http:\/\/okkam.org\/terms#",
		  "eztag": "http:\/\/ontologies.ezweb.morfeo-project.org\/eztag\/ns#",
		  "bibo": "http:\/\/purl.org\/ontology\/bibo\/",
		  "ddl": "http:\/\/purl.org\/vocab\/riro\/ddl#",
		  "ov": "http:\/\/open.vocab.org\/terms\/",
		  "ezcontext": "http:\/\/ontologies.ezweb.morfeo-project.org\/ezcontext\/ns#",
		  "vcard": "http:\/\/www.w3.org\/2006\/vcard\/ns#",
		  "sv": "http:\/\/schemas.talis.com\/2005\/service\/schema#",
		  "frbr": "http:\/\/purl.org\/vocab\/frbr\/core#",
		  "resist": "http:\/\/www.rkbexplorer.com\/ontologies\/resist#",
		  "acm": "http:\/\/www.rkbexplorer.com\/ontologies\/acm#",
		  "user": "http:\/\/schemas.talis.com\/2005\/user\/schema#",
		  "music": "http:\/\/musicontology.com\/",
		  "atomix": "http:\/\/buzzword.org.uk\/rdf\/atomix#",
		  "aiiso": "http:\/\/purl.org\/vocab\/aiiso\/schema#",
		  "phss": "http:\/\/ns.poundhill.com\/phss\/1.0\/",
		  "memo": "http:\/\/ontologies.smile.deri.ie\/2009\/02\/27\/memo#",
		  "sesame": "http:\/\/www.openrdf.org\/schema\/sesame#",
		  "lom": "http:\/\/ltsc.ieee.org\/rdf\/lomv1p0\/lom#",
		  "myspo": "http:\/\/purl.org\/ontology\/myspace#",
		  "h5": "http:\/\/buzzword.org.uk\/rdf\/h5#",
		  "http": "http:\/\/www.w3.org\/2006\/http#",
		  "media": "http:\/\/purl.org\/media#",
		  "plink": "http:\/\/buzzword.org.uk\/rdf\/personal-link-types#",
		  "lomvoc": "http:\/\/ltsc.ieee.org\/rdf\/lomv1p0\/vocabulary#",
		  "lingvoj": "http:\/\/www.lingvoj.org\/ontology#",
		  "product": "http:\/\/purl.org\/commerce\/product#",
		  "botany": "http:\/\/purl.org\/NET\/biol\/botany#",
		  "commerce": "http:\/\/purl.org\/commerce#",
		  "video": "http:\/\/purl.org\/media\/video#",
		  "zoology": "http:\/\/purl.org\/NET\/biol\/zoology#",
		  "cs": "http:\/\/purl.org\/vocab\/changeset\/schema#",
		  "airport": "http:\/\/www.daml.org\/2001\/10\/html\/airport-ont#",
		  "geonames": "http:\/\/www.geonames.org\/ontology#",
		  "ptr": "http:\/\/www.w3.org\/2009\/pointers#",
		  "po": "http:\/\/purl.org\/ontology\/po\/",
		  "grddl": "http:\/\/www.w3.org\/2003\/g\/data-view#",
		  "gold": "http:\/\/purl.org\/linguistics\/gold\/",
		  "dcam": "http:\/\/purl.org\/dc\/dcam\/",
		  "book": "http:\/\/purl.org\/NET\/book\/vocab#",
		  "xhe": "http:\/\/buzzword.org.uk\/rdf\/xhtml-elements#",
		  "wot": "http:\/\/xmlns.com\/wot\/0.1\/",
		  "cnt": "http:\/\/www.w3.org\/2007\/content#",
		  "tl": "http:\/\/purl.org\/NET\/c4dm\/timeline.owl#",
		  "ttl": "http:\/\/www.w3.org\/2008\/turtle#",
		  "biblio": "http:\/\/purl.org\/net\/biblio#",
		  "vs": "http:\/\/www.w3.org\/2003\/06\/sw-vocab-status\/ns#",
		  "tag": "http:\/\/www.holygoat.co.uk\/owl\/redwood\/0.1\/tags\/",
		  "status": "http:\/\/www.w3.org\/2003\/06\/sw-vocab-status\/ns#",
		  "mit": "http:\/\/purl.org\/ontology\/mo\/mit#",
		  "doc": "http:\/\/www.w3.org\/2000\/10\/swap\/pim\/doc#",
		  "scot": "http:\/\/scot-project.org\/scot\/ns#",
		  "time": "http:\/\/www.w3.org\/2006\/time#",
		  "dcmitype": "http:\/\/purl.org\/dc\/dcmitype\/",
		  "org": "http:\/\/www.w3.org\/2001\/04\/roadmap\/org#",
		  "tags": "http:\/\/www.holygoat.co.uk\/owl\/redwood\/0.1\/tags\/",
		  "taxo": "http:\/\/purl.org\/rss\/1.0\/modules\/taxonomy\/",
		  "dbo": "http:\/\/dbpedia.org\/ontology\/",
		  "ddc": "http:\/\/purl.org\/NET\/decimalised#",
		  "con": "http:\/\/www.w3.org\/2000\/10\/swap\/pim\/contact#",
		  "m": "http:\/\/www.kanzaki.com\/ns\/music#",
		  "moat": "http:\/\/moat-project.org\/ns#",
		  "xfn": "http:\/\/vocab.sindice.com\/xfn#",
		  "gen": "http:\/\/www.w3.org\/2006\/gen\/ont#",
		  "ibis": "http:\/\/purl.org\/ibis#",
		  "dbpprop": "http:\/\/dbpedia.org\/property\/",
		  "states": "http:\/\/www.w3.org\/2005\/07\/aaa#",
		  "lifecycle": "http:\/\/purl.org\/vocab\/lifecycle\/schema#",
		  "wairole": "http:\/\/www.w3.org\/2005\/01\/wai-rdf\/GUIRoleTaxonomy#",
		  "lfm": "http:\/\/purl.org\/ontology\/last-fm\/",
		  "lastfm": "http:\/\/purl.org\/ontology\/last-fm\/",
		  "prj": "http:\/\/purl.org\/stuff\/project\/",
		  "xhtmlvocab": "http:\/\/www.w3.org\/1999\/xhtml\/vocab\/",
		  "resource": "http:\/\/purl.org\/vocab\/resourcelist\/schema#",
		  "spin": "http:\/\/spinrdf.org\/spin#",
		  "spl": "http:\/\/spinrdf.org\/spl#",
		  "list": "http:\/\/www.w3.org\/2000\/10\/swap\/list#",
		  "sp": "http:\/\/spinrdf.org\/sp#",
		  "string": "http:\/\/www.w3.org\/2000\/10\/swap\/string#",
		  "crypto": "http:\/\/www.w3.org\/2000\/10\/swap\/crypto#",
		  "os": "http:\/\/www.w3.org\/2000\/10\/swap\/os#",
		  "timeline": "http:\/\/purl.org\/NET\/c4dm\/timeline.owl#",
		  "e": "http:\/\/eulersharp.sourceforge.net\/2003\/03swap\/log-rules#",
		  "cv": "http:\/\/ontologi.es\/colour\/vocab#",
		  "wn": "http:\/\/xmlns.com\/wordnet\/1.6\/",
		  "climb": "http:\/\/climb.dataincubator.org\/vocabs\/climb\/",
		  "nrl": "http:\/\/www.semanticdesktop.org\/ontologies\/2007\/08\/15\/nrl#",
		  "custom": "http:\/\/www.openrdf.org\/config\/sail\/custom#",
		  "giving": "http:\/\/ontologi.es\/giving#",
		  "cert": "http:\/\/www.w3.org\/ns\/auth\/cert#",
		  "doac": "http:\/\/ramonantonio.net\/doac\/0.1\/#",
		  "nao": "http:\/\/www.semanticdesktop.org\/ontologies\/2007\/08\/15\/nao#",
		  "air": "http:\/\/dig.csail.mit.edu\/TAMI\/2007\/amord\/air#",
		  "hlisting": "http:\/\/sindice.com\/hlisting\/0.1\/",
		  "gob": "http:\/\/purl.org\/ontology\/last-fm\/",
		  "dbr": "http:\/\/dbpedia.org\/resource\/",
		  "musim": "http:\/\/purl.org\/ontology\/musim#",
		  "nfo": "http:\/\/www.semanticdesktop.org\/ontologies\/2007\/03\/22\/nfo#",
		  "wisski": "http:\/\/wiss-ki.eu\/",
		  "gr": "http:\/\/purl.org\/goodrelations\/v1#",
		  "acl": "http:\/\/www.w3.org\/ns\/auth\/acl#",
		  "nid3": "http:\/\/www.semanticdesktop.org\/ontologies\/2007\/05\/10\/nid3#",
		  "tmo": "http:\/\/www.semanticdesktop.org\/ontologies\/2008\/05\/20\/tmo#",
		  "ncal": "http:\/\/www.semanticdesktop.org\/ontologies\/2007\/04\/02\/ncal#",
		  "nexif": "http:\/\/www.semanticdesktop.org\/ontologies\/2007\/05\/10\/nexif#",
		  "protege": "http:\/\/protege.stanford.edu\/system#",
		  "nco": "http:\/\/www.semanticdesktop.org\/ontologies\/2007\/03\/22\/nco#",
		  "rsa": "http:\/\/www.w3.org\/ns\/auth\/rsa#",
		  "nmo": "http:\/\/www.semanticdesktop.org\/ontologies\/2007\/03\/22\/nmo#",
		  "like": "http:\/\/ontologi.es\/like#",
		  "swh": "http:\/\/plugin.org.uk\/swh-plugins\/",
		  "u": "http:\/\/purl.org\/NET\/uri#",
		  "rdfg": "http:\/\/www.w3.org\/2004\/03\/trix\/rdfg-1\/",
		  "sparql": "http:\/\/www.openrdf.org\/config\/repository\/sparql#",
		  "skosxl": "http:\/\/www.w3.org\/2008\/05\/skos-xl#",
		  "uri": "http:\/\/purl.org\/NET\/uri#",
		  "fresnel": "http:\/\/www.w3.org\/2004\/09\/fresnel#",
		  "link": "http:\/\/www.w3.org\/2006\/link#",
		  "p3p": "http:\/\/www.w3.org\/2002\/01\/p3prdfv1#",
		  "rei": "http:\/\/www.w3.org\/2004\/06\/rei#",
		  "abc": "http:\/\/www.metadata.net\/harmony\/ABCSchemaV5Commented.rdf#",
		  "af": "http:\/\/purl.org\/ontology\/af\/",
		  "co": "http:\/\/purl.org\/ontology\/chord\/",
		  "chord": "http:\/\/purl.org\/ontology\/chord\/",
		  "mysql": "http:\/\/web-semantics.org\/ns\/mysql\/",
		  "so": "http:\/\/purl.org\/ontology\/symbolic-music\/",
		  "osoc": "http:\/\/web-semantics.org\/ns\/opensocial#",
		  "powder": "http:\/\/www.w3.org\/2007\/05\/powder#",
		  "ctag": "http:\/\/commontag.org\/ns#",
		  "meta": "http:\/\/www.openrdf.org\/rdf\/2009\/metadata#",
		  "sc": "http:\/\/umbel.org\/umbel\/sc\/",
		  "sr": "http:\/\/www.openrdf.org\/config\/repository\/sail#",
		  "obj": "http:\/\/www.openrdf.org\/rdf\/2009\/object#",
		  "sail": "http:\/\/www.openrdf.org\/config\/sail#",
		  "rep": "http:\/\/www.openrdf.org\/config\/repository#",
		  "fed": "http:\/\/www.openrdf.org\/config\/sail\/federation#",
		  "bsbm": "http:\/\/www4.wiwiss.fu-berlin.de\/bizer\/bsbm\/v01\/vocabulary\/",
		  "geographis": "http:\/\/telegraphis.net\/ontology\/geography\/geography#",
		  "money": "http:\/\/telegraphis.net\/ontology\/money\/money#",
		  "code": "http:\/\/telegraphis.net\/ontology\/measurement\/code#",
		  "imreg": "http:\/\/www.w3.org\/2004\/02\/image-regions#",
		  "factbook": "http:\/\/www4.wiwiss.fu-berlin.de\/factbook\/ns#",
		  "common": "http:\/\/www.w3.org\/2007\/uwa\/context\/common.owl#",
		  "swrl": "http:\/\/www.w3.org\/2003\/11\/swrl#",
		  "dcn": "http:\/\/www.w3.org\/2007\/uwa\/context\/deliveryContext.owl#",
		  "java": "http:\/\/www.w3.org\/2007\/uwa\/context\/java.owl#",
		  "hard": "http:\/\/www.w3.org\/2007\/uwa\/context\/hardware.owl#",
		  "swrlb": "http:\/\/www.w3.org\/2003\/11\/swrlb#",
		  "loc": "http:\/\/www.w3.org\/2007\/uwa\/context\/location.owl#",
		  "net": "http:\/\/www.w3.org\/2007\/uwa\/context\/network.owl#",
		  "wgspos": "http:\/\/www.w3.org\/2003\/01\/geo\/wgs84_pos#",
		  "push": "http:\/\/www.w3.org\/2007\/uwa\/context\/push.owl#",
		  "lgd": "http:\/\/linkedgeodata.org\/vocabulary#",
		  "web": "http:\/\/www.w3.org\/2007\/uwa\/context\/web.owl#",
		  "ac": "http:\/\/umbel.org\/umbel\/ac\/",
		  "soft": "http:\/\/www.w3.org\/2007\/uwa\/context\/software.owl#",
		  "sede": "http:\/\/eventography.org\/sede\/0.1\/",
		  "wv": "http:\/\/vocab.org\/waive\/terms\/",
		  "ne": "http:\/\/umbel.org\/umbel\/ne\/",
		  "lode": "http:\/\/linkedevents.org\/ontology\/",
		  "dcq": "http:\/\/purl.org\/dc\/terms\/",
		  "prv": "http:\/\/purl.org\/net\/provenance\/ns#",
		  "irw": "http:\/\/www.ontologydesignpatterns.org\/ont\/web\/irw.owl#",
		  "ir": "http:\/\/www.ontologydesignpatterns.org\/cp\/owl\/informationrealization.owl#",
		  "ire": "http:\/\/www.ontologydesignpatterns.org\/cpont\/ire.owl#"
		};
//list of rnews predefined attributes
var rnews_properties=["rnews:alternativeHeadline","rnews:copyrightNotice","rnews:copyrightYear","rnews:dateCreated","rnews:dateline",
		"rnews:dateModified","rnews:datePublished","rnews:description","rnews:genre","rnews:headline","rnews:identifier",
		"rnews:inLanguage","rnews:publishingPrinciples","rnews:usageTerms","rnews:version","rnews:articleBody",
		"rnews:articleSection","rnews:printColumn","rnews:printEdition","rnews:printPage","rnews:printSection","rnews:wordCount",
		"rnews:encodingFormat","rnews:height","rnews:width","rnews:duration","rnews:transcript","rnews:commentText",
		"rnews:commentTime","rnews:name","rnews:featureCode","rnews:box","rnews:circle","rnews:elevation",
		"rnews:line","rnews:point","rnews:polygon","rnews:additionalName","rnews:familyName","rnews:givenName","rnews:honorificPrefix",
		"rnews:honorificSuffix","rnews:tickerSymbol","rnews:addressCountry","rnews:addressLocality","rnews:addressRegion","rnews:email","rnews:faxNumber"
		,"rnews:postalCode","rnews:streetAddress","rnews:telephone","rnews:postOfficeBoxNumber"];
var rnews_rels=["rnews:discussionUrl","rnews:thumbnailUrl","rnews:replyToUrl","rnews:url"];
var rnews_typeofs=["rnews:PostalAddress","rnews:Place","rnews:Person","rnews:Organization",
                   "rnews:NewsItem","rnews:Article","rnews:ImageObject","rnews:AudioObject","rnews:VideoObject","rnews:UserComments","rnews:Concept", "rnews:GeoCoordinates"];
var rnews_contenttypes=["xsd:string","xsd:double","xsd:anyURI","xsd:dateTime","xsd:integer","xsd:nonNegativeInteger","owl:thing","xsd:duration"];
		
