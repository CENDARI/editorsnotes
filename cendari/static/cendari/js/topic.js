Ext.require(['*']);

Ext.application(
{
	launch: function() 
	{	
		var formPanel = Ext.create('Ext.form.Panel', {
		    frame: true,
			layout:'fit',		
		    items: 
		    [{
		    	contentEl:'noteform',
		    	border:false,
		    	autoScroll: true,
		    }]
		    });
		Ext.getCmp('editortab').add(formPanel);		
		cendari.currentId = 0;
		function edittopic(text,id) 
		{
		   //editor.setValue(text);
			currentId = id;
			if (id == 0)
				Ext.getCmp('editortab').tab.setText("New Topic");
			else
				Ext.getCmp('editortab').tab.setText("Topic "+id);
		                value = '{project:' + cendari_js_project_slug + 'topic_id: ' + id +'}';
		                trace.event("_user","editTopic", "centre", value);
		}
		//cendari.edittopic = edittopic;
   }
});







//{contentEl:'id_title'},{contentEl:'id_content'},
	        /*{
	            xtype: 'textfield',
	            name: 'textfield1',
	            fieldLabel: 'Text field',
	            value: 'Text field value'
	        }, {
	            xtype: 'hiddenfield',
	            name: 'hidden1',
	            value: 'Hidden field value'
	        },{
	            xtype: 'textfield',
	            name: 'password1',
	            inputType: 'password',
	            fieldLabel: 'Password field'
	        }, {
	            xtype: 'filefield',
	            name: 'file1',
	            fieldLabel: 'File upload'
	        }, {
	            xtype: 'textareafield',
	            name: 'textarea1',
	            fieldLabel: 'TextArea',
	            value: 'Textarea value'
	        }, {
	            xtype: 'displayfield',
	            name: 'displayfield1',
	            fieldLabel: 'Display field',
	            value: 'Display field <span style="color:green;">value</span>'
	        }, {
	            xtype: 'numberfield',
	            name: 'numberfield1',
	            fieldLabel: 'Number field',
	            value: 5,
	            minValue: 0,
	            maxValue: 50
	        }, {
	            xtype: 'checkboxfield',
	            name: 'checkbox1',
	            fieldLabel: 'Checkbox',
	            boxLabel: 'box label'
	        }, {
	            xtype: 'radiofield',
	            name: 'radio1',
	            value: 'radiovalue1',
	            fieldLabel: 'Radio buttons',
	            boxLabel: 'radio 1'
	        }, {
	            xtype: 'radiofield',
	            name: 'radio1',
	            value: 'radiovalue2',
	            fieldLabel: '',
	            labelSeparator: '',
	            hideEmptyLabel: false,
	            boxLabel: 'radio 2'
	        }, {
	            xtype: 'datefield',
	            name: 'date1',
	            fieldLabel: 'Date Field'
	        }, {
	            xtype: 'timefield',
	            name: 'time1',
	            fieldLabel: 'Time Field',
	            minValue: '1:30 AM',
	            maxValue: '9:15 PM'
	        }*/
