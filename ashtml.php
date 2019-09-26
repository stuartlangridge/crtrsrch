<?php
include("query.php");
$results = query($_GET["q"]);
?>
<table>
<thead>
    <tr>
        <th></th>
        <th>Speaker</th>
        <th>Episode</th>
        <th></th>
        <th></th>
    </tr>
</thead>
<tbody>
<?php

foreach ($results as $key => $res) {
    echo "<tr><td>";
    echo ($key + 1) . "/" . count($results);
    echo "</td>\n<td><strong>";
    echo htmlentities($res["speaker"]);
    echo "</strong></td>\n<td>";
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
    echo ")</small></td>\n<td>";
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
    echo '">[<span>in </span>transcript]</a> ';
    echo '<a href="';
    echo $res["episode_yt"];
    echo "&t=";
    echo $res["time_h"];
    echo "h";
    echo $res["time_m"];
    echo "m";
    echo $res["time_s"];
    echo 's">[video]</a>';
    echo "</td></tr>";
    echo "<tr>\n<td colspan=5>";
    echo $res["line"];
    echo "</td></tr>";
}
?>
</tbody>
</table>
<?php
if (count($results) >= 100) {
    echo "<p><small>Search results are limited to the first 100. Refine your search if needed.</small></p>";
}
?>