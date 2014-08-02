<?php
header('content-type: application/json; charset=utf-8');
header("access-control-allow-origin: *");

if (isset($_REQUEST['name'])) {
	$name = trim($_REQUEST['name']);
}
if (isset($_REQUEST['id'])) {
	$id = trim($_REQUEST['id']);
}

if ( ((!(isset($id))) || (!($id)))  || ((!(isset($name))) || (!($name))) ) {
	$json['errors'] = 'Request Error id OR name not defined';
	$json = json_encode($json);
	echo isset($_GET['callback']) ? "{$_GET['callback']}($json)" : $json;
	exit;
} else {

if(!(file_exists("$name.mp3"))){
  
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
      $cmd = "python $dir/gdown.py  $id $name";

      $process = proc_open($cmd, $descriptorspec, $pipes);
      $stderr1 = stream_get_contents($pipes[2]);
      fclose($pipes[2]);
      $ret = proc_close($process);
		}
		$json = Array();
	if(file_exists("$name.mp3")){
    $json['download'] = true;
    $json['id'] = $id;
    $json['name'] = $name;
	}else{
    $json['download'] = false;
    $json['id'] = $id;
    $json['name'] = $name;
	}
  $json = json_encode($json);
  echo isset($_GET['callback']) ? "{$_GET['callback']}($json)" : $json;
}


?>