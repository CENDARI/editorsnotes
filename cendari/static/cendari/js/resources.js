$(function() {
    $("#tree").dynatree({
	minExpandLevel:2,
	selectMode:1,//single selection
	clickFolderMode: 3,
	//selectExpandsFolders: false,
	//persist: true,
	initAjax: {
	    data: {key:''},
	    url: cendari_root_url+'cendari/'+cendari_js_project_slug+'/getResourcesData/',
	    dataType: "jsonp",
	},
	onClick: function(node, event) {
	    selected_node = node.data.key;
	    value = '{project:' + selected_node + ', node:' + node.data.title + ',url:' + node.data.url + '}';
	    //alert('node keypath= ' + node.data.key);
	    //trace.event("_user","select", "resources", value);
	    
	    level = node.getLevel();
	    if(level==3){
			//alert('clicked on project ' + cendari_root_url+'cendari/'+cendari_js_project_slug+'/getProjectID/new_slug/'+node.data.key)

			//if this project is not already open, then open it
			if(selected_node!=cendari_js_project_slug){
			    //to get the new project id, getProjectID also changes project slug to new_slug
			    $.ajax({
				data: {},
				url : cendari_root_url+'cendari/'+cendari_js_project_slug+'/getProjectID/new_slug/'+node.data.key,
				datatype:"jsonp",
				success: function(response){
				    project_id = response.project_id;
				    parent.location.href =  cendari_root_url+'cendari/projects/'+project_id;
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
				    n.expand(false);
				}
			    } 
			});
	    }else{
	    	console.log()
			if (node.data.url ) {
				console.log("node.data.url is  "+node.data.url)
			    page_url = parent.location;
			    pathname = page_url.pathname;
			    if(page_url.href.indexOf('pro2.cendari.dariah.eu')!=-1){
					pathname = pathname.replace('enotes/','');
			    }
			    //if node is not already selected
			    if(node.data.url != pathname){
					window.open(node.data.url, "_parent");
			    }
			}else{
			    //unselect other nodes (strange as selectMode:1)
			    console.log('I do not have a node.data.url');
			    $("#tree").dynatree("getRoot").visit(function(n){
					console.log(node.data.key+"!="+n.data.key)
					if (node.data.key!=n.data.key){
					    n.select(false);
					}			 
			    });
			}
	    }
	},
	onPostInit: function(isReloading, isError){
	    page_url = parent.location;
	    pathname = page_url.pathname;
	    var local_host = true;
	    if(page_url.href.indexOf('pro2.cendari.dariah.eu')!=-1){
		pathname = pathname.replace('enotes/','');
		local_host = false;
	    }
	    //a project is selected
	    if(pathname=='/' || pathname.indexOf('/index')!=-1){
		$("#tree").dynatree("getTree").selectKey(cendari_js_project_slug);
		project_node = $("#tree").dynatree("getTree").getNodeByKey(cendari_js_project_slug)
		if(project_node!=null){
		    project_node.expand(true);
		}
	    }else{
		//a leafnode is selected
		pathname = pathname.substring(1, pathname.length-1);
		path_parts = pathname.split("/");
		level = path_parts.length;
		item_id = path_parts[level-1];
		var lazy_node;
		var node_type = '';
		if(pathname.indexOf('topics')!=-1){//or level=6
		    node_type = 'topic';
		    $.ajax({
			url : cendari_root_url+'cendari/'+cendari_js_project_slug+'/getTopicType/topic_id/'+item_id,
			datatype:"jsonp",
			success: function(response){
			    topic_type = response.topic_type;
			    lazy_node = $("#tree").dynatree("getTree").getNodeByKey(cendari_js_project_slug);
			    upload_keyPath = lazy_node.getKeyPath()+'/'+cendari_js_project_slug+'.topics/'+cendari_js_project_slug+'.topic.' + topic_type + '/' + cendari_js_project_slug + '.topic.' + item_id;
			    tree_loadKeyPath(upload_keyPath, node_type);			    
			},
			error: function(){}
		    });
		}else if(pathname.indexOf('notes')!=-1){
		    node_type = 'note';
		    lazy_node = $("#tree").dynatree("getTree").getNodeByKey(cendari_js_project_slug);
		    upload_keyPath = lazy_node.getKeyPath() + '/' + cendari_js_project_slug + '.notes' +'/'+ cendari_js_project_slug +'.note.'+ item_id;
		   // alert('postinit uploadkey = ' + upload_keyPath);
		    tree_loadKeyPath(upload_keyPath, node_type);
		}else if(pathname.indexOf('documents')!=-1){
		    node_type = 'document';
		    lazy_node = $("#tree").dynatree("getTree").getNodeByKey(cendari_js_project_slug);
		    upload_keyPath = lazy_node.getKeyPath() + '/'+ cendari_js_project_slug + '.documents' +'/'+ cendari_js_project_slug +'.document.'+ item_id;
		    //alert('postinit uploadkey = ' + upload_keyPath)
		    tree_loadKeyPath(upload_keyPath, node_type);
		}else if(pathname.indexOf('projects')!=-1){
		    p_node = $("#tree").dynatree("getTree").getNodeByKey(cendari_js_project_slug);	
		    if(p_node!=null){
			p_node.makeVisible(true);
			p_node.select(true);
			p_node.expand(true);
		    }
		}
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
		    var keyParts = key.split(".");
		    var itemType = keyParts[keyParts.length-2];
		    var itemId = parseInt(keyParts[keyParts.length-1]);
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
	onLazyRead: function(node){
	    burl = '';
	    title = node.data.title;
            burl = cendari_root_url+'cendari/'+cendari_js_project_slug+'/getLazyProjectData/'; 
            console.log('==========>>>>>>>>>> burl is : '+burl);
	    node.appendAjax({
                url: burl,
		dataType: "jsonp",
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
	    
        }else if(status == "ok") {
            // 'node' is the end node of our path.
            // If we call activate() or makeVisible() here, then the
            // whole branch will be exoanded now
	    //alert('status OK: ' + node.data.key);
	    node.activate();
	    node.makeVisible();	    
        }else if(status == "notfound") {
            var seg = arguments[2],
	    isEndNode = arguments[3];
        }
    });
}