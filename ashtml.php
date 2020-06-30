<?php
include("query.php");
$qu = $_GET["q"];
$encqu = urlencode($_SERVER['QUERY_STRING']);
$cachepath = __dir__ . "/cache/" . $encqu . ".cache";
if (file_exists($cachepath)) {
    echo file_get_contents($cachepath);
    echo "<span data-cached></span>";
} else {
$results = query($qu);
ob_start();

if (count($results) >= 100) {
    echo "<p><small>Search results are limited to the first 100. Refine your search if needed.</small></p>";
}

foreach ($results as $key => $res) {
    echo "<article><div class='thumb'><img class='thumb' src='" . htmlentities($res["thumbnail"]) . "'></div>\n";
    echo "<div class='count'>";
    echo ($key + 1) . "/" . count($results);
    echo "</div>\n<div class='speaker'>";
    echo htmlentities($res["speaker"]);
    echo "</div>\n<div class='episode'>";
    echo "C";
    echo $res["campaign"];
    echo "E";
    echo $res["episode"];
    echo ": <em>";
    echo htmlentities($res["episode_title"]);
    echo "</em> <small>(";
    echo $res["time_h"];
    echo ":";
    printf("%02d", $res["time_m"]);
    echo ":";
    printf("%02d", $res["time_s"]);
    echo ")</small></div>\n<div class='links'>";
    echo '<a href="html/cr';
    echo $res["campaign"];
    echo "-";
    echo $res["episode"];
    echo '.html#l';
    echo $res["time_h"];
    echo "h";
    echo $res["time_m"];
    echo "m";
    echo $res["time_s"];
    echo 's';
    echo '">transcript</a> ';
    echo '<a href="';
    echo $res["episode_yt"];
    echo "&t=";
    echo $res["time_h"];
    echo "h";
    echo $res["time_m"];
    echo "m";
    echo $res["time_s"];
    echo 's">video</a>';
    echo "</div>\n";
    echo "<div class='line'>";
    echo $res["line"];
    echo "</div></article>";
}

if (count($results) >= 100) {
    echo "<p><small>Search results are limited to the first 100. Refine your search if needed.</small></p>";
}

$output = ob_get_clean();
file_put_contents($cachepath, $output);
echo $output;
}
?>