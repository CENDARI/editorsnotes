// Ext.require(['*']);

// function submitCendariForm()
// {
// 	var formCendari = $(".formCendari");
// 	formCendari.submit(function(e) 
// 	{
//         //e.preventDefault();
// 		if(tinyMCE.activeEditor!=null){
// 			tinyMCE.activeEditor.save();
// 		    }
// 		//prevent Default functionality
       	
//         var fc = $(this);


// 		var formData = fc.serialize();
//         $.ajax(
//         {
//         		//beforeSend: function (xhr) {xhr.setRequestHeader('X-CSRFToken', $('input[name="csrfmiddlewaretoken"]').val());},
//                 url:fc.attr('action'),
//                 type: fc.attr('method'),
//                 data: formData,
//                	content_type:'application/json',
//                 success: function(data) 
//                 {
//                     console.log(data);
//                     console.log(JSON.parse(data));
//                 	var currentUrl = window.location.toString();
// 					var newUrl = currentUrl.replace("add", data.id);
// 					window.location.href(newUrl);
// 					//window.location.assign(newUrl);
//                 	//window.location.assign(cendari_root_url + "cendari/"+cendari_js_project_slug+"/notes/"+data.id);	
// 				}
//          });

//     });	
//     // formCendari.submit();
//     //window.location.assign(cendari_root_url + "cendari/"+cendari_js_project_slug+"/notes/9/");
// }

//document.getElementById('smallvis_iframe').contentWindow.location.reload();


function replaceWindowUrl(data_id){

    var currentUrl = window.location.toString();
    if(currentUrl.indexOf('add')>0){
        var newUrl = currentUrl.replace("add", data_id);
        window.location.replace(newUrl);
    }
}


function removeElement(elemnt_) {
    elemnt_.parentNode.removeChild(elemnt_);
}


function addMessageSaved(modelName){
    $('#progress-message-list').append(modelName +'is saved');
}

function addMessageSaving(modelName){
    $('#progress-message-list').append('Saving: '+ modelName+', please do not reload');
}

function deleteMessage(modelName){
    $('#progress-message-list').append(msg_el);
}


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

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function uniqueElements(el_array){
    var uniqueNames = [];
    $.each(el_array, function(i, el){
        if($.inArray(el, uniqueNames) === -1) uniqueNames.push(el);
    })
    return uniqueNames
}




function submitTranscript(document_id){
    console.log("sumbitting transcript");
    fc = $('#transcriptCendari');
    formData = "";
    formData = formData+"csrfmiddlewaretoken="+document.getElementsByName("csrfmiddlewaretoken")[2].value+"&";

     if($('#transcript-description').length){
        formData =formData +'document='+encodeURIComponent($('#transcript-document').val())+'&creator='+$('#transcript-creator').val()+'&last_updater='+$('#transcript-uploader').val()+'&';
        if(tinyMCE.activeEditor!=null){
            if(tinyMCE.getInstanceById('transcript-description').getContent().length){
                formData = formData+"&content="+encodeURIComponent(tinyMCE.getInstanceById('transcript-description').getContent())+"&";
            }
            else{
                submitScan(document_id);
                return;
            }
        }
    }
    else{
        submitScan(document_id);
        return;
    }

    formData = formData+$("#saveButtonTrascript").attr('name')+"="+$("#saveButtonTrascript").val();


    $.ajax({
        // beforeSend: function (xhr) {xhr.setRequestHeader('X-CSRFToken', $('input[name="csrfmiddlewaretoken"]').val());},
        url:fc.attr('action'),
        type: fc.attr('method'),
        data: formData,
        // content_type:'application/json',
        success: function(data){
            // var currentUrl = window.location.toString();
            // var newUrl = currentUrl.replace("add", document_id);
            // window.location.replace(newUrl);  
            submitScan(document_id);
        }
    });
}

