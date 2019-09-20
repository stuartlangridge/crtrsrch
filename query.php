<?php

function query($q) {
    $db = new SQLite3('cr.db');
    $sql = <<<SQL
    select e.campaign, e.episode, e.title, e.link, l.html,
           group_concat(s.name, ', '), l.time_h, l.time_m, l.time_s
        from line_fts f
        inner join line l on f.line_id = l.id
        inner join episode e on l.episode_id = e.id
        inner join speaker2line sl on l.id = sl.line_id
        inner join speaker s on sl.speaker_id = s.id
        where f.indexed_text match :q group by l.id
SQL;
    $statement = $db->prepare($sql);
    $statement->bindValue(':q', $q);
    $results = $statement->execute();
    $ret = [];
    $count = 0;
    while ($row = $results->fetchArray()) {
        if ($count > 20) break;
        $count += 1;
        $ret[] = array(
            "campaign" => $row[0],
            "episode" => $row[1],
            "episode_title" => $row[2],
            "episode_yt" => $row[3],
            "line" => $row[4],
            "speaker" => $row[5],
            "time_h" => $row[6],
            "time_m" => $row[7],
            "time_s" => $row[8]
        );
    }
    return $ret;
}
?>