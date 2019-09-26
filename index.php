<!doctype html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta charset="utf-8">
<title>Critical Role linked transcript search</title>
<link rel="stylesheet" href="style.css">
</head>
<body>
<main>
<h1>Critical Role linked transcripts</h1>
<p>You can <a href="html/index.html">browse all the Critical Role transcripts</a> or search them below.</p>
<form method="GET">
    <input type="search" name="q" value="<?php
    if (isset($_GET["q"])) {
        echo htmlspecialchars($_GET["q"], ENT_QUOTES);
    }
    ?>">
    <ul>
        <li><label><input type="checkbox" name="LAURA"
            <?php
            if (isset($_GET["LAURA"])) { echo " checked"; }
            ?>> Laura</label></li>
        <li><label><input type="checkbox" name="LIAM"
        <?php
        if (isset($_GET["LIAM"])) { echo " checked"; }
        ?>> Liam</label></li>
        <li><label><input type="checkbox" name="MARISHA"
        <?php
        if (isset($_GET["MARISHA"])) { echo " checked"; }
        ?>> Marisha</label></li>
        <li><label><input type="checkbox" name="MATT"
        <?php
        if (isset($_GET["MATT"])) { echo " checked"; }
        ?>> Matt</label></li>
        <li><label><input type="checkbox" name="SAM"
        <?php
        if (isset($_GET["SAM"])) { echo " checked"; }
        ?>> Sam</label></li>
        <li><label><input type="checkbox" name="TALIESIN"
        <?php
        if (isset($_GET["TALIESIN"])) { echo " checked"; }
        ?>> Taliesin</label></li>
        <li><label><input type="checkbox" name="TRAVIS"
        <?php
        if (isset($_GET["TRAVIS"])) { echo " checked"; }
        ?>> Travis</label></li>
    </ul>
    <input type="submit" value="Search">
</form>
<div id="results">
<?php
if (isset($_GET["q"])) {
    include("ashtml.php");
}
?>
</div>

<footer>
    <p>
        <a href="html/index.html">list of episodes</a>
        |
        <a href="./">search transcripts</a>
    </p>
    <p>This is an <a href="https://kryogenix.org/">@sil</a> thing.</p>
    <p>And a <a href="https://critrole.com/">Critical Role</a>
    thing, of course.</p>
    <p>Mostly a Critical Role thing. And a CRTranscript thing.
    Stuart didn't really have to do much.</p>
</footer>
</main>
<script>
function inline() {
    var res = document.getElementById("results");
    var qbox = document.querySelector("input[type=search]");
    var debounce;
    function query(q) {
        var qs = new URLSearchParams(new FormData(document.querySelector("form"))).toString()
        fetch("ashtml.php?" + qs)
            .then(function(r) {
                return r.text();
            }).then(function(html) {
                res.innerHTML = html;
                window.history.pushState({q: q}, "Search for " + q, "?" + qs);
            }).catch(function(e) {
                console.log("er! error", e);
            })
    }
    function sub(e) {
        if (qbox.value.length > 3) {
            clearTimeout(debounce);
            res.innerHTML = "<p>searching...</p>";
            debounce = setTimeout(query, 200, qbox.value);
        }
    };
    qbox.oninput = sub;
    Array.from(document.querySelectorAll('input[type=checkbox]')).forEach(function(i) {
        i.onchange = sub;
    });
}
if (document.querySelector && window.fetch && window.URLSearchParams && Array.from) { inline(); }
</script>
</body>
</html>