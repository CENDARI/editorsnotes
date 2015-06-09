Ext.require(['*']);

cendari = {};
cendari.version = "0.1";
cendari.init = [];
cendari.addInit = function(fn) {
	cendari.init.push(fn);
};

Ext.application({
	name : 'CendariExt',
	launch : function() {
		Ext.create('Ext.Viewport', {
			id : 'border-example',
			autoScroll : true,
			layout : {
				type : 'border',
				padding : 1
			},
			defaults : {
				split : false
			},
			items : [
				{
					region:'west',
					id:'west-panel',
					title:'Resources',
					split:true,
					width: '22%',
					minWidth : 175,					
					collapsible: true,
					margins : '0 0 0 2',
					layout:'accordion',
					layoutConfig:{
					    animate:true
					},
					items: [{
					    title:'Navigation',
					    autoScroll:true,
					    border:false,
					    iconCls:'nav',
					    contentEl : 'west'
					},{
					    title:'Chat',
					    border:false,
					    autoScroll:true,
					    iconCls:'chat',
					    contentEl : 'southWest'
					}]	

				}, 
			{
				region : 'center',
				layout : 'border',
				border : false,
				autoScroll : true,
				overflowY: 'scroll',
				margins : '0 0 0 0',
				// contentEl : 'center',
				id : 'center-panel', // see Ext.getCmp() below
				dockedItems : 
				[{
					xtype : 'toolbar',
					dock : 'top',
					id: 'toolbarId',
					height:25,
					items : [
						{
							text : 'New',
							id : 'tbarID',
							menu : [{
								text : 'Note',
								id : 'NewNoteId'
							}, {
								text : 'Document',
								id : 'NewDocumentId'
							}, {
								text : 'Project',
								id : 'NewProjectId'
							}]
						}, 
						{
							text : 'Save',
							//contentEl : 'submitButtonCendari',
							id : 'saveNoteID'
						},
						{
							text : 'Button',
							id: 'extraButtonId'
						},
						{
							itemId : 'toggleCw',
							text : 'Pop-up Window',
							layout : 'fit',
							hidden:true,
							enableToggle : true,
							toggleHandler : function() {
								cw.setVisible(!cw.isVisible());
							},
						}, 
						'->', //{
						// 		text : 'Import',
						// 		iconCls : 'options_icon',
						// 		id : 'optionsID',
						// 		menu : [{
						// 			text : 'From Jigsaw',
						// 			id : 'jigsawImport'

						// 			}, {
						// 				text : 'From ... '
						// 			}, {
						// 				text : 'From ...'
						// 			}]
						// 	},
							{
								text:'Delete',
								id: 'deleteButtonId'
							}//, 
							// {
							// 	text : 'Help'
							// }
					]
				}],

				items : [{
					region : 'center',
					xtype : 'tabpanel',
					id : 'centerTabPanel',
					overflowY: 'scroll',
					margins : '0 0 0 0',
					layout:'fit',
					defaults:{
						autoScroll : true,
						minWidth : 5,
					},

					//title: 'My Working Space',
					items : [
						cw = Ext.create('Ext.Window', {
							xtype : 'window',
							closable : true,
							minimizable : true,
							title : 'Pop-up Window',
							height : 200,
							width : 400,
							layout : 'fit',
							constrain : true,
							autoScroll : true,
							itemId : 'center-window',
							minimize : function() {
								this.floatParent.down('button#toggleCw').toggle();
							}
						})
					],				
				}, {
					region : 'south',
					height : 350,
					split : true,
					layout:'fit',
					collapsible : true,
					title : 'Image Viewer',
					id : 'imageViewer',
					collapsed : true,
				    tools: [{
					type: 'expand',
					handler: function() {
					    var src=$('#scan-viewer').attr('src');
					    if (src)
						window.open(src, 'scan');
					}
				    }]
				}]
			}, {
				region : 'east',
				collapsible : true,
				floatable : true,
				contentEl : 'east',
				stateId : 'visualization-panel',
				id : 'east-panel', // see Ext.getCmp() below
				title : 'Visualizations',
				width : '25%',
				split : true,
				layout : 'fit',
				minWidth : 330,
				maxWidth : 400,
				autoScroll : true,
				animCollapse : true,
				margins : '0 0 0 2'
			}, {
				region : 'south',
				contentEl : 'south',
				layout : 'fit',
				height : 100,
				minSize : 100,
				maxSize : 200,
				collapsible : true,
				collapsed : true,
				title : 'About CENDARI',
				margins : '0 0 0 0'
			}]

		});

		cendari.editor = null;
		cendari.addImageViewer = null;
		cendari.addTab = null;
		cendari.addWidgetToActiveTab = null;
		csspath = document.getElementById("static_url").getAttribute("content") + "cendari/css/rdfaceCSS/";
		var editors = [];

		function Editor(height, domID, isReadOnly, editButtonID, labeltitle) {
			this.height = height;
			this.domID = domID;
			this.editButtonID = editButtonID;
			this.labelTitle = labeltitle;
			var editor = tinyMCE.init({
				mode : "specific_textareas",
        		editor_selector : "mceEditor",
				theme : "advanced",
			    force_br_newlines : false,
			    force_p_newlines : false,
			    forced_root_block : 'p',
				//elements : domID,
				content:"Description",
				toolbar:"description",
				// plugins : "style,table,noneditable,example,lists,advhr,advimage,advlink,iespell,inlinepopups,media,paste,directionality,noneditable,nonbreaking,wordcount,advlist,contextmenu,fullscreen,rdface",
				plugins : "markcreativework,style,table,noneditable,example,lists,advhr,advimage,advlink,iespell,inlinepopups,media,paste,directionality,nonbreaking,wordcount,advlist,contextmenu,fullscreen,rdface,autolink,spellchecker,pagebreak,layer,save,emotions,insertdatetime,preview,searchreplace,print,fullscreen,visualchars,xhtmlxtras,template",
				theme_advanced_buttons1 : "undo,redo,cut,copy,paste,fontsizeselect,bold,italic,underline,strikethrough,bullist,numlist,forecolor,backcolor, code,rdfaceHelp,rdfaceRun,rdfaceFacts,rdfaceSetting,markcreativework",//,
				theme_advanced_buttons2 : "tablecontrols,|,link,unlink,anchor,|,justifyleft,justifycenter,justifyright,justifyfull,|,styleselect,formatselect,fontselect,fontsizeselect",
				fullscreen_new_window : true,
				width : "100%",
				content_css : csspath + "content.css ," + csspath + "rdface.css, " + csspath + "schema_colors.css" ,
				height: height,
				noneditable_leave_contenteditable: true,	
				theme_advanced_toolbar_location : "top",
				theme_advanced_toolbar_align : "left",
				theme_advanced_statusbar_location : "bottom",
				noneditable_regexp: /\[\[[^\]]+\]\]/g,
				//theme_advanced_resizing : true,
				//resize : true,
				readonly : isReadOnly,
				valid_elements : "*[*]",
				setup: function (ed) {
	                // Add a custom button
	                ed.addButton('description', {
	                	text:'Description',
	                	icon: false,
	                    onclick: function () {
	                        ed.focus();
	                    }
	                });
	                ed.onInit.add(function(ed) {
			          console.log('Editor is done: ',ed);
			          editors_crc32[ed.id] = CRC32(tinyMCE.getInstanceById(ed.id).getContent());
				    });
            	}
			});
		
	
		}

		function createEditor(height, domID, isReadOnly, editButtonID, labeltitle) {
			var new_extension = 'can_edit';
			var old_extension = 'read_only';
			if(isReadOnly){
				new_extension = 'read_only';
				old_extension = 'can_edit';
			}

			var editor = new Editor(height, domID+new_extension, isReadOnly, editButtonID, labeltitle);
			

			for (var i = 0; i < editors.length; i++) {
				if (editors[i].editButtonID == editButtonID) {
					return;
				}
			}
			editors.push(editor);		
			Ext.get(editButtonID).on('click', function() {
				for (var i = 0; i < editors.length; i++) {
					if (editors[i].editButtonID == editButtonID) {
						// var isReadOnlyTemp = !tinyMCE.getInstanceById(editors[i].domID).settings.readonly;
						var isReadOnlyTemp = !tinyMCE.getInstanceById(domID+old_extension).settings.readonly;
						tinyMCE.getInstanceById(domID+old_extension).remove();
						createEditor(editors[i].height, editors[i].domID, isReadOnlyTemp, editors[i].editButtonID,editors[i].labelTitle);
						var editorreadability = isReadOnlyTemp ? " [ Read Only ]                --- click here for Edit mode" : " [ Editable ]                    --- click here for Read-Only mode";
						document.getElementById(editButtonID).value =editors[i].labelTitle+editorreadability;
						//$('#editButtonID').class+=
						
					}
				}
			});
		}

		function addTab(title) {
			var tab = new Ext.Panel({
				title : title,
				border : false,
				layout : 'fit',
				autoScroll : true,
				overflowY: 'scroll'
			});
			Ext.getCmp('centerTabPanel').add(tab).show();

		}

		function addWidgetToActiveTab(xTypeWidget, domIdWidget, layoutWidget) {
			var widget = Ext.widget(xTypeWidget, {
				//layout: layoutWidget,
				contentEl : domIdWidget,
				frame : true,
				bodyPadding : '0 0 0 0',
				autoScroll : true,
				overflowY: 'scroll',
				margins : '0 0 0 0',
				layout : 'fit'
			});

			Ext.getCmp('centerTabPanel').getActiveTab().add(widget);
		}

		function addImageViewer(type, id) {
			Ext.getCmp('imageViewer').expand();
			var widget = Ext.widget(type, {
				contentEl : id,
				frame : true,
				bodyPadding : '0 0 0',
				autoScroll : true,
				overflowY: 'scroll'
			});
			Ext.getCmp('imageViewer').add(widget);
			//Ext.getCmp('editortab').tab.setText("Document");
		}
		cendari.createEditor = createEditor;
		cendari.addImageViewer = addImageViewer;
		cendari.addTab = addTab;
		cendari.addWidgetToActiveTab = addWidgetToActiveTab;
		cendari.currentId = 0;
		// Ext.getCmp('saveNoteID').on('click', function() {submitCendariForm();});
		Ext.getCmp('saveNoteID').on('click', function() {$('.formCendari').submit()});
		// Ext.getCmp('readModeID').on('click', function() {});
	/*	Ext.getCmp('saveNoteID').on('click', function() {
		    if(tinyMCE.activeEditor!=null){
			tinyMCE.activeEditor.save();
		    }
			frm = $('#noteform');
			frm.submit();
			
			var transIframe 	= document.getElementById('transciptIframe');
			var transDoc 		= transIframe.contentDocument;
			var transForm 		= transDoc.getElementById('transcriptform');
			transForm.submit();
		    value = '{project:' + cendari_js_project_slug + '}';
		    trace.event("_user","saveNote", "centre", value);
			return false;
		});*/
		Ext.getCmp('NewNoteId').on('click', function() {
			console.log("New note called");
			window.location.assign(cendari_root_url + "cendari/"+cendari_js_project_slug+"/notes/add/");
		    value = '{project:' + cendari_js_project_slug + '}';
		    // trace.event("_user","NewNote", "centre", value);
		});
		Ext.getCmp('NewDocumentId').on('click', function() {
			console.log("New document called");
			window.location.assign(cendari_root_url + "cendari/"+cendari_js_project_slug+"/documents/add/");
		    value = '{project:' + cendari_js_project_slug + '}';
		    // trace.event("_user","NewDocument", "centre", value);
		});
		Ext.getCmp('NewProjectId').on('click', function() {
			console.log("New project called");
			window.location.assign(cendari_root_url + "cendari/projects/add/");
		    value = '{project:' + cendari_js_project_slug + '}';
		    // trace.event("_user","NewProject", "centre", value);
		});
		// Ext.getCmp('jigsawImport').on('click', function() {
		// 	console.log("Jigsaw");
		// 	window.open(cendari_root_url + "cendari/"+cendari_js_project_slug + "/importfromjigsaw/");
		//     value = '{project:' + cendari_js_project_slug + '}';
		//     trace.event("_user","jagsawImport", "centre", value);
		// });
		cendari.init.map(function(fn) {
			fn.call();
		});
	}
});

