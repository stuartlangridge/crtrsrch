<?php

function wrap($fontSize, $angle, $fontFace, $string, $width){

    $ret = "";

    $arr = explode(' ', $string);

foreach ( $arr as $word ){

    $teststring = $ret.' '.$word;
    $testbox = imagettfbbox($fontSize, $angle, $fontFace, $teststring);
    if ( $testbox[2] > $width ){
        $ret.=($ret==""?"":"\n").$word;
    } else {
        $ret.=($ret==""?"":' ').$word;
    }
}

return $ret;
}

function result($im, $idx, $total, $name, $episode, $text) {
    global $white, $black, $medgrey, $greyish, $lightgreyish, $font;
    $fontsize = 12;
    $boxtop = 90 + (($idx - 1) * 110);
    imagefilledrectangle($im, 20, $boxtop, 380, $boxtop + 100, $white);
    imagerectangle($im, 20, $boxtop, 380, $boxtop + 100, $lightgreyish);
    imagettftext($im, $fontsize, 0, 30, $boxtop + 20, $medgrey, $font, "$idx/$total");
    imagettftext($im, $fontsize, 0, 90, $boxtop + 20, $greyish, $font, $name);

    $arr = explode(" ", $episode);
    $out = "";
    foreach ($arr as $word) {
        $test = $out .  ($out == "" ? "" : " ") . $word;
        $testbox = imagettfbbox($fontsize, 0, $font, $test);
        if ($testbox[2] > 190) {
            $out .= "…";
            break;
        } else {
            $out = $test;
        }
    }
    imagettftext($im, $fontsize, 0, 170, $boxtop + 20, $medgrey, $font, $out);


    $arr = explode(" ", $text);
    $out = "";
    $lines = 1;
    foreach ($arr as $word) {
        $test = $out .  ($out == "" ? "" : " ") . $word;
        $testbox = imagettfbbox($fontsize, 0, $font, $test . "……");
        if ($testbox[2] > 360) {
            $lines += 1;
            if ($lines > 3) {
                $out .= "…";
                break;
            }
            $out .= "\n" . $word;
        } else {
            $out = $test;
        }
    }
    imagettftext($im, $fontsize, 0, 30, $boxtop + 50, $greyish, $font, $out);
}

include("query.php");
if (isset($_GET["q"])) {
    $qu = $_GET["q"];
    $results = query($qu);
} else {
    $results = ["results" => "", "count" => 0];
}


header("Content-type: image/png");
$im = @imagecreatefrompng("embedimg.png") or die("No GD");
$bg = imagecolorallocate($im, 245, 248, 255);
$white = imagecolorallocate($im, 255, 255, 255);
$black = imagecolorallocate($im, 0, 0, 0);
$greyish = imagecolorallocate($im, 40, 40, 40);
$medgrey = imagecolorallocate($im, 160, 160, 160);
$lightgreyish = imagecolorallocate($im, 210, 210, 210);
$shadow = imagecolorallocate($im, 235, 237, 255);
$font = __DIR__ . "/Ubuntu-R.ttf";

// search box
// first try with large font
$arr = explode(" ", $qu);
$out = "";
$overrun = FALSE;
foreach ($arr as $word) {
    $test = $out .  ($out == "" ? "" : " ") . $word;
    $testbox = imagettfbbox(25, 0, $font, $test);
    if ($testbox[2] > 300) {
        $out .= "…";
        $overrun = TRUE;
        break;
    } else {
        $out = $test;
    }
}
if ($overrun) {
    $arr = explode(" ", $qu);
    $out = "";
    foreach ($arr as $word) {
        $test = $out .  ($out == "" ? "" : " ") . $word;
        $testbox = imagettfbbox(18, 0, $font, $test);
        if ($testbox[2] > 300) {
            $out .= "…";
            $overrun = TRUE;
            break;
        } else {
            $out = $test;
        }
    }
    imagettftext($im, 18, 0, 30, 60, $greyish, __DIR__ . "/Ubuntu-R.ttf", $out);
} else {
    imagettftext($im, 25, 0, 30, 60, $greyish, __DIR__ . "/Ubuntu-R.ttf", $out);
}

if ($results['count'] > 0) {
    result(
        $im, 1, $results['count'], 
        $results["results"][0]["speaker"], 
        "C" . $results['results'][0]["campaign"] . "E" . 
            $results['results'][0]["episode"] . ": " . 
            $results['results'][0]["episode_title"], 
        $results['results'][0]["line"]);
}
if ($results['count'] > 1) {
    result(
        $im, 2, $results['count'], 
        $results["results"][1]["speaker"], 
        "C" . $results['results'][1]["campaign"] . "E" . 
            $results['results'][1]["episode"] . ": " . 
            $results['results'][1]["episode_title"], 
        $results['results'][1]["line"]);
}




imagepng($im);
imagedestroy($im);

?>
