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

$(document).ready(function(){
    var csrftoken = getCookie('csrftoken');

    // $.ajaxSetup({
    //     beforeSend: function(xhr, settings) {
    //         if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
    //             xhr.setRequestHeader("X-CSRFToken", csrftoken);
    //         }
    //     }
    // });
    
    $('.formCendari').submit(function(e){
        e.preventDefault();
        
        if(tinyMCE.activeEditor!=null){
            tinyMCE.activeEditor.save();
        }

        var fc = $(this);
        var formData = fc.serialize()+"&"+$("#saveButton").attr('name')+"="+$("#saveButton").val();
        console.log("formData are : \n: "+formData);    
        $.ajax({
        // beforeSend: function (xhr) {xhr.setRequestHeader('X-CSRFToken', $('input[name="csrfmiddlewaretoken"]').val());},
            url:fc.attr('action'),
            type: fc.attr('method'),
            data: formData,
            content_type:'application/json',
            success: function(data){
                // console.log(data);
                var currentUrl = window.location.toString();
                var newUrl = currentUrl.replace("add", data.id);
                window.location.replace(newUrl);
                //window.location.assign(newUrl);
                //window.location.assign(cendari_root_url + "cendari/"+cendari_js_project_slug+"/notes/"+data.id);  
            }
        });

    }); 

});
