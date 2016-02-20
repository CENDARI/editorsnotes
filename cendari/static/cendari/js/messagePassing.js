/** Handle message passing between the different IFrames in the main CENDARI GUI. (wjwillett)

To send a message to an IFrame (from within another) call:
    parent.postMessage(options,origin);
    - where 'options' is an object with parameters
        'messageType': A string from MESSAGE_TYPES (below)
        'targetWindowIds': A string or array of strings, each containing the id of an IFrame or a div that contains it
        'entityIds': An array containing the Ids of the entities that should be manipulated.
        + any additional parameters you want (for example you can send an additional 
          'highlightMode'[=1,2,3] parameter to the visualizations view along with a 'highlight'
          message to control the color of the highlighting.)
    - and 'origin' is the root url of the site (you can get this from document.location.origin);


To recieve messages sent from another IFrame:
    (1) Set up a listener using:
    if(window.addEventListener) addEventListener("message", handleHighlightMessage, false);
    else attachEvent("onmessage", handleHighlightMessage);
    - where handleHighlightMessage is a function that recieves one argument with properties:
        'origin': Check to make sure it came from the same domain!
        'data': The parameters object sent from the other IFrame - should 
                have 'messageType', 'targetWindowIds', and 'entityIds' properties as described above.
                Check the message type and handle it appropriately.
    (2) Send a message indicating that this Window is ready to recieve messages, by calling:
    parent.postMessage(options,origin);
    - where 'options' is an object with parameters
        'messageType': 'cendari_ready' (you can also send 'cendari_wait' to postpone reception)
        'windowId': A string containing the id of this IFrame or a div that contains it
    - and 'origin' is the root url of the site (you can get this from document.location.origin);
**/

// List of standard message types that will be forwarded between windows
var MESSAGE_TYPES = ['cendari_highlight', 'cendari_ready', 'cendari_wait'];

// List of possible states for target windows. If no state is set, assume the window is not ready.
var TARGET_STATES = ['cendari_isready', 'cendari_iswaiting'];

// Lookup for storing window states, indexed by the window id
var statesByWindowId = {};

// Look for storing FIFO queues of messages for windows that are not ready, indexed by the window id
var messageQueuesByWindowId = {};

/**
 * Handle messages recieved from IFrames.
 */
function handleMessage(event){

  //check that the message is of an approved type, otherwise it probably isn't for/from us.
  if(!event.data.messageType || MESSAGE_TYPES.indexOf(event.data.messageType) == -1){
    return;
  }
  //check that message is originates from the same domain
  if(event.origin != window.location.origin){
    console.error('Recieved message is not from this domain.');
    return; 
  }
  //check that the message has a data object 
  if(!event.data){
    console.error('Recieved message has no data object.');
    return;
  }
  //handle state-setting messages
  if(event.data.messageType == 'cendari_wait' || event.data.messageType == 'cendari_ready')
    setTargetState(event);
  //forward coordination messages
  else if(event.data.messageType == 'cendari_highlight')
    forwardMessage(event);
}


/**
 * Handle messages that track the state of a window.
 */
function setTargetState(event){

  //check that a windowId is specified.
  if(!event.data.windowId){
    console.error('Recieved state message does not specify a windowId.');
    return;
  }

  //set the window state
  if(event.data.messageType == 'cendari_wait'){
    statesByWindowId[event.data.windowId] = 'cendari_iswaiting';
  }
  else if(event.data.messageType == 'cendari_ready'){
    statesByWindowId[event.data.windowId] = 'cendari_isready';

    //if there are queued messages for the target, forward them
    if(messageQueuesByWindowId[event.data.windowId]){
      for(var i = 0; i < messageQueuesByWindowId[event.data.windowId].length; i++)
        forwardMessage(messageQueuesByWindowId[event.data.windowId].shift());
    }
  }
}


/**
 * Forward coordination messages between IFrames. 
 **/
function forwardMessage(event){
    
  //check that targets are specified.
  if(!event.data.targetWindowIds || event.data.targetWindowIds.length == 0){
    console.error('Recieved message does not specify any targets.');
    return;
  }

  //if targetWindowIds is a string, wrap it as an array
  if(typeof event.data.targetWindowIds == 'string')
    event.data.targetWindowIds = [event.data.targetWindowIds];

  //try to pass the message to each target panel
  for(var i=0; i < event.data.targetWindowIds.length; i++){
    var targetWindowId = event.data.targetWindowIds[i];

    //check that the target exists and contains (or is) an IFrame
    if(!targetWindowId || !document.getElementById(targetWindowId) || 
       document.getElementById(targetWindowId).getElementsByTagName('iframe').length < 1){
      console.error('target of the recieved message ("' + targetWindowId + '") does not have a matching IFrame.');
      continue;
    }

    //if the window has signaled that it is ready, pass the message to the matching IFrame's content window...
    if(statesByWindowId[targetWindowId] == 'cendari_isready'){
      //pass the message to the
      var win = document.getElementById(targetWindowId).getElementsByTagName('iframe')[0].contentWindow;
      win.postMessage(event.data, event.origin);
    }
    // ... otherwise queue it to send later.
    else{
      messageQueuesByWindowId[targetWindowId] = messageQueuesByWindowId[targetWindowId] || [];
      messageQueuesByWindowId[targetWindowId].push(event);
    }
  }
}




//Attach listener for messages to the window
if(window.addEventListener) addEventListener("message", handleMessage, false);
else attachEvent("onmessage", handleMessage);
