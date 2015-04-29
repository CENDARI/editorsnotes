Ext.require(['*']);
//cendari.editdocument ={};
 
$.fn.zotero = function (options) {
}

var formPanel = Ext.create('Ext.form.Panel', 
{
	    frame: true,
	    //width:'100%',
	    //autoScroll: true,
	    //bodyPadding: 5,
	    //padding:10,
	    layout: 'fit',
	    id:'documentFormID',
	    items: [{
			contentEl:'noteform',
			border:false,
			autoScroll: true,
    		//border: false,
    		height:'100%',
		//width:'100%',
		//anchor: '100% 100%',
	    }]
});


var images = [],
    viewer = null;

function viewImage(id) 
{
	console.log('id',id);

    if (id == null)
		return;
    $('#scan-viewer').attr('src', cendari_root_url+'cendari/'+cendari_js_project_slug+'/scan/'+id);
    value = '{project:' + cendari_js_project_slug + 'scan_id: ' + id + '}';
    //trace.event("_system","viewImage", "centre", value);
    console.log('value',value);
    console.log('scan-viewer src',cendari_root_url+'cendari/'+cendari_js_project_slug+'/scan/'+id);
}

$(document).ready(function() 
{
	console.log('initializing scans :D ');

	$('body').delegate( "a.scan", "click", function(event) {
    // $('a.scan').click(function(event) {
    	event.preventDefault();
    	console.log('I was clicked',this);
    	
		var scan_id = this.getAttribute('id');
		console.log(this.getAttribute('id'))
		console.log(scan_id)
		//value = '{project:' + cendari_js_project_slug + 'scan_id: ' + scan_id + '}';
		//trace.event("_user","selectScan", "centre", value);
		if (! scan_id)
		    return;

		$('a.btn-info').removeClass('btn-info');
		$(this).addClass('btn-info');
		viewImage(scan_id);
    });


	$('#scan-list').sortable({
		helper: function(e, elt) {
			return elt.clone(true);
		}
	});
	
	$( "body" ).delegate('.delete','click',function(event){
		event.preventDefault();
		var choice = confirm(this.getAttribute('data-confirm'));
		if (choice) {
			var li_jq = $($(this).parent());

			var formData ="csrfmiddlewaretoken="+document.getElementsByName("csrfmiddlewaretoken")[2].value+"&_method=DELETE";
			$.ajax({
			// beforeSend: function (xhr) {xhr.setRequestHeader('X-CSRFToken', $('input[name="csrfmiddlewaretoken"]').val());},
				url:this.getAttribute('href'),
				type: 'POST',
				data: formData,
				success: function(data){
					li_jq.remove();
					$('#scansTab').text('Scans ('+$('#scan-list').find('li').size()+')')
				},
				error: function(XMLHttpRequest, textStatus, errorThrown) { 
					console.log("Error with status "+textStatus+":",errorThrown);
					showErrorMessage(messages.transcript.error);
				} 
			});
		}

	})

});

