


/**
 * Vis definitions can include.
    - visualization: 'histogram', 'timeline', 'map'
    - value: function used to map item to a key for aggregation
    - inputFilter: function to run on items to determine if they should be included (return a boolean)
    - resultsFilter: function to run on values produced by the value method to determine if item should be included (return a boolean)
    - label: function used to determine the label for an item
    - location: (maps only) function used to determine the lat-lon position of an item
    - maxLabelLength: integer length beyond which labels will be abbreviated
    - format: function used to format output values
    - entityTypeClass: (optional) class to add to the visualization indicating the type of data
    Labels (specifying label text will cause that label to be displayed):
    - maxLabel: show item with largest value
    - minLabel: show item with smallest value
    - medianLabel: show item with median value
    - meanLabel: show mean value
**/



/** 
 * Construct a set of visualizations inside the target element based on the 
 * data and set of vis definitions provided.
 */ 
function buildVisualizations(dataObjects, visDefinitions, target){

  //perform any aggregation and processing specified in the vis definition
  //aggregated values are stored in the vis definitions
  aggregateForVis(dataObjects, visDefinitions);

  //Construct a panel for each visualization
  d3.select(target).selectAll('.panel').data(visDefinitions)
    .enter().append('div')
     .attr('class', function(d){
      //If specified, add a special class to the panel to indicate the type of data
      return 'panel' + (d.entityTypeClass ? ' ' + d.entityTypeClass : '');
     })
     .html(function(d) {

      //For each panel include a div containing all of 
      // the titles specified in the vis definition
      var output = "<div class='panelText'>"
      if(!d.filteredItems || d.filteredItems.length < 1){
        output += '<span class="value">Add some ' +
                  (d.entityTypeClass ? ' <strong>' + d.entityTypeClass + '</strong> ': '') + 
                  'entities to see a ' + d.visualization + ' here.</span>';
        return output;
      }
      if(!d.maxLabelLength) d.maxLabelLength = 50;
      if(d.maxLabel && d.maxItem){
        output += (d.maxLabel + ' <span class="title" guid="' + d.maxItem.guid + '">' + 
                   abbreviateString(d.label(d.maxItem), d.maxLabelLength) + '</span> ' + 
                   '<span class="value">' + (d.format ? d.format(d.max) : d.max) + '</span><br>');
      }
      if(d.minLabel && d.minItem){
        output += (d.minLabel + ' <span class="title" guid="' + d.minItem.guid + '">' + 
                   abbreviateString(d.label(d.minItem), d.maxLabelLength) + '</span> ' + 
                   '<span class="value">' + (d.format ? d.format(d.min) : d.min) + '</span><br>');
      }
      if (d.meanLabel){
        output += (d.meanLabel + 
                   ' <span class="value">' + (d.format ? d.format(d.mean) : d.mean) + '</span><br>');
      }
      if (d.medianLabel && d.median){
        output += (d.medianLabel + ' <span class="title" guid="' + d.medianItem.guid + '">' + 
                   abbreviateString(d.label(d.medianItem), d.maxLabelLength) + '</span> ' + 
                   '<span class="value">' + (d.format ? d.format(d.median) : d.median) + '</span><br>');
      }
      if (d.mostFrequentLabel && d.mostFrequent){
        output += (d.mostFrequentLabel + ' <span class="title">' + 
                   abbreviateString(d.label(d.mostFrequentItem), d.maxLabelLength) + '</span> ' + 
                   '<span class="value">' + (d.format ? d.format(d.mostFrequentCount) : d.mostFrequentCount) +
                   '</span><br>');
      }
      if (d.leastFrequentLabel && d.leastFrequent){
        output += (d.leastFrequentLabel + ' <span class="title">' +
                   abbreviateString(d.label(d.leastFrequentItem), d.maxLabelLength) + '</span> ' +
                   '<span class="value">' + (d.format ? d.format(d.leastFrequentCount) : d.leastFrequentCount) +
                   '</span><br>');
      }
      output += '</div>';
      return output;
    }).each(placeAndRenderVisualization)
      .on('mouseleave', onVisLeave);

    //re-render visualziations when the page size changes
    d3.select(window).on('resize',function(){
      d3.selectAll('.panel').each(placeAndRenderVisualization);
      refreshHighlights();
    });
}


