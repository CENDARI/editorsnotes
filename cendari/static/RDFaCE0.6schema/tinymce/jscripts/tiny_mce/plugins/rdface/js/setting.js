tinyMCEPopup.requireLangPack();
var rdfaSetting = {
		init : function() {	
			var f = document.getElementById('settingNLP');
			var f2 = document.getElementById('settingGeneral');
			var selectedArray = new Array();
			//default values
			if(!getCookie("annotationF")){
				f2.a_format[0].checked = true;
				setCookie("annotationF",f2.a_format[0].value,30);
			}		
			if(!getCookie("uriSuggestor")){
				f2.uri_suggestor[0].checked = true;
				setCookie("uriSuggestor",f2.uri_suggestor[0].value,30);
			}	
			if(!getCookie("recEntities")){
				f2.place.checked = true;
				f2.person.checked = true;
				f2.org.checked = true;
				setCookie("recEntities","Place,Person,Organization",30);
			}else{
				var recEntities = new Array();
				recEntities=getCookie("recEntities").split(",");
				if(recEntities.indexOf('Place')!=-1)
					f2.place.checked = true;
				if(recEntities.indexOf('Person')!=-1)
					f2.person.checked = true;
				if(recEntities.indexOf('Organization')!=-1)
					f2.org.checked = true;					
			}			
			if(!getCookie("NLPAPI")){
				f.NLPAPI[3].selected = true;
				setCookie("NLPAPI",f.NLPAPI[3].value,30);
			}	
			if(!getCookie("combination")){
				f.combination[0].selected = true;
				setCookie("combination",f.combination[0].value,30);
			}
			//set values based on the cookie
			if(getCookie("annotationF")=='RDFa'){
				f2.a_format[0].checked = true;
			}else{
				f2.a_format[1].checked = true;
			}
			if(getCookie("uriSuggestor")=='Sindice'){
				f2.uri_suggestor[0].checked = true;
			}else{
				f2.uri_suggestor[1].checked = true;
			}			
			selectedArray=getCookie("NLPAPI").split(",");
			var selObj = f.NLPAPI;
			var i;
			for (i=0; i<selObj.options.length; i++) {
				if (selectedArray.indexOf(selObj.options[i].value)!= -1) {
					selObj.options[i].selected=true;
				}
			}  
			selObj = f.combination;
			for (i=0; i<selObj.options.length; i++) {
				if (selObj.options[i].value== getCookie("combination")) {
					selObj.options[i].selected=true;
				}
			}  
		},
		insert : function() {
			var f = document.getElementById('settingNLP');
			var f2 = document.getElementById('settingGeneral');
			var prev_af=getCookie("annotationF");
			//ask for user to confirm because of RDFa Microdata mixup
			if(prev_af=="RDFa" && f2.a_format[1].checked && tinyMCEPopup.editor.dom.get('namespaces')){
				var r=confirm("You already have some annotations in RDFa format. Changing the annotation format might result in some inconsistencies in your document! Is it OK?");
				if (r==true)
					setCookie("annotationF",f2.a_format[1].value,30);
			}else{
				setCookie("annotationF",f2.a_format[1].value,30);
			}
			if(f2.a_format[0].checked)
				setCookie("annotationF",f2.a_format[0].value,30);

			if(f2.uri_suggestor[0].checked)
				setCookie("uriSuggestor",f2.uri_suggestor[0].value,30);
			else
				setCookie("uriSuggestor",f2.uri_suggestor[1].value,30);				
			var recEntities = new Array();
			if(f2.place.checked)
				recEntities.push("Place");
			if(f2.person.checked)
				recEntities.push("Person");
			if(f2.org.checked)
				recEntities.push("Organization");	
			if(recEntities.length)
				setCookie("recEntities",recEntities.join(','),30);
			// get form inputs
			var selectedArray = new Array();
			var selObj = f.NLPAPI;
			var i;
			var count = 0;
			for (i=0; i<selObj.options.length; i++) {
				if (selObj.options[i].selected) {
					selectedArray[count] = selObj.options[i].value;
					count++;
				}
			}
			var error=0;
			var errorMsg=document.getElementById("errorMsg");
			switch(f.combination.value){
			case "two":
				if(selectedArray.length<2){
					errorMsg.innerHTML="<font color='red'>*You need to choose at least two APIs!</font>";
					error=1;
				}
				break;
			case "three":
				if(selectedArray.length<3){
					errorMsg.innerHTML="<font color='red'>*You need to choose at least three APIs!</font>";
					error=1;
				}
				break;
			case "four":
				if(selectedArray.length<4){
					errorMsg.innerHTML="<font color='red'>You need to choose at least four APIs!</font>";
					error=1;
				}
				break;
			case "five":
				if(selectedArray.length<5){
					errorMsg.innerHTML="<font color='red'>You need to choose at least five APIs!</font>";
					error=1;
				}
				break;
			}			
			// --------------------
			if(!error){
				// set a cookie
				setCookie("NLPAPI",selectedArray.join(','),30);
				setCookie("combination",f.combination.value,30);
				tinyMCEPopup.close();
			}
		}
}

tinyMCEPopup.onInit.add(rdfaSetting.init, rdfaSetting);
