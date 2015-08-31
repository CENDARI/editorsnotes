// --- Contextmenu helper --------------------------------------------------
function bindContextMenu(span) {
    // Add context menu to this node:
    $(span).contextMenu({menu: "myMenu"}, function(action, el, pos) {
      // The event was bound to the <span> tag, but the node object
      // is stored in the parent <li> tag
	alert("bindContextMenu was called ...");
      var node = $.ui.dynatree.getNode(el);
      switch( action ) {
      case "cut":
      case "copy":
      case "paste":
        copyPaste(action, node);
        break;
      default:
        alert("Todo: appply action '" + action + "' to node " + node);
      }
    });
};

$(function() {
    $("#tree").dynatree({
     checkbox: true,
      // Override class name for checkbox icon:
      classNames: {checkbox: "dynatree-radio"},


	minExpandLevel:2,
	selectMode:2,//1 single selection,2:multi,3:multi-hier
	clickFolderMode: 3,
	//selectExpandsFolders: false,
	//persist: true,
	onClick: function(node, event) {

	   // Close context  menu on click
	   if( $(".contextMenu:visible").length > 0 ){
	 	$(".contextMenu").hide();
		// return false;
	    }


	    selected_node = node.data.key;
	    //value = '{project:' + selected_node + ', node:' + node.data.title + ',url:' + node.data.url + '}';
	    //trace.event("_user","select", "resources", value);//remove call for now, causes a bug	   
	    level = node.getLevel();
            //console.log('==============================>>>>>>>>>> Resources/onClick: selected node key, level = ' + selected_node + ' , ' + level);
	    if(level==3){
			//alert('clicked on project ' + cendari_root_url+'cendari/'+cendari_js_project_slug+'/getProjectID/new_slug/'+node.data.key)
            		//console.log('==============================>>>>>>>>>> Resources/onClick: selected node is a project');

			//if this project is not already open, then open it
			if(selected_node!=cendari_js_project_slug){
            		    //console.log('==============================>>>>>>>>>> Resources/onClick: open current project.');
			    //to get the new project id, getProjectID also changes project slug to new_slug
			    $.ajax({
				data: {},
				url : cendari_root_url+'cendari/'+cendari_js_project_slug+'/getProjectID/new_slug/'+node.data.key,
				datatype:"jsonp",
				success: function(response){
				    project_id = response.project_id;
				    parent.location.href =  cendari_root_url+'cendari/projects/'+project_id;
            		    	    //console.log('==============================>>>>>>>>>> Resources/onClick: parent.location.href = ' + parent.location.href + ", but should just use cendari_js_object_id = " + cendari_js_object_id);
				},
				error: function(){}
			    });
			    node.select(true);
			}
			//close the rest of the project folders
			$("#tree").dynatree("getRoot").visit(function(n){
			    level = n.getLevel();
			    if (level==3){
				if(n.data.key != node.data.key){
				    // n.setTitle('<html><font color="#C0C0C0">' + n.data.title + '</font></html>');
            		    	    //console.log('==============================>>>>>>>>>> Resources/onClick: close rest of projects, now close ' + n.data.key);
				    n.expand(false);
				}
			    } 
			});
	    }else{
			if (node.data.url ) {
			    	page_url = parent.location;
				node_url = node.data.url;
				node_key = node.data.key;
           			//console.log('==============================>>>>>>>>>> 1esources/onClick: if not a project node is selected, with node url = ' + node.data.url);	
				//alert("page_url.href.indexOf(node_url) = " + page_url.href.indexOf(node_url));	 
			    	if(page_url.href.indexOf(node_url)==-1){
           				//console.log('==============================>>>>>>>>>> Resources/onClick: page url:' + page_url + ' does not contain node url:' + node.data.url);
					if (node.data.key.indexOf(cendari_js_project_slug+'.topic.')==-1){
					}else{
						//found a topic
						console.log("==============================>>>>>>>>>> selected node is a topic, with key : " + node_key);
						if(event.shiftKey){
							node.toggleSelect();
							console.log("==============================>>>>>>>>>> selected node is a topic, and shift was preseed.");
						}else{
							$("#tree").dynatree("getRoot").visit(function(node) { 
								node.select(false);
							});
							console.log("==============================>>>>>>>>>> selected node is a topic, and shift was NOT preseed.");
						}
					}		 
					//window.open(node.data.url, "_parent");
			    	}else{
           				// console.log('==============================>>>>>>>>>> Resources/onClick: page url:' + page_url + ' does contain node url:' + node.data.url);
				}
			}else{
			    //unselect other nodes (strange as selectMode:1)
           		    //console.log('==============================>>>>>>>>>> Resources/onClick: I do not have a node.data.url, node data = ' + node.data);
			    $("#tree").dynatree("getRoot").visit(function(n){
           		    		//console.log('==============================>>>>>>>>>> Resources/onClick: visiting node, node key= ' + n.data.key);
					if (node.data.key!=n.data.key){
           		    		    //console.log('==============================>>>>>>>>>> Resources/onClick: finding nodes to close: ' + node.data.key+"!="+n.data.key);
					    n.select(false);
					}			 
			    });
			}
	    }
	},
	onDblClick: function(node, event){
		// console.log('dynatree node.data is : ',node.data);
	},
      /*Bind context menu for every node when it's DOM element is created.
        We do it here, so we can also bind to lazy nodes, which do not
        exist at load-time. (abeautifulsite.net menu control does not
        support event delegation)*/
      onCreate: function(node, span){
	alert("onCreate function called ..");
        bindContextMenu(span);
      },

	onPostInit: function(isReloading, isError){
	  	//console.log('==============================>>>>>>>>>> Resources/onPostInit: cendari_js_project_slug = ' + cendari_js_project_slug);
	  	//console.log('==============================>>>>>>>>>> Resources/onPostInit: cendari_js_object_type = ' + cendari_js_object_type);
	  	//console.log('==============================>>>>>>>>>> Resources/onPostInit: cendari_js_object_id = ' + cendari_js_object_id);
	  	//console.log('==============================>>>>>>>>>> Resources/onPostInit: cendari_js_topic_type = ' + cendari_js_topic_type);
		if(cendari_js_object_type=='note'){
		    	lazy_node = $("#tree").dynatree("getTree").getNodeByKey(cendari_js_project_slug);
			if(lazy_node!=null){
			    upload_keyPath = lazy_node.getKeyPath() + '/' + cendari_js_project_slug + '.notes' +'/'+ cendari_js_project_slug +'.note.'+ cendari_js_object_id;
		            //console.log('==============================>>>>>>>>>> Resources/onPostInit: NOTE upload_keyPath = ' + upload_keyPath);
			    tree_loadKeyPath(upload_keyPath, cendari_js_object_type);
			}else{
		            // console.log('==============================>>>>>>>>>> Resources/onPostInit: NOTE lazy_node is null');
			}		
		} else if (cendari_js_object_type=='document'){
		    	lazy_node = $("#tree").dynatree("getTree").getNodeByKey(cendari_js_project_slug);		
			if(lazy_node!=null){
			    	upload_keyPath = lazy_node.getKeyPath() + '/'+ cendari_js_project_slug + '.documents' +'/'+ cendari_js_project_slug +'.document.'+ cendari_js_object_id;
		            	//console.log('==============================>>>>>>>>>> Resources/onPostInit: DOCUMENT upload_keyPath = ' + upload_keyPath);
			    	tree_loadKeyPath(upload_keyPath, cendari_js_object_type);
			}else{
		            // console.log('==============================>>>>>>>>>> Resources/onPostInit: DOCUMENT lazy_node is null');
			}
		} else if (cendari_js_object_type=='topic'){
		    	lazy_node = $("#tree").dynatree("getTree").getNodeByKey(cendari_js_project_slug);		
			if(lazy_node!=null){
				upload_keyPath = lazy_node.getKeyPath() +'/'+cendari_js_project_slug+'.topics/'+cendari_js_project_slug+'.topic.' + cendari_js_topic_type + '/' + cendari_js_project_slug + '.topic.' + cendari_js_object_id;
		            	//console.log('==============================>>>>>>>>>> Resources/onPostInit: TOPIC upload_keyPath = ' + upload_keyPath);
			    	tree_loadKeyPath(upload_keyPath, cendari_js_object_type);
			}else{
		            // console.log('==============================>>>>>>>>>> Resources/onPostInit: TOPIC lazy_node is null');
			}
		} else if (cendari_js_object_type==''){//this is a project
			$("#tree").dynatree("getTree").selectKey(cendari_js_project_slug);
			project_node = $("#tree").dynatree("getTree").getNodeByKey(cendari_js_project_slug);
		       	//console.log('==============================>>>>>>>>>> Resources/onPostInit: PROJECT project_node = ' + project_node);
			if(project_node!=null){
			    project_node.expand(true);
		            //console.log('==============================>>>>>>>>>> Resources/onPostInit: PROJECT lazy_node expanded = ' + project_node);
			}else{
		            // console.log('==============================>>>>>>>>>> Resources/onPostInit: PROJECT lazy_node is null');
			}
		} else {
	            	// console.log('==============================>>>>>>>>>> Resources/onPostInit: does it ever get to here?');
		}

	},
	onCreate: function(dtnode, nodeSpan){
		// When nodes are created, add hover event handlers to trigger highlighting in the vis
	    $(nodeSpan).hover(function(){
			var node = $.ui.dynatree.getNode(this);
			if(!node) 
				return;
			if(!node.data || !node.data.key)
				return;
			var key = node.data.key;
	    		//console.log('==============================>>>>>>>>>> Resources/onCreate: node.data.key = ' + key);
		    var keyParts = key.split(".");
		    var itemType = keyParts[keyParts.length-2];
		    var itemId = parseInt(keyParts[keyParts.length-1]);
         	    //console.log('==============================>>>>>>>>>> Resources/onCreate: itemType = ' + itemType);
	    	    //console.log('==============================>>>>>>>>>> Resources/onCreate: itemId = ' + itemId);
		    if(itemType != "topic" || isNaN(itemId))
		    	return;
			parent.postMessage({'messageType':'cendari_highlight',
	                      'targetWindowIds':'east',
	                      'entityIds':[itemId],
	                      'highlightMode':2},
	                       document.location.origin);
			}, function(){
				parent.postMessage({'messageType':'cendari_highlight',
	                      'targetWindowIds':'east',
	                      'entityIds':[],
	                      'highlightMode':2},
	                       document.location.origin);
			});
	}, 
	onRender: function(node, nodeSpan) {
    	// $(nodeSpan).find("a.dynatree-title").css("color", "red");
    	// console.log('Node is ',node);
    	// console.log($(nodeSpan).find('.dynatree-radio'));
    	// console.log('is it a folder ? ', node);
    	// console.log(node.isFolder);
    	// radio_button = 
    	radio = $(nodeSpan).find('.dynatree-radio')[0]
    	if(node.data.isFolder && (node.data.project_id !== undefined)){
    		// console.log('yes it is a folder');
    		// project_path  = cendari_root_url+'cendari/projects/'+node.data.project_id;
    		// console.log($(nodeSpan).next().attr('class'))
    		// if($(nodeSpan).next().attr('class') !== 'edit_button_span'){
    		//     $img= $('<img>').attr('src',cendari_js_edit_image_path).attr('alt','Edit');
    		//     $a = $('<a>').addClass('edit_button').attr('href',project_path).attr('target','_blank').append($img);
	    	// 	$span = $('<span>').addClass('edit_button_span').addClass('dynatree-radio')//.append($a)
	    	// 	// $(nodeSpan).after('<span><a class="edit_button" href="'+project_path+'" >  <img src="'++'" alt="Edit" >  </a></span>')
	    	// 	// $(nodeSpan).after($span);
    		// }
    		$(radio).attr('pid',node.data.project_id);
    	}
    	else{
    		$(radio).hide();
    	}

	},
	onLazyRead: function(node){
	    burl = '';
	    title = node.data.title;
            burl = cendari_root_url+'cendari/'+cendari_js_project_slug+'/getLazyProjectData/sfield/'+sfield; 
	    //console.log('==============================>>>>>>>>>> Resources/onLazyRead: burl, sfield ' + burl + ' , ' + sfield);
	    node.removeChildren();//to solve tree duplication problem 
	    node.appendAjax({
                url: burl,
		dataType: "jsonp"
	    });
	}
    });
});

function tree_loadKeyPath(keyPath, node_type){
    $("#tree").dynatree("getTree").loadKeyPath(keyPath, function(node, status){
        if(status == "loaded") {
            // 'node' is a parent that was just traversed.
            // If we call expand() here, then all nodes will be expanded
            // as we go
	    node.expand();
	    //alert('traversing to this node, key: ' + node.data.key);
	    //console.log('==============================>>>>>>>>>> Resources/tree_loadKeyPath: traversing node with key = ' + node.data.key);
	    
        }else if(status == "ok") {
            // 'node' is the end node of our path.
            // If we call activate() or makeVisible() here, then the
            // whole branch will be exoanded now
	    //alert('status OK: ' + node.data.key);
	    //console.log('==============================>>>>>>>>>> Resources/tree_loadKeyPath: status OK for node key = ' + node.data.key);
	    node.activate();
	    node.makeVisible();	    
        }else if(status == "notfound") {
            var seg = arguments[2],
	    isEndNode = arguments[3];
	    //console.log('==============================>>>>>>>>>> Resources/tree_loadKeyPath: status not found');
        }
    });
}
