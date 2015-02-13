<?php 
	echo "hello :D \n";
	// Get cURL resource
	$curl = curl_init();
	// Set some options - we are passing in a useragent too here
	// Austria+invaded+and+fought+the+Serbian+army+at+the+Battle+of+Cer+and+Battle+of+Kolubara+beginning+on+12+August.
	curl_setopt_array($curl, array(
	    CURLOPT_RETURNTRANSFER => 1,
	    CURLOPT_URL => 'http://traces1.saclay.inria.fr:8090/service/processNERDText?text='.$_GET['text'].'&onlyNER=false&shortText=false&nbest=false&sentence=false&format=JSON&customisation=generic',
	    CURLOPT_USERAGENT => 'Codular Sample cURL Request'
	));
	// Send the request & save response to $resp
	$resp = curl_exec($curl);
	// Close request to clear up some resources
	curl_close($curl);


	echo $resp;
?>
