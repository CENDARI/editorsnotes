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
        'error': 'entity did not resolved correctly',
        'warning_latlong': 'entinty was resolved but coordinates couldn\'t be found '
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

var toastr_options = {
    "closeButton": true,
    "debug": false,
    "newestOnTop": true,
    "progressBar": false,
    "positionClass": "toast-top-center",
    "preventDuplicates": true,
    "onclick": null,
    "showDuration": "300",
    "hideDuration": "1000",
    "timeOut": "5000000000000000",
    "extendedTimeOut": "5000000000000000",
    "showEasing": "swing",
    "hideEasing": "linear",
    "showMethod": "fadeIn",
    "hideMethod": "fadeOut"
}

function showToastrMessage(type,message){
    toastr.clear();
    toastr[type](message);
}

function showErrorMessage(message){
    toastr.options.timeOut="500";
    toastr.options.extendedTimeOut="1000";
    showToastrMessage('error',message);
}

function showSuccessMessage(message){
    toastr.options.timeOut="500";
    toastr.options.extendedTimeOut="1000";
    showToastrMessage('success',message);
}


function showWarningMessage(message){
    toastr.options.timeOut="5000";
    toastr.options.extendedTimeOut="10000";
    showToastrMessage('warning',message);
}

function showInfoMessage(message){
    toastr.options.timeOut="5000000000000000";
    toastr.options.extendedTimeOut="5000000000000000";
    showToastrMessage('info',message)
}


function updateIframe(iframe_id){
    document.getElementById(iframe_id).src = document.getElementById(iframe_id).src;
}



function createEntityLink(absolute_url,type,name,rdf){
    var html = '';
    var innerHtml = name;
    console.log('rdf',rdf);
    if(rdf !==null && rdf!==undefined){
        if(!rdf.length){
            innerHtml = '<u>'+innerHtml+'</u>';
        }
    }
    else{
        innerHtml = '<u>'+innerHtml+'</u>';
    }
    html='<a  href="'+absolute_url+'" class="'+type_class_mapping[type]+'"> '+innerHtml+' </a>';

    return html;
}

function  updatedEnitiesTab(prefix,related_topics){
    var entities_html = "";
    var related_topics_jq = $('#'+prefix+'-related-topics');
    console.log('related_topics: ',related_topics)
    for(var i=0;i<related_topics.length;i++){
        entities_html += createEntityLink(related_topics[i].absolute_url,related_topics[i].type,related_topics[i].preferred_name,related_topics[i].rdf);
    }

    related_topics_jq.empty();
    console.log("entities_html",entities_html);
    related_topics_jq.append(entities_html);

    $('#entitiesTab').text('Entities ('+related_topics.length+')');
}


function createScanElement(image_url,thumbnail_url,id){
    var html = "";
    html +='<li class="scan-list-item btn">'+
            '<a class="scan" id="1" href="http://'+window.location.pathname+image_url+'">'+
            '<img id="ext-gen1206" src="'+thumbnail_url+'" alt="Thumbnail of scan 1" width="100"></a>'+
            '<a href="'+cendari_root_url+'api/projects/'+cendari_js_project_slug+'/documents/'+cendari_js_object_id+'/scans/'+id+'/" class="delete" data-confirm="Are you sure to delete this item?"><img src="'+cendari_root_url+'static/cendari/img/fileclose.png"></a>'+
            '</li>';
    return html;
                    

}

function updateScanTab(scans){
    var scans_jq = $('#scan-list');
    var scans_html = "";

    console.log('scans',scans);

    for(var i=0;i<scans.length;i++){
        scans_html += createScanElement(scans[i].image_url,scans[i].image_thumbnail_url,scans[i].id);
    }

    
    scans_jq.empty();
    scans_jq.append(scans_html);
    $('#scansTab').text('Scans ('+scans.length+')');
    $('#id_image').val('');

}

function addMessage(div,msg,msg_id){
    var msg_el = $("<div></div>").text(msg).attr('id',msg_id).addClass('alert');   
    $('#'+div).append(msg_el);
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
    return uniqueNames;
}




function submitTranscript(document_id,fc_document){
    console.log("sumbitting transcript");
    var fc = $('#transcriptCendari');
    var formData = "";
    formData = formData+"csrfmiddlewaretoken="+document.getElementsByName("csrfmiddlewaretoken")[2].value+"&";

    if($('#transcript-description').length){
        formData =formData +'document='+encodeURIComponent($('#transcript-document').val())+'&creator='+$('#transcript-creator').val()+'&last_updater='+$('#transcript-uploader').val()+'&';
        if(tinyMCE.getInstanceById('transcript-description')!=null){
            if(tinyMCE.getInstanceById('transcript-description').getContent().length && CRC32(tinyMCE.getInstanceById('transcript-description').getContent()) !== editors_crc32['transcript-description']){
                formData = formData+"&content="+encodeURIComponent(tinyMCE.getInstanceById('transcript-description').getContent())+"&";
            }
            else{
                submitDocument(fc_document);
                return;
            }
        }
    }
    else{
        submitDocument(fc_document);
        return;
    }

    formData = formData+$("#saveButtonTrascript").attr('name')+"="+$("#saveButtonTrascript").val();


    $.ajax({
        // beforeSend: function (xhr) {xhr.setRequestHeader('X-CSRFToken', $('input[name="csrfmiddlewaretoken"]').val());},
        url:fc.attr('action'),
        type: fc.attr('method'),
        data: formData,
        success: function(data){
            $("#transcriptTab").text('Transcript (1)');
            submitDocument(fc_document);
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) { 
            console.log("Error with status "+textStatus+":",errorThrown);
            showErrorMessage(messages.transcript.error);
            submitDocument(fc_document);
        } 
    });
}

