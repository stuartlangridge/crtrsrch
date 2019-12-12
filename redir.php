<?php

ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

function begone() {
    echo "Sorry, I couldn't work out which episode that was about.";
    die();
}

$q = str_replace("-", " ", $_GET["q"]);
if (strpos($q, "%") === FALSE) {
    // not escaped
} else {
    $q = urldecode($q);
}
$parts = explode(" ", $q);
if (count($parts) < 3) {
    begone();
}
$c = intval($parts[0]);
$e = intval($parts[1]);
if ($c == 0 || $e == 0) { begone(); }

$db = new SQLite3('cr.db');
$sql = <<<SQL
select link from episode where campaign = :c and episode = :e
SQL;
$statement = $db->prepare($sql);
$statement->bindValue(':c', $c);
$statement->bindValue(':e', $e);
$results = $statement->execute();
$row = $results->fetchArray();
if ($row === FALSE) {
    begone();
}
$time = preg_match('/^[0-9]+h[0-9]+m[0-9]+s$/', $_GET["time"], $matches);
if ($time != 1) {
    begone();
}
$out = $row[0] . "&t=" . $_GET["time"];
header("Location: " . $out);