/**
 * Add the visualization containers and call chart-specific rendering methods.
 **/
function placeAndRenderVisualization(d){
  //Create and position the tooltip and a holder for the visualization
  var panel = d3.select(this);
  panel.selectAll('.panelTip, .panelVis').remove();
  var panelVis = d3.select(this).append('div').classed('panelVis', true);
  var panelTip = d3.select(this).append('div').classed('panelTip', true);
  
  //Size the visualization to fit the leftover space to the right of the text block.
  //If it is too small to fit there, move it below. 
  //we enforce minimum heights and widths here, but larger sizes can be set 
  var panelWidth = this.clientWidth - parseInt(panel.style('margin-right')) - parseInt(panel.style('margin-left'));
  var panelTipWidth = panelTip[0][0].clientWidth;
  var minVisWidth = 300; 
  var minVisHeight = 30;
  panelVis.style('min-height', minVisHeight)
          .style('min-width', minVisWidth)
          .style('width', (panelWidth - panelTipWidth) <  minVisWidth ?
                           panelWidth : panelWidth - panelTipWidth);

  //Render the visualization itself 
  if (d.visualization == 'histogram')
    buildHistogram(d.filteredItems, panelVis);
  else if(d.visualization == 'timeline')
    buildTimeline(d.filteredItems, panelVis);
  else if(d.visualization == 'map')
    buildMap(d.filteredItems, panelVis);
}


/**
 * Constructs a histogram visualization.
 **/
function buildHistogram(histogramData, element, maxBars, barWidth) {

  var histogram = element.classed('histogram', true);
  var height = parseInt(element.style('height'));
  var width = parseInt(element.style('width'));
  barWidth = barWidth || 5;
  maxBars = maxBars || width / (barWidth - 1) - 2;

  histogramData.sort(function(a, b) {
    return b._value - a._value;
  });
  // Clip items out of the middle to meet the specified max number of bars
  if (maxBars < histogramData.length) {
    histogramData.splice(Math.ceil(maxBars / 2), histogramData.length - maxBars);
  }

  // Build the histogram
  var chart = histogram.append('svg').attr('height', height).attr('width', width);
  var yScale = d3.scale.linear().domain([0, d3.max(histogramData, function(d) {
    return d._value
  })]).range([2, height]);
  var barsEnter = chart.selectAll('.mark').data(histogramData).enter().append('g').attr('class', 'mark')
    .attr('x', function(d, i) {
      return i * barWidth - .5;
    });
  barsEnter.append('rect').attr('x', function(d, i) {
      return i * barWidth - .5;
    }).attr('y', 0).attr('width', barWidth).attr('height', height);
  barsEnter.append('rect').attr('x', function(d, i) {
      return i * barWidth - .5;
    }).attr('y', function(d) {
      return height - yScale(d._value) - .5;
    }).attr('width', barWidth).attr('height', function(d) {
      return yScale(d._value);
    });

  // Replace some middle bars with an ellipsis if we're clipping the histogram
  if (maxBars == histogramData.length) {
    var cutPoint = Math.floor(maxBars / 2);
    chart.select('.mark:nth-child(' + cutPoint + ')').remove();
    chart.select('.mark:nth-child(' + cutPoint + ')').remove();
    chart.append('text').text('...').attr('y', height - 1).attr('x', function(d, i) {
      return (cutPoint - 0.8) * barWidth - 1
    });
  }

  // Display information on hover and hide on leave
  histogram.selectAll('.mark').on('mouseover', onVisHover);
  
}


