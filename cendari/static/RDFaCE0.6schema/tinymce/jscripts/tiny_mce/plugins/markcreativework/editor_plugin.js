/**
 * editor_plugin_src.js
 *
 * Copyright 2009, Moxiecode Systems AB
 * Released under LGPL License.
 *
 * License: http://tinymce.moxiecode.com/license
 * Contributing: http://tinymce.moxiecode.com/contributing
 */

(function() {

	
	function urlify(text) {
    	var urlRegex = /(https?:\/\/[^\s]+)/g;
	    return text.replace(urlRegex, function(url) {
	        return '<a href="' + url + '">' + url + '</a>';
	    })
	}


	// Load plugin specific language pack
	tinymce.PluginManager.requireLangPack('markcreativework');

	tinymce.create('tinymce.plugins.MarkCreativeWorkPlugin', {
		/**
		 * Initializes the plugin, this will be executed after the plugin has been created.
		 * This call is done before the editor instance has finished it's initialization so use the onInit event
		 * of the editor instance to intercept that event.
		 *
		 * @param {tinymce.Editor} ed Editor instance that the plugin is initialized in.
		 * @param {string} url Absolute URL to where the plugin is located.
		 */
		init : function(ed, url) {
			//Register the command so that it can be invoked by using tinyMCE.activeEditor.execCommand('mceExample');
			ed.addCommand('mceMarkCreativeWork', function() {
				console.log('tinymce editor content is :',ed.getContent());				

				var linkedText = Autolinker.link( ed.getContent(), {
				    replaceFn : function( autolinker, match ) {
				        console.log( "href = ", match.getAnchorHref() );
				        console.log( "text = ", match.getAnchorText() );

				        switch( match.getType() ) {
				            case 'url' :
				                console.log( "url: ", match.getUrl() );
				                console.log("match",match)
				                // if( match.getUrl().indexOf( 'mysite.com' ) === -1 ) {
				                
				                    return true;  
				        }
				    }
				} );

				console.log('linked text: ',linkedText);
				$linkedText = $(linkedText)
				console.log('updated linked text before: ',$linkedText.html())
				$linkedText.find('a').each(function(){
					$this = $(this)

					if($this.parent().prop('tagName') !== 'SPAN'){
						var temp = $this.text()
						$this.text('')
						$this.append ('<span style="" class="r_entity r_creativework" typeof="schema:CreativeWork"><span style="" class="r_prop r_name" property="schema:name">'+temp+'</span><meta property="schema:url" content="'+$this.attr('href')+'" /></span>')

						console.log($this)
						console.log($this.parent())
					}
				});
				console.log('updated linked text: ',$linkedText.html())
				ed.setContent($('<div>').append($linkedText.clone()).html())


			});

			// Register example button
			ed.addButton('markcreativework', {
				title : 'Automatic Tagging of URLs as Publication Entities', //'markcreativework.desc'
				cmd : 'mceMarkCreativeWork',
				image : url + '/img/buttonRed.png'
			});

			//Add a node change handler, selects the button in the UI when a image is selected
			ed.onNodeChange.add(function(ed, cm, n) {
				cm.setActive('markcreativework', n.nodeName == 'IMG');
			});
		},

		/**
		 * Creates control instances based in the incomming name. This method is normally not
		 * needed since the addButton method of the tinymce.Editor class is a more easy way of adding buttons
		 * but you sometimes need to create more complex controls like listboxes, split buttons etc then this
		 * method can be used to create those.
		 *
		 * @param {String} n Name of the control to create.
		 * @param {tinymce.ControlManager} cm Control manager to use inorder to create new control.
		 * @return {tinymce.ui.Control} New control instance or null if no control was created.
		 */
		createControl : function(n, cm) {
			return null;
		},

		/**
		 * Returns information ab
		 out the plugin as a name/value array.
		 * The current keys are longname, author, authorurl, infourl and version.
		 *
		 * @return {Object} Name/value array containing information about the plugin.
		 */
		getInfo : function() {
			return {
				longname : 'MarkCreativeWork',
				author : 'Some author',
				authorurl : 'http://tinymce.moxiecode.com',
				infourl : 'http://wiki.moxiecode.com/index.php/TinyMCE:Plugins/example',
				version : "1.0"
			};
		}
	});

	// Register plugin
	tinymce.PluginManager.add('markcreativework', tinymce.plugins.MarkCreativeWorkPlugin);
})();
