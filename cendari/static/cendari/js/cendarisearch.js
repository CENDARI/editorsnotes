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
var geohash_distances = [
    5003530,
    625441,
    123264,
    19545,
    3803,
    610,
    118,
    19,
    3.71,
    0.6
];


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
    var docCountExtent = d3.extent(mapData, function(d){return d.doc_count;}),
        colorScale = d3.scale.linear()
            .domain(docCountExtent);
    if (docCountExtent[0] == docCountExtent[1])
        colorScale.range(["red", "red"]);
    else
        colorScale.range(["lightblue", "red"]);
    var radius = 10000;

    
    //Using Leaflet (instead of D3) for basemap
    leafletMap = L.map('leafletmap',{attributionControl:false, minZoom:minZoom, maxZoom:maxZoom});
    if (bounds) {
        var b = bounds.split(',').map(Number),
            top_left = b.splice(0, 2),
            bottom_right = b.splice(0, 2),
            view = L.latLngBounds(L.latLng(top_left[0], bottom_right[1]),
                                  L.latLng(bottom_right[0], top_left[1]));
        if (view.isValid())
            leafletMap.fitBounds(view);
        else
            leafletMap.fitWorld();
        if (b.length > 0) { // precision
            radius = geohash_distances[b[0]+1]/6;
        }
    }
    else
        leafletMap.fitWorld();
    L.tileLayer(document.location.protocol + '//{s}.tiles.mapbox.com/v4/wjwillett.i9o7e0g1/{z}/{x}/{y}.png?access_token=pk.eyJ1Ijoid2p3aWxsZXR0IiwiYSI6IlJtUlFYVkEifQ.Qk10zoCrd2pTN6t2rcyifQ').addTo(leafletMap);
    for(i=0; i < mapData.length; i++){
        var d = mapData[i];
        var mark = L.circle([d._lat,d._lon], radius,
                            {'className':'mark',
                             stroke: false,
                             fillOpacity: 0.7,
                             fillColor: colorScale(d.doc_count)})
                .addTo(leafletMap); 
        //associate a data tuple with the mark (to mimic D3)
        mark._path.__data__ = d;   
    }
}

function rebin(range, data) {
    var m = data.length,
        dx = (range[1]-range[0])/m,
        bin, i;

    if (dx == 0) {
        dx = 1;
    }

    // Initialize the bins.
    for (i = 0; i < m; i++) {
        bin = data[i];
        bin.x = bin.key;
        bin.dx = dx;
    }

    return data;
}

/**
 * Constructs a timeline visualization.
 **/