/**
 * Constructs a timeline visualization.
 **/
function buildTimeline(timelineData, element) {
  var timeline = element.classed('timeline', true);
  var height = parseInt(element.style('height'));
  var width = parseInt(element.style('width'));
  
  // Build the timeline
  var chart = timeline.append('svg').attr('height', height).attr('width', width);
  var unixTimeExtent = d3.extent(timelineData, function(d) { return Number(d._value)});
  var dateTimeExtent = [new Date(Number(unixTimeExtent[0])),new Date(Number(unixTimeExtent[1]))];
  var xLinearScale = d3.scale.linear().domain(unixTimeExtent).range([0, width]);
  var xTimeScale = d3.time.scale().domain(dateTimeExtent).range([0, width]).nice();
  var xAxis = d3.svg.axis().scale(xTimeScale).orient('bottom').ticks(Math.floor(width/60));

  chart.selectAll('.mark').data(timelineData).enter().append('rect').attr('class', 'mark')
                    .attr('x', function(d){ return xLinearScale(d._value)}).attr('y', 0)
                    .attr('width', 1).attr('height', height-10);
  chart.append('g').attr('class', 'x axis')
        .attr('transform', 'translate(0,' + (height - 10) + ')')
        .call(xAxis)
       .selectAll('text').attr('y', 2).attr('x', 2).style('text-anchor', 'start');

  // Display information on hover and hide on leave
  timeline.selectAll('.mark').on('mouseover', onVisHover);
}


/**
 * Constructs a map visualization.
 **/
function buildMap(mapData, element, useCounts){
  var map = element.classed('map', true).attr('id','leafletmap');
  var height = parseInt(element.style('height'));
  var width = parseInt(element.style('width'));
  
  var maxZoom = 10, minZoom = 3, defaultZoom = 3;
  var minPointSize = 6, maxPointSize = 15;

  if(mapData.length < 1) return;

  //process location string into lat/lon values
  for(var i = 0; i < mapData.length; i++){
    var item = mapData[i];
    var latLon = item._location;
    if(!latLon) continue;
    var latLonSplit = latLon.split(', ');
    if(latLonSplit.length != 2) continue;
    var lat = Number(latLonSplit[0]);
    var lon = Number(latLonSplit[1]);
    if(lat == 0 && lon == 0) continue;
    item._lat = lat;
    item._lon = lon;
  }

   
  var latExtent = d3.extent(mapData, function(d){return d._lat;});
  var lonExtent = d3.extent(mapData, function(d){return d._lon;});
  var latScale = d3.scale.linear().domain(latExtent).range([height - maxPointSize/2, maxPointSize/2]);
  var lonScale = d3.scale.linear().domain(lonExtent).range([maxPointSize/2, width - maxPointSize/2]);
  var sizeScale = d3.scale.linear().domain(d3.extent(mapData, function(d){return d._value;})).range([minPointSize/2, maxPointSize/2]);

  //Using Leaflet (instead of D3) for basemap
  var leafletMap = L.map('leafletmap',{attributionControl:false, minZoom:minZoom, maxZoom:maxZoom})
                    .setView([(latExtent[0]+latExtent[1])/2,(lonExtent[0]+lonExtent[1])/2], defaultZoom);
  L.tileLayer(document.location.protocol + '//{s}.tiles.mapbox.com/v4/wjwillett.i9o7e0g1/{z}/{x}/{y}.png?access_token=pk.eyJ1Ijoid2p3aWxsZXR0IiwiYSI6IlJtUlFYVkEifQ.Qk10zoCrd2pTN6t2rcyifQ').addTo(leafletMap);
  for(var i=0; i < mapData.length; i++){
    var d = mapData[i];
    var mark = L.circleMarker([d._lat,d._lon],{'className':'mark', opacity:1.0, weight:0.4, fillOpacity: 1.0})
                .setRadius(sizeScale(d._value)).addTo(leafletMap); 
    //associate a data tuple with the mark (to mimic D3)
    mark._path.__data__ = d;   
  }

  // Display information on hover and hide on leave
  map.selectAll('.mark').on('mouseover', onVisHover);
  map.selectAll('.mark').on('mouseout', onVisLeave);

  // (NB) Load entity form on mouse click
  map.selectAll('.mark').on('click', onVisClick);
}


