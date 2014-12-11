tinyMCEPopup.requireLangPack();

var facts = {
		init : function() {
			var rootEl = tinyMCEPopup.editor.dom.getRoot();
			$("body").html(rootEl.innerHTML);
			$("body").append('<div id="output"></div>');
			RDFa.attach(document,true);
			document.data.setMapping("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#");
			document.data.setMapping("schema", "http://schema.org/");
			document.data.setMapping("dbpedia", "http://dbpedia.org/resource/");
			document.data.setMapping("rdfs", "http://www.w3.org/2000/01/rdf-schema#");
			var subjects=document.data.getSubjects();
			var tripleNo=0;
			var bg='';
			for(var i = 0; i < subjects.length; i++)
			{
			   var element = document.getElementsBySubject(subjects[i]);
			   for (var j=0; j<element.length; j++) {
				   //console.log(element[j].data);
				   $.each(element[j].data.predicates, function(key,value){
					   tripleNo++;
					   if(tripleNo%2==0){
						   bg="background-color:#fff;";
					   }else{
						   bg="background-color:#e7e7e7;";
					   }
					   //console.log();
					   $('#output').prepend('<div onmouseover="facts.highlightEditor(\''+subjects[i]+'\',\''+document.data.shorten(key)+'\',\''+encodeURIComponent(value.objects[0].value)+'\','+tripleNo+',0);" onmouseout="facts.highlightEditor(\''+subjects[i]+'\',\''+document.data.shorten(key)+'\',\''+encodeURIComponent(value.objects[0].value)+'\','+tripleNo+',1);" class="fact-triple" id="triple'+tripleNo+'" style="'+bg+'"><b>S</b>: <a href="'+subjects[i]+'" target="_blank"><span class="fact-subject">'+document.data.shorten(subjects[i])+'</span></a><br/> <b>P</b>: <span class="fact-predicate">'+document.data.shorten(key)+'</span><br/> <b>O</b>: <span class="fact-object">'+value+'</span></div><hr/>');
				   })
				   
				}
			   //var properties = document.data.getProperties(subjects[i]);
			}
			   $('#output').prepend('<center><b>'+tripleNo+'</b> triple(s) found.</center>');
			$("body").html($('#output').html());
			
		},
		highlightEditor : function(subject,predicate, object, i,reset) {
			if(reset)
				$("#triple"+i).css("background-color", "");
			else
				$("#triple"+i).css("background-color", "#eeff22");
			var querySt;
			var predicateType;
			if($.trim(predicate)=='rdf:type'){
				predicateType="typeof";
				querySt = "*[typeof='" + document.data.shorten(decodeURIComponent(object)) + "']";
			}else{
				predicateType="property";
				querySt = "*[property='" + predicate + "']";
			}
			//only one instance is there
			if($(tinyMCEPopup.editor.getDoc()).find(querySt).length==1){
				if(reset)
					$(tinyMCEPopup.editor.getDoc()).find(querySt).css("background-color", "");
				else
					$(tinyMCEPopup.editor.getDoc()).find(querySt).css("background-color", "#eeff22");
			}else{
				//we have to use the value or uri as well
				if(predicateType=='property'){
					$.each($(tinyMCEPopup.editor.getDoc()).find(querySt), function(key, value) {
						if ($(value).attr('content')) {
							if ($(value).attr('content') == decodeURIComponent(object)) {
								if(reset)
									$(value).css("background-color", "");
								else
									$(value).css("background-color", "#eeff22");
							}								
						} else {
							// manage tinymce redundant hidden attributes
							//object = object.replace(/\s(data-mce-href=)".*?"/g, "");
							//object = object.replace(/\s(xmlns=)".*?"/g, "");
							contentHTML=$(value).html();
							//contentHTML = contentHTML.replace(/\s(data-mce-href=)".*?"/g, "");
							//contentHTML = contentHTML.replace(/\s(xmlns=)".*?"/g, "");						
							if (contentHTML == decodeURIComponent(object)) {
								if(reset)
									$(value).css("background-color", "");
								else
									$(value).css("background-color", "#eeff22");
							}
						}
					});
				}else{
				$.each($(tinyMCEPopup.editor.getDoc()).find(querySt), function(key, value) {	
						if ($(value).attr('resource')==subject) {
							if(reset)
								$(value).css("background-color", "");
							else
								$(value).css("background-color", "#eeff22");
						}
				});			
			}
			}
	
		}
}
tinyMCEPopup.onInit.add(facts.init, facts);