function submitScan(document_id,fc_document){
    console.log('sumbitting scan');

    if($('#id_image').length>0 && $('#id_image').val().length>0){
        $('#scanCendari').submit(function(e){
            e.preventDefault();
            var options = { 
                success: function(){
                    submitDocument(fc_document)
                },
                 error: function(XMLHttpRequest, textStatus, errorThrown) { 
                    console.log("Error with status "+textStatus+":",errorThrown);
                    showErrorMessage(messages.scan.error);
                    submitDocument(fc_document)
                }
                
            }; 
            $('#scanCendari').ajaxSubmit(options);
            return false;
        });
        $('#scanCendari').submit();
    }
    else{
        submitDocument(fc_document);
    }
}



function submitScanAutomatic(){

    
    var bar = $('.bar');
    var percent = $('.percent');
    var status = $('#status');

    $('#scanCendari').submit(function(e){
        e.preventDefault();
        var options = {
            beforeSend: function() {
                status.empty();
                var percentVal = '0%';
                bar.width(percentVal)
                percent.html(percentVal);
            },
            uploadProgress: function(event, position, total, percentComplete) {
                var percentVal = percentComplete + '%';
                bar.width(percentVal);
                percent.html(percentVal);
                //console.log(percentVal, position, total);
            },
            success: function(e) {
                console.log('response',e);
                var percentVal = '100%';
                bar.width(percentVal);
                percent.html(percentVal);
            },
            complete: function(xhr) {
                status.html(xhr.responseText);
            }
        };
        $('#scanCendari').ajaxSubmit(options);
        return false;
    });
    $('#scanCendari').submit();

}


function submitDocument(fc){
    console.log('sumbitting document');

    var formData = "";
    
    formData = formData+"csrfmiddlewaretoken="+document.getElementsByName("csrfmiddlewaretoken")[2].value+"&";
    formData = formData+"&description="+encodeURIComponent(tinyMCE.getInstanceById('document-description').getContent())+"&";
    formData = formData+$("#saveButton").attr('name')+"="+$("#saveButton").val();
    console.log('formData:',formData);
    $.ajax({
        url:fc.attr('action'),
        type: fc.attr('method'),
        data: formData,
        success: function(data){
            console.log("response data:",data);

            showSuccessMessage(messages.document.success);
            updatedEnitiesTab(cendari_js_object_type,data.related_topics);
            // updateScanTab(data.scans);
            
            replaceWindowUrl(data.id);
            
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) { 
            console.log("Error with status "+textStatus+":",errorThrown);
            showErrorMessage(messages.document.error);
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
        // beforeSend:function(){
        // // addMessage('message-list',messages[type].beforeSend,messages[type].id);
        //     console.log("saving ....")
        //     toastr['info'](messages.note.beforeSend)
        // },
        success: function(data){
            showSuccessMessage(messages.note.success);
            updatedEnitiesTab(cendari_js_object_type,data.related_topics);
            replaceWindowUrl(data.id);
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) { 
            console.log("Error with status "+textStatus+":",errorThrown);
            showErrorMessage(messages.note.error);

        } 
    });
}

function submitEntity(fc){
    var formData = "";
    
    formData = formData+"csrfmiddlewaretoken="+document.getElementsByName("csrfmiddlewaretoken")[2].value+"&";
    formData=formData+"id="+$('#model_id').val()+"&";
    formData = formData + "summary="+$('#entity_description').val().trim()+"&";
    formData = formData + "rdf="+$('#rdf_id').val().trim()+"&";
    formData = formData + "preferred_name="+$('#preferred_name_id').text().trim()+"&";
    formData = formData+$("#saveButton").attr('name')+"="+$("#saveButton").val();
    $.ajax({
        url:fc.attr('action'),
        type: fc.attr('method'),
        data: formData,
        success: function(data){

            // console.log('type')
            // console.log('latlong')
            if(data.type==='PLA'){
                if(data.latlong === null || data.latlong=== undefined){
                    showWarningMessage(messages.entity.warning_latlong);    
                }
                else{
                    showSuccessMessage(messages.entity.success);
                }
            }
            else{
                showSuccessMessage(messages.entity.success);
            }

            updatedEnitiesTab(cendari_js_object_type,data.related_topics);           
            replaceWindowUrl(data.id);
            
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) { 
            console.log("Error with status "+textStatus+":",errorThrown);
            showErrorMessage(messages.entity.error);

        } 
    });
}


$(document).ready(function(){
    var csrftoken = getCookie('csrftoken');    
    toastr.options = toastr_options

    $('.formCendari').submit(function(e){
        e.preventDefault();
       
        for (var edId in tinyMCE.editors){
            if(tinyMCE.editors[edId]!=null){
                tinyMCE.editors[edId].save();
            }
        }

        var fc = $(this);
        console.log('fc',fc);
        if(cendari_js_object_type == 'note'){
            showInfoMessage(messages.note.beforeSend);
            submitNote(fc);
        }
        if(cendari_js_object_type == 'document'){
            showInfoMessage(messages.document.beforeSend);
            console.log("cendari_js_object_id ===>",cendari_js_object_id)
            if(cendari_js_object_id.length === 0){
                submitDocument(fc);
            }
            else{
                submitTranscript(cendari_js_object_id,fc);
            }
        }
        if(cendari_js_object_type == 'topic'){
            showInfoMessage(messages.entity.beforeSend)
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

