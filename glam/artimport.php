<?php

function trimParam($param) {
	return mysql_real_escape_string(trim($param, "\" "));
}

print 'start' . PHP_EOL;

$ts_pw = posix_getpwuid(posix_getuid());
$ts_mycnf = parse_ini_file('/home/aude/.my.cnf');
$db = mysql_connect('sql', 'aude', $ts_mycnf['password']) or die('could not connect: ' . mysql_error());
mysql_select_db("u_aude");
unset($ts_mycnf, $ts_pw);

$lines = file("smithsonian-americanart.csv");

$i = 0;

$sql_other = "INSERT INTO archivesamericanart (name, type, city, state) VALUES ('%s', '%s', '%s', '%s')";
$sql_artist = "INSERT INTO archivesamericanart (name, last, first, type, city, state) VALUES ('%s', '%s', '%s', '%s', '%s', '%s')";

foreach ( $lines as $linenum => $line ) {
	$arg = explode("\t", $line);
	$type = trimParam($arg[2]);
	$city = trimParam($arg[3]);
	$state = trimParam($arg[4]);

	if ( $type == 'artist' ) {
		$last = trimParam($arg[0]);
		$first = trimParam($arg[1]);
		$query = sprintf($sql_artist, 
			$first . " " . $last,
			$last,
			$first,
			$type,
			$city,
			$state
		);
	} else {
		$query = sprintf($sql_other,
			trimParam($arg[0]),
			$type,
			$city,
			$state
		);
	}
	mysql_query($query);	
}

print 'done';

?>
