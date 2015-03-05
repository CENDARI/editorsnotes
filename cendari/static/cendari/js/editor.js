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

var type_class_mapping = {
    "PER" : "form-entities r_person",
    "ORG" : "form-entities r_organization",
    "EVT" : "form-entities r_event",
    "PLA" : "form-entities r_place",
    "TAG" : "form-entities r_thing",
    ""    : "form-entities"
};

function updateIframe(iframe_id){
    document.getElementById(iframe_id).src = document.getElementById(iframe_id).src
}



function createEntityLink(absolute_url,type,name){
    var html = '<a  href="'+absolute_url+'" class="'+type_class_mapping[type]+'"> '+name+' </a>'

    return html;
}

function  updatedEnitiesTab(prefix,related_topics){
    var entities_html = "";
    var related_topics_jq = $('#'+prefix+'-related-topics');
    for(var i=0;i<related_topics.length;i++){
        entities_html += createEntityLink(related_topics[i].absolute_url,related_topics[i].type,related_topics[i].preferred_name);
    }

    related_topics_jq.empty();
    console.log("entities_html",entities_html);
    related_topics_jq.append(entities_html);

    $('#entitiesTab').text('Entities ('+related_topics.length+')');
}


function createScanElement(thumbnail_url,id){
    var html = "";
    html +='<li>'+
            '<a class="scan btn" id="1" href="'+thumbnail_url+'">'+
            '<img id="ext-gen1206" src="/media/scans/2015/02/HB043T_TIF_thumb.gif" alt="Thumbnail of scan 1" width="100">'+
            id +'</a></li>'
                    

}

function updateScanTab(scans){
    var scans_jq = $('#scan-list');
    var scans_html = "";

    for(var i=0;i<scans.length;i++){
        scans_html += createScanElement(scans[i].image_thumbnail_url,scans[i].id);
    }

    scans_jq.empty();
    scans_jq.append(scans_html);

}

function addMessage(div,msg,msg_id){
    var msg_el = $("<div></div>").text(msg).attr('id',msg_id).addClass('alert');   
    $('#'+div).append(msg_el)
}

function updateMessage(msg_id,new_msg){
    $('#'+msg_id).text(new_msg);
}


function replaceWindowUrl(data_id){

    var currentUrl = window.location.toString();
    if(id.length===0){
        var newUrl = currentUrl.replace("add", data_id);
        window.location.replace(newUrl);
    }
    else{
        updateIframe('resourcesIframe');
        updateIframe('smallvisIframe');
    }
}


function removeElement(elemnt_) {
    elemnt_.parentNode.removeChild(elemnt_);
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
            // addMessage('message-list',messages.transcript.beforeSend,messages.transcript.id);
            toastr['info'](messages.transcript.beforeSend)
        },

        success: function(data){
            // var currentUrl = window.location.toString();
            // var newUrl = currentUrl.replace("add", document_id);
            // window.location.replace(newUrl);
            // updateMessage(messages.transcript.success,messages.transcript.id);
            toastr['success'](messages.transcript.success)
            submitScan(document_id);
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) { 
            // alert("Status: " + textStatus); alert("Error: " + errorThrown); 
            console.log("Error with status "+textStatus+":",errorThrown);
            // updateMessage(messages.transcript.error,messages.transcript.id);
            toastr['error'](messages.transcript.error)
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
                    toastr['info'](messages.scan.beforeSend)
                },
                success: function(){
                   
                    toastr['success'](messages.scan.success)
                    replaceWindowUrl(document_id);
                },
                 error: function(XMLHttpRequest, textStatus, errorThrown) { 
                    console.log("Error with status "+textStatus+":",errorThrown);
                    toastr['error'](messages.scan.error)
                    replaceWindowUrl(document_id);
                }
                
            }; 
            $('#scanCendari').ajaxSubmit(options);
            return false;
        });
        
        $('#scanCendari').submit();
    }
    else{
        toastr['success'](messages.scan.success);
        replaceWindowUrl(document_id);
    }
}