/** 
 * Perform aggregations and filtering necessary
 * for each of the vis definitions.
 */ 
function aggregateForVis(items, visDefinitions) {
  // For each vis definition ...
  for (var ci in visDefinitions) {
    var visDef = visDefinitions[ci];
    //Ensure the vis definition has a label function (default to the value)
    if(!visDef.label) visDef.label = visDef.value;

    //Process the data by running the provided functions
    visDef.values = [];
    visDef.filteredItems = [];
    visDef.itemsByValueIndex = {};
    for (var ni in items) {
      var itemData = items[ni];

      //if provided, calculate the location
      if(visDef.location){
        itemData._location = visDef.location(itemData);
        if(!itemData._location) continue;
      }

      //filter out unwanted input items before applying the map function
      if(visDef.inputFilter && !visDef.inputFilter(itemData)) continue;
      
      //compute the value to show for this item
      var value = visDef.value(itemData);

      //filter out unwanted results
      if(visDef.resultFilter && !visDef.resultFilter(value)) continue;

      // Save and index the values and items that passed the filter
      itemData._value = value;
      visDef.filteredItems.push(itemData);
      var indexedByValueResult = visDef.itemsByValueIndex[value] || [];
      indexedByValueResult.push(itemData);
      visDef.itemsByValueIndex[value] = indexedByValueResult;
      visDef.values.push(value);
    }

    //Then reduce and record the map results into summary statistics
    if (visDef.values.length > 0) {
      var sum = 0;
      for (var ri in visDef.values)
      sum += visDef.values[ri];
      visDef.values.sort(function(a, b) {
        return a - b
      });
      visDef.min = visDef.values[0];
      visDef.minItem = visDef.itemsByValueIndex[visDef.min][0];
      visDef.max = visDef.values[visDef.values.length - 1];
      visDef.maxItem = visDef.itemsByValueIndex[visDef.max][0];
      visDef.median = visDef.values[Math.floor(visDef.values.length / 2)];
      visDef.medianItem = visDef.itemsByValueIndex[visDef.median][0];
      visDef.mean = sum / visDef.values.length;
    }
  }
  return visDefinitions;
}


/**
 * Trigger selections when a visualization is hovered.
 */
function onVisHover(){
  var itemData = d3.select(this).datum();

  // post a message to highlight in other panes
  parent.postMessage({'messageType':'cendari_highlight',
                      'targetWindowIds':'east',
                      'entityIds':[itemData.id],
                      'highlightMode':2},
                       document.location.origin);

  // log the hover event
  var visDivRaw = getParentVisPanel(this);
  var visDiv = d3.select(visDivRaw);
  var visDef = visDiv.datum();
  logHover(itemData, visDef);
}


/**
 * Removes selections a visualization is unhovered.
 */
function onVisLeave(){
    // post a message to unhighlight in other panes
  parent.postMessage({'messageType':'cendari_highlight',
                      'targetWindowIds':'east',
                      'entityIds':[],
                      'highlightMode':2},
                       document.location.origin);
  // cancel logging of the hover event
  cancelLogHover();
}


/**
 * (NB) Trigger selections and page upload when a visualization is clicked.
 */