function submitScan(document_id){
    console.log('sumbitting scan');

    if($('#id_image').length>0 && $('#id_image').val().length>0){
        $('#scanCendari').submit(function(e){
            e.preventDefault();
            var options = { 
                success: function(){
                    // var currentUrl = window.location.toString();
                    // var newUrl = currentUrl.replace("add", document_id);
                    // window.location.replace(newUrl);  
                    replaceWindowUrl(document_id);
                }

                // other available options: 
                //url:       url         // override for form's 'action' attribute 
                //type:      type        // 'get' or 'post', override for form's 'method' attribute 
                //dataType:  null        // 'xml', 'script', or 'json' (expected server response type) 
                //clearForm: true        // clear all form fields after successful submit 
                //resetForm: true        // reset the form after successful submit 

                // $.ajax options can be used here too, for example: 
                //timeout:   3000 
            }; 
            $('#scanCendari').ajaxSubmit(options);
            return false;
        });
        
        $('#scanCendari').submit();
    }
    else{
        // var currentUrl = window.location.toString();
        // var newUrl = currentUrl.replace("add", document_id);
        // window.location.replace(newUrl);  
        replaceWindowUrl(document_id);
    }


    

}


$(document).ready(function(){
    var csrftoken = getCookie('csrftoken');

    $('.formCendari').submit(function(e){
        e.preventDefault();
        
        // if(tinyMCE.activeEditor!=null){
        //     tinyMCE.activeEditor.save();
        // }

        for (var edId in tinyMCE.editors){
            if(tinyMCE.editors[edId]!=null){
                tinyMCE.editors[edId].save();
            }
        }

        var fc = $(this);
        // console.log("form object is:");
        // console.log(fc);
        var model = "" // <<<<====
        formData = "";
        formData = formData+"csrfmiddlewaretoken="+document.getElementsByName("csrfmiddlewaretoken")[2].value+"&";
        if($('#model_id').length){
            formData=formData+"id="+$('#model_id').val()+"&";
        }
        if($('#note_title').length){
            formData =formData +'title='+$('#note_title').val()+"&related_topics=&status=open&is_private=false&";
            if(tinyMCE.activeEditor!=null){
                formData = formData+"content="+encodeURIComponent(tinyMCE.getInstanceById('note-description').getContent())+"&";
            }        
        }
        if($('#document-description').length){
            if(tinyMCE.activeEditor!=null){
                formData = formData+"&description="+encodeURIComponent(tinyMCE.getInstanceById('document-description').getContent())+"&";
            }        
        }
        // if($('#transcript-description').length){
        //     formData =formData +'document='+encodeURIComponent($('#transcript-document').val())+'&creator='+$('#transcript-creator').val()+'&last_uploader='+$('#transcript-uploader').val()+'&';
        //     if(tinyMCE.activeEditor!=null){
        //         formData = formData+"&content="+encodeURIComponent(tinyMCE.activeEditor.getContent())+"&";
        // }        
        
        
         if($('#rdf_id').length){
            formData = formData + "rdf="+$('#rdf_id').val().trim()+"&";
            formData = formData + "preferred_name="+$('#preferred_name_id').text().trim()+"&";
         }

        formData = formData+$("#saveButton").attr('name')+"="+$("#saveButton").val();

        // var formData = fc.serialize()+"&"+$("#saveButton").attr('name')+"="+$("#saveButton").val();
        // var formData = $("#saveButton").attr('name')+"="+$("#saveButton").val()+"&csrfmiddlewaretoken="+document.getElementsByName("csrfmiddlewaretoken")[2].value+"&_content_type=application/json&_content="+encodeURIComponent(content)
        // console.log("formData are : \n: "+formData);    
        $.ajax({
        // beforeSend: function (xhr) {xhr.setRequestHeader('X-CSRFToken', $('input[name="csrfmiddlewaretoken"]').val());},
            url:fc.attr('action'),
            type: fc.attr('method'),
            data: formData,
            // content_type:'application/json',
            success: function(data){
                // console.log(data);
                if($('#document-description').length){
                    submitTranscript(data.id);
                }
                else{
                    console.log('submitting non document');
                    // var currentUrl = window.location.toString();
                    // var newUrl = currentUrl.replace("add", data.id);
                    // window.location.replace(newUrl);
                    replaceWindowUrl(data.id)
                }
            }
        });

    }); 

});
