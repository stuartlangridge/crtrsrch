<?php

ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

function begone() {
    echo "Sorry, I couldn't work out which episode that was about.";
    die();
}

$c = intval($_GET["c"]);
$e = intval($_GET["e"]);
$h = intval($_GET["h"]);
$m = intval($_GET["m"]);
$s = intval($_GET["s"]);

if ($c < 1 || $e < 1 || $h < 0 || $h > 23 || $m < 0 || $m > 59 || $s < 0 || $s > 59) { begone(); }

$db = new SQLite3('cr.db');
$sql = <<<SQL
select l.time_h, l.time_m, l.time_s from episode e 
inner join line l  on e.id = l.episode_id
where e.campaign = :c and e.episode = :e
and (l.time_h * 3600) + (l.time_m * 60) + (l.time_s) <= :secs
order by (l.time_h * 3600) + (l.time_m * 60) + (l.time_s) desc 
limit 1
SQL;
$statement = $db->prepare($sql);
$statement->bindValue(':c', $c);
$statement->bindValue(':e', $e);
$statement->bindValue(':secs', ($h * 3600) + ($m * 60) + $s);
$results = $statement->execute();
$row = $results->fetchArray();
if ($row === FALSE) {
    begone();
}
$link = "html/cr" . $c . "-" . $e . ".html#l" . $row[0] . "h" . $row[1] . "m" . $row[2] . "s";
header("Location: " . $link);