function onVisClick(){
  var itemData = d3.select(this).datum();
  //console.log('NB................................ clicking on mark: ' + itemData);
  // post a message to highlight in other panes
  parent.postMessage({'messageType':'cendari_highlight',
                      'targetWindowIds':'east',
                      'entityIds':[itemData.id],
                      'highlightMode':2},
                       document.location.origin);

  // log the hover event
  var visDivRaw = getParentVisPanel(this);
  var visDiv = d3.select(visDivRaw);
  var visDef = visDiv.datum();
  logHover(itemData, visDef);

  if(parent.location.href.indexOf(itemData.url)==-1){
	var r = confirm("Are you sure you want to leave this page? If you press 'OK', you might loose unsaved work.");
  	if (r == true) {
		window.open(itemData.url, "_parent");
	}
  } 
}


/**
 * Takes a sub element of a visualization (usually a mark, although it can also be the panel,
 * or any element in-between them in the tree) and 
 * returns the outside container panel for the vis.
 */
function getParentVisPanel(element){
    if(element == null || element == document.body) 
      return null;
    else if(d3.select(element).classed('panel'))
      return element;
    else return getParentVisPanel(element.parentNode);
}

/**
 * Tracks and logs cells that are hovered for more than 1s
 */ 
var hoveredItemData;
var hoveredPanelData;
var hoverLogTimer;
function logHover(itemData, panelData){
  if(itemData != hoveredItemData || hoveredPanelData != panelData)
    cancelLogHover();
  hoveredItemData = itemData; 
  hoveredPanelData = panelData; 
  var hoverLogFunction = function(){
    if(!hoveredItemData || !hoveredPanelData)
      return;
    var logJSON = {'panelType': hoveredPanelData.visualization, 
                   'panelLabel': hoveredPanelData.entityTypeClass,
                   'itemName': hoveredItemData.preferred_name,
                   'itemId': hoveredItemData.id};
    console.log("LOGGED-HOVER: " + JSON.stringify(logJSON));
    //trace.event("_user","hover","visualizations",logJSON);  
  }
  hoverLogTimer = setTimeout(hoverLogFunction, 1000);
}

/** 
 * Cancels the log timer for an element (for example, if unhovered before time elapses.)
 */ 
function cancelLogHover(){
  if(hoverLogTimer) clearTimeout(hoverLogTimer);
  hoverLogTimer = null;
  hoveredItemData = null;
  hoveredPanelData = null;
}



/**
 * Highlights items in the visualization with the matching Ids.
 * Multiple levels of highlighting can be simultaneously applied. If no level 
 * is specified, all matching marks will be styled using the first level of highlighting. 
 * If an item is highlighted with multiple levels, the higher overrides.
 */
var highlights = {}
function highlightVis(entityIds,level){
  //console.log("::::::::::::::::::::::::::: highlightVis called with entityIds,level=" +entityIds + "," + level);
  level = level || 1;
  if(level % 1 === 0 && level > 0 && Array.isArray(entityIds)){
    highlights[level] = entityIds;
  }
  refreshHighlights();
}


/**
 * Remove all highlights at the specified highlighting level (or at all levels, if none specified).
 */
function removeHighlights(level){
  if(level % 1 === 0 && level > 0)
    highlights[level] = [];
  else if(level === undefined){
    for(var l in Object.keys(highlights)) highlights[l] = [];
  }
  refreshHighlights();
}


/**
 * Refresh and re-render highlights
 */
