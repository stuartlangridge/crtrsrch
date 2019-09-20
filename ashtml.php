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
    echo "</td>\n<td>";
    echo htmlentities($res["speaker"]);
    echo "</td>\n<td>";
    echo "Campaign ";
    echo $res["campaign"];
    echo " Episode ";
    echo $res["episode"];
    echo ": ";
    echo htmlentities($res["episode_title"]);
    echo "</td>\n<td>";
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
    echo '">[context]</a>';
    echo "</td>\n<td>";
    echo '<a href="';
    echo $res["episode_yt"];
    echo "&t=";
    echo $res["time_h"];
    echo "h";
    echo $res["time_m"];
    echo "m";
    echo $res["time_s"];
    echo 's">[youtube]</a>';
    echo "</td></tr>";
    echo "<tr>\n<td colspan=5>";
    echo $res["line"];
    echo "</td></tr>";
}
?>
</tbody>
</table>
