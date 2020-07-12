<?php

function query($q) {
    $db = new SQLite3('cr.db');
    $sql = <<<SQL
    select e.campaign, e.episode, e.title, e.link, l.html,
           group_concat(s.name, ', '), l.time_h, l.time_m, l.time_s,
           e.thumbnail
        from line_fts f
        inner join line l on f.line_id = l.id
        inner join episode e on l.episode_id = e.id
        inner join speaker2line sl on l.id = sl.line_id
        inner join speaker s on sl.speaker_id = s.id
        where f.indexed_text match :q 
SQL;
    $speakers = [];
    if (isset($_GET["ASHLEY"])) { $speakers[] = "ASHLEY"; }
    if (isset($_GET["LAURA"])) { $speakers[] = "LAURA"; }
    if (isset($_GET["LIAM"])) { $speakers[] = "LIAM"; }
    if (isset($_GET["MARISHA"])) { $speakers[] = "MARISHA"; }
    if (isset($_GET["MATT"])) { $speakers[] = "MATT"; }
    if (isset($_GET["SAM"])) { $speakers[] = "SAM"; }
    if (isset($_GET["TALIESIN"])) { $speakers[] = "TALIESIN"; }
    if (isset($_GET["TRAVIS"])) { $speakers[] = "TRAVIS"; }
    if (count($speakers) > 0) {
        $sql .= " and s.name in (";
        $splaces = [];
        foreach ($speakers as $idx => $name) {
            if ($idx > 0) $sql .= ",";
            $sql .= ":sp" . $idx;
            $splaces[":sp" . $idx] = $name;
        }
        $sql .= ")";
    }
    if (isset($_GET["lm"])) {
        switch ($_GET["lm"]) {
            case "1-a":
                $sql .= " and campaign = '1' and cast(episode as decimal) < 51 ";
                break;
            case "1-b":
                $sql .= " and campaign = '1' and cast(episode as decimal) > 50 and cast(episode as decimal) < 101 ";
                break;
            case "1-c":
                $sql .= " and campaign = '1' and cast(episode as decimal) > 100 ";
                break;
            case "2-a":
                $sql .= " and campaign = '2' and cast(episode as decimal) < 51 ";
                break;
            case "2-b":
                $sql .= " and campaign = '2' and cast(episode as decimal) > 50 and cast(episode as decimal) < 101 ";
                break;
            case "2-c":
                $sql .= " and campaign = '2' and cast(episode as decimal) > 100 ";
                break;
            case "3-a":
                $sql .= " and campaign = '3' and cast(episode as decimal) < 51 ";
                break;
            case "3-b":
                $sql .= " and campaign = '3' and cast(episode as decimal) > 50 and cast(episode as decimal) < 101 ";
                break;
            case "3-c":
                $sql .= " and campaign = '3' and cast(episode as decimal) > 100 ";
                break;
        }
    }
    $sql .= " group by l.id order by e.sortkey desc";
    $statement = $db->prepare($sql);
    $statement->bindValue(':q', $q);
    if (count($speakers) > 0) {
        foreach ($splaces as $ph => $name) {
            $statement->bindValue($ph, $name);
        }
    }
    @$results = $statement->execute();
    $ret = ['count' => 0, 'results' => []];
    if ($results === FALSE) { return $ret; }
    $count = 0;
    while ($row = $results->fetchArray()) {
        $count += 1;
        if ($count > 100) continue;
        $ret['results'][] = array(
            "campaign" => $row[0],
            "episode" => $row[1],
            "episode_title" => $row[2],
            "episode_yt" => $row[3],
            "line" => $row[4],
            "speaker" => $row[5],
            "time_h" => $row[6],
            "time_m" => $row[7],
            "time_s" => $row[8],
            "thumbnail" => $row[9]
        );
    }
    $ret['count'] = $count;
    return $ret;
}
?>