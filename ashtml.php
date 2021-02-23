<?php
// based on https://stackoverflow.com/a/7356682/1418014
function merge_querystring($query = null) {
    // $url = 'http://www.google.com.au?q=apple&type=keyword';
    // $query = '?q=banana';
    $url = "index.php?" . $_SERVER["QUERY_STRING"];
    $url_components = parse_url($url);
    // if we have the query string but no query on the original url
    // just return the URL + query string
    if(empty($url_components['query'])) {
        return $url . '?' . ltrim($query, '?');
    }

    parse_str($url_components['query'], $original_query_string);
    parse_str(parse_url($query,PHP_URL_QUERY),$merged_query_string);

    $merged_result = array_merge($original_query_string,$merged_query_string);

    if (array_key_exists("lm", $merged_result) && $merged_result["lm"] == "") {
        unset($merged_result["lm"]);
    }

    return str_replace($url_components['query'], http_build_query($merged_result), $url);
}


include("query.php");
$qu = $_GET["q"];
$encqu = urlencode($_SERVER['QUERY_STRING']);
$cachepath = __dir__ . "/cache/" . $encqu . ".cache";
// cache times out after some time so that if new shows have arrived with matches
// for an already cached query, the problem will eventually right itself
if (file_exists($cachepath) && (time()-filemtime($cachepath)) < 60 * 60 * 24 * 3) {
    echo file_get_contents($cachepath);
    echo "<span data-cached></span>";
} else {
$results = query($qu);
ob_start();

echo "<div class='warnings'>\n";
if ($results['count'] >= 100) {
    echo "<p><small>Search results are limited to the first 100 (of ";
    echo $results["count"];
    echo " for this search). Refine your search if needed.</small></p>";
}

if ($results['count'] >= 100 || isset($_GET["lm"])) {
    echo "<p><small>Show ";
    if (isset($_GET["lm"])) {
        echo '<a href="' . htmlentities(merge_querystring('?lm=')) . '">all</a> or '; 
    }
    echo "only Campaign 1: ";

    if (isset($_GET["lm"]) && $_GET["lm"] == "1-a") {} else {
        echo '<a href="' . htmlentities(merge_querystring('?lm=1-a')) . '">'; }
    echo "episodes 1-50";
    if (isset($_GET["lm"]) && $_GET["lm"] == "1-a") {} else { echo '</a>'; }
    echo " | ";

    if (isset($_GET["lm"]) && $_GET["lm"] == "1-b") {} else {
        echo '<a href="' . htmlentities(merge_querystring('?lm=1-b')) . '">'; }
    echo "51-100";
    if (isset($_GET["lm"]) && $_GET["lm"] == "1-b") {} else { echo '</a>'; }
    echo " | ";

    if (isset($_GET["lm"]) && $_GET["lm"] == "1-c") {} else {
        echo '<a href="' . htmlentities(merge_querystring('?lm=1-c')) . '">'; }
    echo "101-end";
    if (isset($_GET["lm"]) && $_GET["lm"] == "1-c") {} else { echo '</a>'; }
    echo " | ";

    echo "Campaign 2: ";

    if (isset($_GET["lm"]) && $_GET["lm"] == "2-a") {} else {
        echo '<a href="' . htmlentities(merge_querystring('?lm=2-a')) . '">'; }
    echo "1-50";
    if (isset($_GET["lm"]) && $_GET["lm"] == "2-a") {} else { echo '</a>'; }
    echo " | ";

    if (isset($_GET["lm"]) && $_GET["lm"] == "2-b") {} else {
        echo '<a href="' . htmlentities(merge_querystring('?lm=2-b')) . '">'; }
    echo "51-100";
    if (isset($_GET["lm"]) && $_GET["lm"] == "2-b") {} else { echo '</a>'; }
    echo " | ";

    if (isset($_GET["lm"]) && $_GET["lm"] == "2-c") {} else {
        echo '<a href="' . htmlentities(merge_querystring('?lm=2-c')) . '">'; }
    echo "101-end";
    if (isset($_GET["lm"]) && $_GET["lm"] == "2-c") {} else { echo '</a>'; }

    echo "</small></p>";
}
echo "</div><!--warnings-->\n";

$rcount = $results["count"];
if ($rcount > 100) {
    $rcount = 100;
}

foreach ($results['results'] as $key => $res) {
    echo "<article><div class='thumb'><img class='thumb' src='" . htmlentities($res["thumbnail"]) . "'></div>\n";
    echo "<div class='count'>";
    echo ($key + 1) . "/" . $rcount;
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

if ($results['count'] > 100) {
    echo "<p><small>Search results are limited to the first 100 (of ";
    echo $results["count"];
    echo " for this search). Refine your search if needed.</small></p>";
}

$output = ob_get_clean();
file_put_contents($cachepath, $output);
echo $output;
}
?>