function submitDocument(fc){
    var formData = "";
    formData = formData+"csrfmiddlewaretoken="+document.getElementsByName("csrfmiddlewaretoken")[2].value+"&";
    formData = formData+"&description="+encodeURIComponent(tinyMCE.getInstanceById('document-description').getContent())+"&";
    formData = formData+$("#saveButton").attr('name')+"="+$("#saveButton").val();

    $.ajax({
        // beforeSend: function (xhr) {xhr.setRequestHeader('X-CSRFToken', $('input[name="csrfmiddlewaretoken"]').val());},
        url:fc.attr('action'),
        type: fc.attr('method'),
        data: formData,
        // content_type:'application/json',
        beforeSend:function(){
        // addMessage('message-list',messages[type].beforeSend,messages[type].id);
            console.log("saving ....")
            toastr['info'](messages.document.beforeSend)
        },
        success: function(data){
            console.log("response data:",data);

            toastr['success'](messages.document.success)
            
            updatedEnitiesTab(cendari_js_object_type,data.related_topics);
            updateScanTab(data.scans);

            submitTranscript(data.id);
            
            console.log('submitting non document');
            replaceWindowUrl(data.id)
            
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) { 
       

            console.log("Error with status "+textStatus+":",errorThrown);
            toastr['error'](messages.document.error)

        } 
    });
}

function submitNote(fc){
    var formData = "";
    formData = formData+"csrfmiddlewaretoken="+document.getElementsByName("csrfmiddlewaretoken")[2].value+"&";
    formData=formData+"id="+$('#model_id').val()+"&";
    formData =formData +'title='+$('#note_title').val()+"&related_topics=&status=open&is_private=false&";
    formData = formData+"content="+encodeURIComponent(tinyMCE.getInstanceById('note-description').getContent())+"&";
    formData = formData+$("#saveButton").attr('name')+"="+$("#saveButton").val();

    $.ajax({
        // beforeSend: function (xhr) {xhr.setRequestHeader('X-CSRFToken', $('input[name="csrfmiddlewaretoken"]').val());},
        url:fc.attr('action'),
        type: fc.attr('method'),
        data: formData,
        // content_type:'application/json',
        beforeSend:function(){
        // addMessage('message-list',messages[type].beforeSend,messages[type].id);
            console.log("saving ....")
            toastr['info'](messages.note.beforeSend)
        },
        success: function(data){
            toastr['success'](messages.note.success)
            updatedEnitiesTab(cendari_js_object_type,data.related_topics);
            submitTranscript(data.id);
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) { 
            console.log("Error with status "+textStatus+":",errorThrown);
            toastr['error'](messages.note.error)

        } 
    });
}

function submitEntity(fc){
    var formData = "";
    formData = formData+"csrfmiddlewaretoken="+document.getElementsByName("csrfmiddlewaretoken")[2].value+"&";
    formData=formData+"id="+$('#model_id').val()+"&";
    formData = formData + "rdf="+$('#rdf_id').val().trim()+"&";
    formData = formData + "preferred_name="+$('#preferred_name_id').text().trim()+"&";
    formData = formData+$("#saveButton").attr('name')+"="+$("#saveButton").val();

    $.ajax({
        url:fc.attr('action'),
        type: fc.attr('method'),
        data: formData,
        beforeSend:function(){

            console.log("saving ....")
            toastr['info'](messages.entity.beforeSend)
        },
        success: function(data){
            toastr['success'](messages.entity.success)
            updatedEnitiesTab(cendari_js_object_type,data.related_topics);           
            replaceWindowUrl(data.id)
            
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) { 
            console.log("Error with status "+textStatus+":",errorThrown);
            toastr['error'](messages.entity.error)

        } 
    });
}



