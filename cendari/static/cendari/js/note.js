Ext.require(['*']);

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