function refreshHighlights(){
  var levels = Object.keys(highlights).sort().reverse();
  
  // Clear highlighting if no highlights exist, otherwise, de-emphasize all points
  var selectionsExist = false;
  for(var l in levels){
    if(highlights[levels[l]].length > 0){
      selectionsExist = true;
      break;
    }
  }
  d3.selectAll('.mark').classed('deselected', selectionsExist);

  // For each panel, highlight marks and display a panel tip if necessary
  d3.selectAll('.panel').each(function(visDef){
    var visDiv = d3.select(this);
    var selectedItems = [];
    var highestSelectedLevel = 0;

    // Highlight marks
    visDiv.selectAll('.mark').each(function(itemData){
      if(itemData == null){
        itemData = {};
      }
      var item = d3.select(this);
      var highlightLevel = 0;
      for(var li in levels){
        var l = parseInt(levels[li]);
        var highlightClass = 'highlight' + l;
        if(highlightLevel > l)
          item.classed(highlightClass, false);
        else if(highlights[l].indexOf(itemData.id) != -1){
          highlightLevel = l;
          item.classed(highlightClass, true).classed('deselected',false);
          if(highlightLevel > highestSelectedLevel){
            highestSelectedLevel = highlightLevel;
            selectedItems = [];
          }
          if(highlightLevel == highestSelectedLevel) 
            selectedItems.push(itemData);
        }
        else item.classed(highlightClass, false);
      }
    });

    // Display the panel tip if only one item in the view is selected at the highest level
    var tip = visDiv.select('.panelTip');
    if(selectedItems.length == 1){
      var itemData = selectedItems[0];
      tip.html('<span class="value">' + (visDef.format ? visDef.format(itemData._value) : itemData._value) + ' &#8212;</span><br>' + 
               '<span class="title">' + abbreviateString(visDef.label(itemData), visDef.maxLabelLength) + '</span>')
        .style('display', 'block').transition().style('opacity', '1');
      visDiv.select('.panelText').transition(0).style('opacity', '0');
    }
    else{
      tip.style('display', 'none').transition(0).style('opacity', '0');
      visDiv.select('.panelText').transition().style('opacity', '1');
    }
  });

}


/** 
 * Add listeners for messages from other panels that should trigger highlights.
 **/
function setupHighlightMessageReciever(){
  var handleHighlightMessage = function(event){
    //check that message is from the same origin
    if(event.origin != window.location.origin){
      console.error('Recieved message is not from the same domain!');
      return; 
    }
    //check that the message is a higlight
    if(!event.data || event.data.messageType != 'cendari_highlight'){
      console.error('Recieved message is not cendari_highlight type!',event.data.messageType);
      return;
    }
    //TODO: check to see that the data is actually an array of keys
    var entityIds = event.data.entityIds;
    var highlightMode = event.data.highlightMode;

    //console.log('::::::::::::message::::::::::::')
    //console.log(entityIds,highlightMode);
    //console.log('::::::::::::message::::::::::::')

    highlightVis(entityIds, highlightMode);
  };

  //attach message handler (alt versions for IE/Webkit)
  if(window.addEventListener) addEventListener("message", handleHighlightMessage, false);
  else attachEvent("onmessage", handleHighlightMessage);

  //let the message passing coordinator know we're ready to receive 
  parent.postMessage({'messageType':'cendari_ready', 'windowId':'east'}, document.location.origin);

}


/** 
 * Given a dict of arrays, return the keys sorted by frequency low->high
 **/
function sortKeysByArraySize(dictOfArrays) {
  var keys = [];
  for (var key in dictOfArrays)
  keys.push(key);
  keys.sort(function(a, b) {
    return dictOfArrays[a].length - dictOfArrays[b].length;
  });
  return keys;
}


/** 
 * Abbreviates a string to fit within the character limit provided
 **/
function abbreviateString(input, maxLength){
  var string = "" + input; //guarantee its actually a string...
  var words = string.split(" ");
  var abbreviated = '';
  for(var wi in words){
    var word = words[wi];
    if(wi == words.length - 1 && abbreviated.length + word.length + 1 <= maxLength)
      abbreviated += ' ' + word;
    else if(abbreviated.length + word.length + 4 <= maxLength) 
      abbreviated += ' ' + word;
    else if(abbreviated.length == 0)
      abbreviated += word.slice(0,maxLength - 3);
    else{
      abbreviated += '...';
      break;
    }
  }
  return abbreviated;
}


/**
 * Print numbers with commas.
 * From: http://stackoverflow.com/a/2901298
 **/
function numberWithCommas(x) {
  return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}
