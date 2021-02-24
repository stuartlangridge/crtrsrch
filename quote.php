<?php
header("Access-Control-Allow-Origin: *");
header("Content-Type: application/json");
include("query.php");
$epre = preg_match('/^C([0-9]+)E([0-9]+)$/', $_GET["ep"], $epd);
if ($epre == 0) {
    echo json_encode(Array("error" => "bad episode"));
    die();
}
$qu = $_GET["q"];
$results = query($qu, $epd[1], $epd[2]);
$nres = [];
foreach ($results["results"] as $res) {
    $nres[] = Array(
        "link" => $res["episode_yt"] . '&t=' . $res["time_h"] . "h" . $res["time_m"] . "m" . $res["time_s"] . "s",
        "title" => $res["episode_title"],
        "epref" => "{{ep ref|ep=" . $epd[1] . "x" . $epd[2] . "|" . $res["time_h"] . ":" . str_pad($res["time_m"], 2, "0") . ":" . str_pad($res["time_s"], 2, "0") . "}}",
        "line" => $res
    );
}
echo(json_encode($nres));
?>