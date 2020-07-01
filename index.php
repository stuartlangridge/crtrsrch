<!doctype html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta charset="utf-8">
<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=UA-331575-1"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'UA-331575-1');
</script>
<title>Critical Role linked transcript search</title>
<link rel="stylesheet" href="style.css">
</head>
<body>
<main>
<h1>Critical Role</h1>
<h2>Linkable transcripts</h2>
<p>You can <a href="html/index.html">browse all the Critical Role transcripts</a> or search them below.</p>
<p>For example, find the occasion when <a href="?q=pastries+are+made+with+cinnamon">Jester told a creature of darkness about cinnamon pastries</a>, or look at every time <a href="?q=&quot;burt+reynolds&quot;&amp;SAM=on">Sam mentioned Burt Reynolds</a> or <a href="?q=&quot;diplomatic+immunity&quot;&amp;LIAM=on">Liam quotes Joss Ackland</a>!</p>
<form method="GET">
    <input type="search" name="q" value="<?php
    if (isset($_GET["q"])) {
        echo htmlspecialchars($_GET["q"], ENT_QUOTES);
    }
    ?>" placeholder="search here!">
    <ul>
        <li><label><input type="checkbox" name="ASHLEY"
        <?php
        if (isset($_GET["ASHLEY"])) { echo " checked"; }
        ?>> Ashley</label></li>
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
    <p>This is an <a href="https://kryogenix.org/">@sil</a> thing. Ping him <a href="https://twitter.com/sil">on Twitter</a> about problems.</p>
    <p>And a <a href="https://critrole.com/">Critical Role</a>
    thing, of course.</p>
    <p>Mostly a Critical Role thing. And a CRTranscript thing.
    Stuart just tied all their hard work together. There are some limited <a href="api.html">“API” docs</a>.</p>
</footer>
</main>
<script>
function inline() {
    var res = document.getElementById("results");
    var qbox = document.querySelector("input[type=search]");
    var debounce;
    var latest_qs;
    function query(q, pushState) {
        var fd = new FormData(document.querySelector("form"));
        var qs = new URLSearchParams(fd).toString();
        latest_qs = qs;
        var fdd = {};
        Array.from(fd.entries()).forEach(function(kv) { fdd[kv[0]] = kv[1]; })
        fetch("ashtml.php?" + qs)
            .then(function(r) {
                return r.text();
            }).then(function(html) {
                if (qs != latest_qs) {
                    console.log("not displaying result of query", qs,
                        "because it has been superseded by", latest_qs);
                }
                res.innerHTML = html;
                if (pushState) window.history.pushState(fdd, "Search for " + q, "?" + qs);
            }).catch(function(e) {
                console.log("er! error", e);
            })
    }
    function sub(e) {
        if (qbox.value.length > 3) {
            clearTimeout(debounce);
            res.innerHTML = "<p>searching...</p>";
            debounce = setTimeout(query, 500, qbox.value, true);
        }
    };
    qbox.oninput = sub;
    Array.from(document.querySelectorAll('input[type=checkbox]')).forEach(function(i) {
        i.onchange = sub;
    });
    window.onpopstate = function(e) {
        setTimeout(function() {
            if (!e.state) {
                qbox.value = "";
                res.innerHTML = "";
                return;
            }
            if (e.state.q) {
                Array.from(document.querySelectorAll("input[type=checkbox]")).forEach(e => {
                    e.checked = false
                });
                for (var k in e.state) {
                    if (k == "q") {
                    } else {
                        var el = document.querySelector("input[name=" + k + "]");
                        if (el) el.checked = true;
                    }
                }
                res.innerHTML = "<p>searching...</p>";
                qbox.value = e.state.q;
                query(e.state.q, false);
            }
        }, 0);
    }
}
if (document.querySelector && window.fetch && window.URLSearchParams && Array.from) { inline(); }

</script>
</body>
</html>