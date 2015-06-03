function showfiltervals(event) {
    event.preventDefault();
    if ( $(this).hasClass('facetview_open') ) {
	$(this).children('i').removeClass('icon-minus');
	$(this).children('i').addClass('icon-plus');
	$(this).removeClass('facetview_open');
	$('[id="facetview_' + $(this).attr('rel') +'"]').children().find('.facetview_filtervalue').hide();
	$(this).siblings('.facetview_filteroptions').hide();
    } else {
	$(this).children('i').removeClass('icon-plus');
	$(this).children('i').addClass('icon-minus');
	$(this).addClass('facetview_open');
	$('[id="facetview_' + $(this).attr('rel') +'"]').children().find('.facetview_filtervalue').show();
	$(this).siblings('.facetview_filteroptions').show();
    }
}

var leafletMap;
/**
 * Constructs a map visualization.
 **/
function buildMap(mapData, element) {
    var map = element.classed('map', true).attr('id','leafletmap');
    var height = parseInt(element.style('height'));
    var width = parseInt(element.style('width'));
    
    var maxZoom = 10, minZoom = 0, defaultZoom = 0;
    var pointSize = 5, i;
    
    if(mapData.length < 1) return;
    
    //process location string into lat/lon values
    for(i = 0; i < mapData.length; i++){
	var item = mapData[i];
	var latlon = Geohash.decode(item.key);
	var lat = latlon.lat;
	var lon = latlon.lon;
	if(lat == 0 && lon == 0) continue;
	item._lat = lat;
	item._lon = lon;
    }
    
    
    var latExtent = d3.extent(mapData, function(d){return d._lat;});
    var lonExtent = d3.extent(mapData, function(d){return d._lon;});
    var latScale = d3.scale.linear()
	    .domain(latExtent)
	    .range([height - pointSize/2, pointSize/2]);
    var lonScale = d3.scale.linear()
	    .domain(lonExtent)
	    .range([pointSize/2, width - pointSize/2]);
    var colorScale = d3.scale.linear()
	    .domain(d3.extent(mapData, function(d){return d.doc_count;}))
	    .range(["lightblue", "red"]);
    
    //Using Leaflet (instead of D3) for basemap
    leafletMap = L.map('leafletmap',{attributionControl:false, minZoom:minZoom, maxZoom:maxZoom})
	    .fitWorld();
    L.tileLayer(document.location.protocol + '//{s}.tiles.mapbox.com/v4/wjwillett.i9o7e0g1/{z}/{x}/{y}.png?access_token=pk.eyJ1Ijoid2p3aWxsZXR0IiwiYSI6IlJtUlFYVkEifQ.Qk10zoCrd2pTN6t2rcyifQ').addTo(leafletMap);
    for(i=0; i < mapData.length; i++){
	var d = mapData[i];
	var mark = L.circle([d._lat,d._lon], 100000,
			    {'className':'mark',
			     stroke: false,
			     fillOpacity: 0.7,
			     fillColor: colorScale(d.doc_count)})
		.addTo(leafletMap); 
	//associate a data tuple with the mark (to mimic D3)
	mark._path.__data__ = d;   
    }
}

var doc_params = [],
    doc_args = {};
function parse_doc_params() {
    var params = document.location.search.substring(1);
    var varvals = params.split('&');
    for (var i = 0; i < varvals.length; i++) {
	var p = varvals[i].split('=');
	if (p.length == 2) {
	    doc_params.push(p);
	    doc_args[p[0]] = p[1];
	}
    }
}

var doc_facets = {};
var facets_prefix = 'selected_facets';
var bounds = '';
function parse_facets() {
    doc_facets = {};
    for (var i = 0; i < doc_params.length; i++) {
	var p = doc_params[i];
	if (p[0] == facets_prefix) {
	    var facets_vals = p[1].split(':');
	    if (doc_facets[facets_vals[0]]) {
		for (var j = 1; j < facets_vals.length; j++) {
		    doc_facets[facets_vals[0]].add(facets_vals[j]);
		}
	    }
	    else {
		doc_facets[facets_vals[0]] = d3.set(facets_vals.slice(1));
	    }
	}
	else if (p[0] == 'bounds') {
	    bounds = p[1].split(',').map(Number);
	}
    }
}

parse_doc_params();
parse_facets();

function url_facets() {
    var ret = location.origin+location.pathname+"?",
	first = true;
    if ('q' in doc_args) {
	ret += 'q='+doc_args['q'];
	first = false;
    }
    for (var d in doc_facets) {
	var facet =doc_facets[d].values();
	if (facet.length == 0)
	    continue;
	if (! first) {
	    ret += '&';
	    first = false;
	}
	ret += 'selected_facets='+d;
	for (var f in facet) {
	    ret += ':';
	    ret += facet[f];
	}
    }
    if (bounds) {
	if (! first) {
	    ret += '&';
	    first = false;
	}
	ret += 'bounds='+bounds;
    }
    return ret;
}

function facet_toggle_value(val) {
    //return href + (href.indexOf('?')==-1?"?q=":"")+ "&" + val;
    var varval = val.split('='),
	facets = varval[1].split(':'),
	facet = doc_facets[facets[0]];
    if (! facet)
	doc_facets[facets[0]] = d3.set([facets[1]]);
    else if (doc_facets[facets[0]].has(facets[1]))
	doc_facets[facets[0]].remove(facets[1]);
    else
	doc_facets[facets[0]].add(facets[1]);

    return url_facets();
}

function facet_del_facet(facet) {
    delete doc_facets[facet];

    var url = url_facets();
}

function filter_location(event) {
    event.preventDefault();
    var b = leafletMap.getBounds();
    bounds = b.getNorth()+","+b.getWest()+","+b.getSouth()+","+b.getEast();
    var url = url_facets();
    document.location.assign(url);
}

function adapt_resolution(event) {
    event.preventDefault();
}

function reset_location(event) {
    event.preventDefault();
}

function morefacetvals(event) {
    event.preventDefault();
    
    var url = facet_toggle_value($(this).attr("href"));
    document.location.assign(url);
}

function facet_toggle(event) {
    event.preventDefault();
    var url = facet_toggle_value($(this).attr("href"));
    document.location.assign(url);
}


function bind_faceted_widgets() {
    $('.facetview_morefacetvals').click(morefacetvals);
    $('.facetview_toggle').click(facet_toggle);
    $('.facetview_filtershow').click(showfiltervals);
    $('.facetview_filterlocation').click(filter_location);
    $('.facetview_adaptresolution').click(adapt_resolution);
    $('.facetview_resetlocation').click(reset_location);
}
