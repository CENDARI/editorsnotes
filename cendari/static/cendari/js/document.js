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
    if (id == null)
	return;
    $('#scan-viewer').attr('src', cendari_root_url+'cendari/'+cendari_js_project_slug+'/scan/'+id);
    //value = '{project:' + cendari_js_project_slug + 'scan_id: ' + id + '}';
    //trace.event("_system","viewImage", "centre", value);
}

$(document).ready(function() 
{
    $('a.scan').click(function(event) {
	var scan_id = this.getAttribute('id');
	value = '{project:' + cendari_js_project_slug + 'scan_id: ' + scan_id + '}';
	//trace.event("_user","selectScan", "centre", value);
	if (! scan_id)
	    return;
	event.preventDefault();

	$('a.btn-info').removeClass('btn-info');
	$(this).addClass('btn-info');
	viewImage(scan_id);
    });
});

