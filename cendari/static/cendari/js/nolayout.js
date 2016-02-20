Ext.require(['*']);

cendari = {};
cendari.version = "0.1";
cendari.init = [];

cendari.addInit = function(fn) {
	cendari.init.push(fn);
};

Ext.require(['*']);

Ext.application({
	launch : function() {
		cendari.editor = null;
		csspath = document.getElementById("static_url").getAttribute("content") + "cendari/css/rdfaceCSS/";
		var editors = [];
		
function Editor(height, domID, isReadOnly, editButtonID, labeltitle) {
			this.height = height;
			this.domID = domID;
			this.editButtonID = editButtonID;
			this.labelTitle = labeltitle;

			var editor = tinyMCE.init({
				mode : "exact",
				theme : "advanced",
			    force_br_newlines : false,
			    force_p_newlines : false,
			    forced_root_block : '',
				elements : domID,
				content:"Description",
				toolbar:"description",
				plugins : "example,fullscreen,lists,advhr,advimage,advlink,iespell,inlinepopups,media,paste,directionality,fullscreen,noneditable,nonbreaking,wordcount,advlist,contextmenu,rdface, anthisplugin, fullscreen",
				theme_advanced_buttons1 : "undo,redo,cut,copy,paste,fontsizeselect,bold,italic,underline,strikethrough,bullist,numlist,forecolor,backcolor, code,rdfaceHelp,rdfaceRun,rdfaceFacts,rdfaceSetting",
				fullscreen_new_window : true,
				width : "100%",
				content_css : csspath + "content.css ," + csspath + "rdface.css, " + csspath + "schema_colors.css" ,
				height: height,
				noneditable_leave_contenteditable: true,
				//entity_encoding : "raw",

				//skin : "o2k7",
				//Ali:added rdface plugin+contextmenu
				//plugins : "lists,advhr,advimage,advlink,iespell,inlinepopups,media,paste,directionality,fullscreen,noneditable,nonbreaking,wordcount,advlist,contextmenu,rdface",
				// Ali: add XHHTML elements for RDFa
				//valid_elements : "*[*]",
				//Ali:added rdface buttons
				// Theme options
				//theme_advanced_buttons1 : "bold,italic,underline,strikethrough,|,justifyleft,justifycenter,justifyright,justifyfull,styleselect,formatselect,fontselect,fontsizeselect,forecolor,backcolor,anthisplugin",
				// theme_advanced_buttons2 : "cut,copy,paste,pastetext,pasteword,|,bullist,numlist,|,outdent,indent,|,undo,redo,|,link,unlink,image,,code,|,ltr,rtl,|,fullscreen,|,rdfaceHelp,rdfaceRun,rdfaceFacts,rdfaceSetting,|",
				//theme_advanced_buttons3 : "",
				//theme_advanced_buttons4 : "",
				theme_advanced_toolbar_location : "top",
				theme_advanced_toolbar_align : "left",
				theme_advanced_statusbar_location : "bottom",
				noneditable_regexp: /\[\[[^\]]+\]\]/g,
				//theme_advanced_resizing : true,
				//resize : true,
				readonly : isReadOnly,
				//plugins : "autolink,lßists,pagebreak,style,layer,table,save,advhr,advimage,advlink,emotions,iespell,inlinepopups,insertdatetime,preview,media,searchreplace,print,contextmenu,paste,directionality,fullscreen,noneditable,visualchars,nonbreaking,xhtmlxtras,template,advlist,rdface",
				// Add XHHTML elements for RDFa
				valid_elements : "*[*]",
				
				// Theme options
				setup: function (ed) {
	                // Add a custom button
	                ed.addButton('description', {
	                	text:'Description',
	                	icon: false,
	                    onclick: function () {
	                        ed.focus();
	                    }
	                });
            	}
			});
		
	
		}

		function createEditor(height, domID, isReadOnly, editButtonID, labeltitle) {
			var editor = new Editor(height, domID, isReadOnly, editButtonID, labeltitle);

			for (var i = 0; i < editors.length; i++) {
				if (editors[i].editButtonID == editButtonID) {
					return;
				}
			}
			editors.push(editor);		
			Ext.get(editButtonID).on('click', function() {
				for (var i = 0; i < editors.length; i++) {
					if (editors[i].editButtonID == editButtonID) {
						var isReadOnlyTemp = !tinyMCE.getInstanceById(editors[i].domID).settings.readonly;
						tinyMCE.getInstanceById(editors[i].domID).remove();
						createEditor(editors[i].height, editors[i].domID, isReadOnlyTemp, editors[i].editButtonID,editors[i].labelTitle);
						var editorreadability = isReadOnlyTemp ? " [ Read Only ]                --- click here for Edit mode" : " [ Editable ]                    --- click here for Read-Only mode";
						document.getElementById(editButtonID).value =editors[i].labelTitle+editorreadability;
						//$('#editButtonID').class+=
						
					}
				}
			});
		}

		cendari.createEditor = createEditor;
		cendari.currentId = 0;		
		cendari.init.map(function(fn) {
			fn.call();
		});
	}
});

