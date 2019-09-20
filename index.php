<!doctype html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta charset="utf-8">
<title>Critical Role linked transcript search</title>
<style>
table {
    border-collapse: collapse;
}
td {
    vertical-align: top;
    padding: 0.1em;
}
tbody tr:nth-child(2n+1) {
    border-top: 1px solid #ccc;
}
tr:nth-child(2n) td {
    padding-bottom: 1em;
}
th { text-align: left; }
</style>
</head>
<body>
<h1>Search</h1>
<form method="GET">
    <input type="search" name="q" value="<?php
    if (isset($_GET["q"])) {
        echo htmlspecialchars($_GET["q"], ENT_QUOTES);
    }
    ?>">
    <input type="submit">
</form>
<div id="results">
<?php
if (isset($_GET["q"])) {
    include("ashtml.php");
}
?>
</div>
<script>
var res = document.getElementById("results");
function query(q) {
    fetch("ashtml.php?q=" + q)
        .then(function(r) {
            return r.text();
        }).then(function(html) {
            res.innerHTML = html;
        }).catch(function(e) {
            console.log("er! error", e);
        })
}
var debounce;
document.querySelector('[name="q"]').oninput = function(e) {
    if (this.value.length > 3) {
        clearTimeout(debounce);
        debounce = setTimeout(query, 200, this.value);
    }
};
</script>
</body>
</html>