function switchtabs(noOfTabs, type)
{
	var height;
 	$('.tab-content').hide();
	$('.tabs.'+type).height("0");
	$('#tab1').prop('checked', false);

	switch (type){
		case  "note":
			height = $(".tab-content.note").height();
		    value = '{project:' + cendari_js_project_slug + '}';
		    // trace.event("_system","switch to Note tab", "centre", value);
			break;
		case "document":
			height = $(".tab-content.document").height();
		    value = '{project:' + cendari_js_project_slug + '}';
		    // trace.event("_system","switch to Document tab", "centre", value);
			break;
		case "entity":
			height = $(".tab-content.note").height();
		    value = '{project:' + cendari_js_project_slug + '}';
		    // trace.event("_system","switch to Entity tab", "centre", value);
			break;
			
	}
	
	var tab = new Array();
	var tabcontent = new Array();

	for(var i=1; i<=noOfTabs; i++) {
		tab[i]="#tab"+i;
		tabcontent[i] ="#tab-content"+i;
	}
	

	$.each(tab, function(i,value){
		$(value).on('click', function (e) {
				for(var j=1; j<=noOfTabs; j++) if(j!=i) $(tabcontent[j]).hide();
		    	$(tabcontent[i]).is(":visible")? $(tabcontent[i]).hide():$(tabcontent[i]).show();
		    	$(tabcontent[i]).is(":visible")? $('.tabs.'+type).height(height):$('.tabs.'+type).height("0");
		    	$(tabcontent[i]).is(":visible")? $(value).prop('checked', true): $(value).prop('checked', false);	
		});
	});
	
}