$(document).ready(function(){
    var csrftoken = getCookie('csrftoken');
    // if(cendari_js_object_type === 'note' || cendari_js_object_type==='document'){
    //     main_editor_crc32 = CRC32($('#'+cendari_js_object_type+'-description').text())
    //     if(cendari_js_object_type === 'document'){
    //         transcript_editor_crc32 = CRC32($('#transcript-description').text());   
    //     }
    // }
    
    
    toastr.options = {
        "closeButton": true,
        "debug": false,
        "newestOnTop": true,
        "progressBar": false,
        "positionClass": "toast-top-center",
        "preventDuplicates": true,
        "onclick": null,
        "showDuration": "300",
        "hideDuration": "1000",
        "timeOut": "5000",
        "extendedTimeOut": "1000",
        "showEasing": "swing",
        "hideEasing": "linear",
        "showMethod": "fadeIn",
        "hideMethod": "fadeOut"
    }

    $('.formCendari').submit(function(e){
        e.preventDefault();
       
        for (var edId in tinyMCE.editors){
            if(tinyMCE.editors[edId]!=null){
                tinyMCE.editors[edId].save();
            }
        }

        var fc = $(this);
        
        if(cendari_js_object_type == 'note'){
            submitNote(fc)
        }
        if(cendari_js_object_type == 'document'){
            submitDocument(fc)
        }
        if(cendari_js_object_type == 'entity'){
            submitEntity(fc)
        }

    }); 

});









































/** deprecated 
$(document).ready(function(){
    var csrftoken = getCookie('csrftoken');
    if(cendari_js_object_type === 'note' || cendari_js_object_type==='document'){
        main_editor_crc32 = CRC32($('#'+cendari_js_object_type+'-description').text())
        if(cendari_js_object_type === 'document'){
            transcript_editor_crc32 = CRC32($('#transcript-description').text());   
        }
    }
    
    
    toastr.options = {
        "closeButton": true,
        "debug": false,
        "newestOnTop": true,
        "progressBar": false,
        "positionClass": "toast-top-center",
        "preventDuplicates": true,
        "onclick": null,
        "showDuration": "300",
        "hideDuration": "1000",
        "timeOut": "5000",
        "extendedTimeOut": "1000",
        "showEasing": "swing",
        "hideEasing": "linear",
        "showMethod": "fadeIn",
        "hideMethod": "fadeOut"
    }

    $('.formCendari').submit(function(e){
        e.preventDefault();
        
        // if(tinyMCE.activeEditor!=null){
        //     tinyMCE.activeEditor.save();
        // }
        if(id.length>0){
            if(tinyMCE.getInstanceById(cendari_js_object_type'-description')){}

        }

        for (var edId in tinyMCE.editors){
            if(tinyMCE.editors[edId]!=null){
                tinyMCE.editors[edId].save();
            }
        }

        var fc = $(this);
        // console.log("form object is:");
        // console.log(fc);
        var model = "" // <<<<====
        var type  = "none"
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
        console.log("formData are : \n: "+formData);    
        $.ajax({
        // beforeSend: function (xhr) {xhr.setRequestHeader('X-CSRFToken', $('input[name="csrfmiddlewaretoken"]').val());},
            url:fc.attr('action'),
            type: fc.attr('method'),
            data: formData,
            // content_type:'application/json',
            beforeSend:function(){
                // addMessage('message-list',messages[type].beforeSend,messages[type].id);
                console.log("saving ....")
                toastr['info'](messages[type].beforeSend)
            },
            success: function(data){
                console.log("response data:",data);
                
                toastr['success'](messages[type].success)
                console.log(type);
                console.log(type==='document');
                console.log(type==='note');

                if(type.length>0 && (type==='document' || type==='note')){
                    updatedEnitiesTab(type,data.related_topics);
                }

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
                // alert("Status: " + textStatus); alert("Error: " + errorThrown); 
                // updateMessage(messages[type].error,messages[type].id);
                // var currentUrl = window.location.toString();
                
                console.log("Error with status "+textStatus+":",errorThrown);
                // updateMessage(messages.transcript.error,messages.transcript.id);
                toastr['error'](messages[type].error)

                // window.location.replace(currentUrl);
            } 
        });

    }); 

});
**/

