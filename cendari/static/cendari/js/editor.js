var messages = {
    'document':{
        'id' : 'documentStatusMsg',
        'beforeSend':'saving document please do not refresh',
        'success' :'document saved',
        'error': 'document did not saved correctly'
    },
    'transcript':{
        'id' : 'transcriptStatusMsg',
        'beforeSend':'saving transcript please do not refresh',
        'success' :'transcript saved',
        'error': 'transcript did not saved correctly'
    },
    'scan':{
        'id' : 'scanStatusMsg',
        'beforeSend':'uploading image please do not refresh',
        'success' :'image uploaded',
        'error': 'imaged did not upload correctly'
    },
    'note':{
        'id' : 'noteStatusMsg',
        'beforeSend':'saving note please do not refresh',
        'success' :'note saved',
        'error': 'note did not saved correctly'
    },
    'entity':{
        'id' : 'entityStatusMsg',
        'beforeSend':'resolving entity please do not refresh',
        'success' :'entity resolved',
        'error': 'entity did not resolved correctly'
    },
    'none':{
        'id' : 'noneStatusMsg',
        'beforeSend':'',
        'success' :'',
        'error': ''
    }
};


function addMessage(div,msg,msg_id){
    var msg_el = $("<p></p>").text(msg).attr('id',msg_id);   
    $('#'+div).append(msg_el);
}

function updateMessage(msg_id,new_msg){
    $('#'+msg_id).text(new_msg);
}


function replaceWindowUrl(data_id){

    var currentUrl = window.location.toString();
    // if(currentUrl.indexOf('add')>0){
    var newUrl = currentUrl.replace("add", data_id);
    window.location.replace(newUrl);
    // }
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
    });
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
        beforeSend: function(){
            addMessage('statusMessages',messages.transcript.beforeSend,messages.transcript.id);
        },

        success: function(data){
            // var currentUrl = window.location.toString();
            // var newUrl = currentUrl.replace("add", document_id);
            // window.location.replace(newUrl);
            updateMessage(messages.transcript.success,messages.transcript.id);
            submitScan(document_id);
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) { 
            alert("Status: " + textStatus); alert("Error: " + errorThrown); 
            updateMessage(messages.transcript.error,messages.transcript.id);
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
                 beforeSend: function(){
                    addMessage('statusMessages',messages.scan.beforeSend,messages.scan.id);
                },
                success: function(){
                    // var currentUrl = window.location.toString();
                    // var newUrl = currentUrl.replace("add", document_id);
                    // window.location.replace(newUrl);  
                    updateMessage(messages.scan.success,messages.scan.id);
                    replaceWindowUrl(document_id);
                },
                 error: function(XMLHttpRequest, textStatus, errorThrown) { 
                    alert("Status: " + textStatus); alert("Error: " + errorThrown); 
                    updateMessage(messages.scan.error,messages.scan.id);
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
        var model = ""; // <<<<====
        var type  = "none";
        formData = "";
        formData = formData+"csrfmiddlewaretoken="+document.getElementsByName("csrfmiddlewaretoken")[2].value+"&";
        if($('#model_id').length){
            formData=formData+"id="+$('#model_id').val()+"&";
        }
        if($('#note_title').length){
            type = 'note';
            formData =formData +'title='+$('#note_title').val()+"&related_topics=&status=open&is_private=false&";
            if(tinyMCE.activeEditor!=null){
                formData = formData+"content="+encodeURIComponent(tinyMCE.getInstanceById('note-description').getContent())+"&";
            }        
        }
        if($('#document-description').length){
            type = 'document';
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
            type = 'entity';
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
            beforeSend:function(){
                addMessage('statusMessages',messages[type].beforeSend,messages[type].id);
            },
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
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) { 
                alert("Status: " + textStatus); alert("Error: " + errorThrown); 
                updateMessage(messages[type].error,messages[type].id);
                var currentUrl = window.location.toString();
    
                window.location.replace(currentUrl);
            } 
        });

    }); 

});