function buildTimeline(timelineData, extent, element) {
    var m = timelineData.length,
	dateExtent = [ timelineData[0].key, timelineData[m-1].key],
	dx = (dateExtent[1]-dateExtent[0])/m;
    dateExtent[1] += dx;
    if (dx == 0) dx = 1;
    for (var i = 0; i < timelineData.length; i++) {
        var td = timelineData[i];
	td.dx = dx;
	td.x = td.key;
        td.date = new Date(td.key); // converts key to a proper date
        td.y = Math.log(1+td.doc_count)/Math.LN10;
    }
    if (timelineData.length == 0) return;
    
    var timeline = element.classed('timeline', true);
    var total_height = parseInt(element.style('height'));
    var total_width = parseInt(element.style('width'));

    // Formatters for counts and times (converting numbers to Dates).
    var formatCount = d3.format(",.0f"),
        formatTime1 = d3.time.format("%Y-%m-%d"),
        formatTime = function(d) { return formatTime1(new Date(d)); };

    var margin = {top: 2, right: 2, bottom: 2, left: 2},
        width = total_width - margin.left - margin.right,
        height = total_height - margin.top - margin.bottom;


    var x = d3.time.scale()
            .domain(dateExtent)
            .range([0, width]);

    var data = timelineData; //rebin(dateExtent, timelineData.length, timelineData);
    var y = d3.scale.linear()
            .domain([0, d3.max(data, function(d) { return d.y; })])
            .range([height, 0]);
    
    var xAxis = d3.svg.axis()
            .scale(x)
            .orient('bottom')
            .tickFormat(formatTime),
        yAxis = d3.svg.axis().scale(y).orient('left');

    // Build the timeline
    var chart = timeline.append('svg')
              .attr('height', total_height)
              .attr('width', total_width)
            .append("g")
              .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
    var bar_width = Math.floor(width / (data.length+1));

    var draw = function() {
	console.log('translate='+d3.event.translate);
	console.log('scale='+d3.event.scale);
	console.log('axis(0)='+xAxis.scale().invert(0));
	console.log('axis('+width+')='+xAxis.scale().invert(width));
	//bg.select(".bg").call(xAxis);
	//bar.select(".bar").call(xAxis);
    };
//    var zoom = d3.behavior.zoom()
//	    .x(x)
//            .on("zoom", draw);

    var bg = chart.selectAll(".bg")
              .data(data)
           .enter().append("rect")
            .attr("class", "bg")
            .attr("x", function(d) { return x(d.x); })
            .attr("width", bar_width)
            .attr("height", height)
           .append("title")
            .text(function(d) { return formatTime(d.x)+": "+formatCount(d.y); });

    var bar = chart.selectAll(".bar")
              .data(data)
            .enter().append("g")
             .attr("class", "bar")
             .attr("transform", function(d) { return "translate(" + x(d.x) + "," + y(d.y) + ")"; });

    bar.append("rect")
        .attr("x", 1)
        .attr("width", bar_width)
        .attr("height", function(d) { return Math.ceil(height - y(d.y)); })
      .append("title")
        .text(function(d) { return formatTime(d.x)+": "+formatCount(d.y); });

    // chart.append("rect")
    // 	.attr("class", "zoompane")
    // 	.attr("width", width)
    // 	.attr("height", height)
    // 	.call(zoom);

    // bar.append("text")
    //     .attr("dy", ".75em")
    //     .attr("y", 6)
    //     .attr("x", width/(data.length*2))
    //     .attr("text-anchor", "middle")
    //     .text(function(d) { return formatCount(d.y); });

    // chart.append("g")
    //     .attr("class", "x axis")
    //     .attr("transform", "translate(0," + height + ")")
    //     .call(xAxis)
    //   .selectAll("text")
    //     .style("text-anchor", "end")
    //     .attr("dx", "-.8em")
    //     .attr("dy", "-.55em")
    //     .attr("transform", "rotate(-90)" );
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
var bounds = 0;
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
            bounds = p[1];
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

function filter_date(event) {
    event.preventDefault();
}

function filter_location(event) {
    event.preventDefault();
    var b = leafletMap.getBounds(),
        width = b.getNorthEast().distanceTo(b.getNorthWest()),
        height = b.getNorthEast().distanceTo(b.getSouthEast()),
        area = width*height,
        prec, d;
    for (prec = 0; prec < geohash_distances.length; prec++) {
        d = geohash_distances[prec] * geohash_distances[prec];

        if ((area / d) > 5000)
            break;
    }
    
    bounds = b.getNorth()+","+b.getWest()+","+b.getSouth()+","+b.getEast()+","+prec;
    var url = url_facets();
    document.location.assign(url);
}

function adapt_resolution(event) {
    event.preventDefault();
    var b = leafletMap.getBounds(),
        width = b.getNorthEast().distanceTo(b.getNorthWest()),
        height = b.getNorthEast().distanceTo(b.getSouthEast()),
        area = width*height,
        prec, d;
    for (prec = 0; prec < geohash_distances.length; prec++) {
        d = geohash_distances[prec] * geohash_distances[prec];

        if ((area / d) > 5000)
            break;
    }
    
    if (bounds) {
        var i = bounds.lastIndexOf(',');
        bounds = bounds.substring(0, i+1)+prec;
    }
    else
        bounds = b.getNorth()+","+b.getWest()+","+b.getSouth()+","+b.getEast()+","+prec;
    var url = url_facets();
    document.location.assign(url);
}

function reset_location(event) {
    event.preventDefault();
    bounds = '';
    var url = url_facets();
    document.location.assign(url);
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

function datepicker_parseDate(format, value, settings) {
    if (format == null || value == null) {
	throw "Invalid arguments";
    }

    value = (typeof value === "object" ? value.toString() : value + "");
    if (value === "") {
	return null;
    }

    var year = 1, month = 0, day = 0, len;
    var m = value.match('^[-]?[0-9]+');
    if (! m) return null;
    var date = new Date(Date.UTC(2000, month, day));
    year = Number(m[0]);
    if (! year) 
	year = 1;
    date.setUTCFullYear(year);
    len = m[0].length;
    if (len == value.length)
	return date;
    var sep = value[len];
    if (sep != '-' && sep != '/' && sep != '.')
	return null;
    value = value.substring(len+1);
    m = value.match('^[0-9]+');
    if (! m)
	return date;
    month = Number(m[0]);
    if (month < 1 || month > 12)
	month = 1;
    date.setMonth(month-1);
    len = m[0].length;
    if (len == value.length || sep != value[len])
	return date;
    value = value.substring(len+1);
    m = value.match('^[0-9]+');
    if (! m)
	return date;
    day = Number(m[0]);
    if (day < 1 || day > 31) 
	day = 1;
    date.setDate(day);
    return date;
}

function datepicker_formatDate(format, date, settings) {
    if (!date) {
	return "";
    }
    var year = date.getUTCFullYear(),
	negative = (year < 0);
    if (negative) {
	year = -year;
    }
    var ret = year.toString();
    while (ret.length < 4) 
	ret = '0' + ret;
    if (negative)
	ret = '-' + ret;
    ret = ret + '-';
    var v = (date.getUTCMonth()+1).toString();
    if (v.length < 2)
	v = '0'+v;
    ret = ret + v + '-';
    v = (date.getUTCDate()).toString();
    if (v.length < 2)
	v = '0'+v;
    ret = ret + v;
    return ret;
}

function datepicker__formatDate(inst, day, month, year) {
    var date;
    if (!day) {
	inst.currentDay = inst.selectedDay;
	inst.currentMonth = inst.selectedMonth;
	inst.currentYear = inst.selectedYear;
	date = new Date(Date.UTC(inst.currentYear, inst.currentMonth, inst.currentDay));
	date.setUTCFullYear(inst.currentYear);
	this._daylightSavingAdjust(date);
    }
    else if (typeof day !== "object") {
	date = new Date(Date.UTC(year, month, day));
	date.setUTCFullYear(year);
	this._daylightSavingAdjust(date);
    }
    return this.formatDate(this._get(inst, "dateFormat"), date, this._getFormatConfig(inst));
}

var datepicker_options = {
    dateFormat: "yy-mm-dd"
};

(function( $, dp ){
    $.datepicker.parseDate = datepicker_parseDate;
    $.datepicker.formatDate = datepicker_formatDate;
    $.datepicker._formatDate = datepicker__formatDate;
}( jQuery, jQuery.ui.datepicker ));

function bind_faceted_widgets() {
    $('.facetview_morefacetvals').click(morefacetvals);
    $('.facetview_toggle').click(facet_toggle);
    $('.facetview_filtershow').click(showfiltervals);
    $('.facetview_filterlocation').click(filter_location);
    $('.facetview_adaptresolution').click(adapt_resolution);
    $('.facetview_resetlocation').click(reset_location);
}
