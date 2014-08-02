<?php
header('content-type: application/json; charset=utf-8');
header("access-control-allow-origin: *");


if (isset($_REQUEST['q'])) {
	$q = trim($_REQUEST['q']);
}

if ((!(isset($q))) || (!($q)) ) {
	$json['errors'] = 'Request Error q not defined';
	$json = json_encode($json);
	echo isset($_GET['callback']) ? "{$_GET['callback']}($json)" : $json;
	exit;
} else {


	$descriptorspec = array(
		0 => array(
			"pipe",
			"r"
		) , // stdin
		1 => array(
			"pipe",
			"w"
		) , // stdout
		2 => array(
			"pipe",
			"w"
		) , // stderr
	);
	$dir = getcwd();
	$cmd = "python $dir/gsearch.py $q";

	$stderr1="";
/*
	$process = proc_open($cmd, $descriptorspec, $pipes);
	$stderr1 = stream_get_contents($pipes[2]);
	fclose($pipes[2]);
	$ret = proc_close($process);
	*/
	shell_exec($cmd);
	//echo $cmd;


  
  if(file_exists("$q.json")){
    $string = file_get_contents("$q.json");
    $json = json_decode($string, true);
  }else{
    $json = Array();
    $json['errors'] = 'Groove Error: '. $cmd .$stderr1;
  }
  
  $json = json_encode($json);
  echo isset($_GET['callback']) ? "{$_GET['callback']}($json)" : $json;

}

?>