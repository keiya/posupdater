#!/usr/bin/perl

use strict;
use warnings;
use CGI;

my $logfile = "log.txt";

my $q = new CGI;
my $int  = $q->param('int');
my $alim = $q->param('alim');
my $lati = $q->param('lat');
my $long = $q->param('long');
my $accu = $q->param('acc');

print "Content-Type: text/html; charset=UTF-8\n\n";

if (defined $int) {
    &log($int,$alim);
} elsif (defined $lati and defined $long) {
    &wlog($lati,$long,$accu,$logfile);
} else {
    &map($logfile);
}

sub log
{
my $out=<<__EOM__;
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<meta name="viewport" content="minimum-scale=1.0, width=device-width, maximum-scale=1.0">
<title>posupdater</title>
<script type="text/javascript" src="xmlhttp.js"></script>
<script>
var count = 0;

function locSend(lati,longi,acc) {
    httpObj = createXMLHttpRequest(loc);
    if (httpObj) {
        httpObj.open("GET",("loc.cgi?lat="+lati+"&long="+longi+"&acc="+acc),true);
        httpObj.send(null);
    }
}

function loc(){
    if ((httpObj.readyState == 4) && (httpObj.status == 200)) {
        \$("res").innerHTML = "<b>Loc Sent.</b>";
    }else{
        \$("res").innerHTML = "<b>Sending...</b>";
    }
}
function locupdate(pos) { 
    count ++;
    var d = document.getElementById("d");
    d.innerHTML = "lat : " + pos.coords.latitude + "<br/>long : " + pos.coords.longitude + "<br/>accuracy : " + pos.coords.accuracy + "<br/>";
    if (count % $_[0] == 0 && pos.coords.accuracy < $_[1]) {
        locSend(pos.coords.latitude,pos.coords.longitude,pos.coords.accuracy);
    }
}

function handleError(a) {
    var d = document.getElementById("d");
    d.innerHTML = "<p> error: " + a.code + "</p>";

}

window.onload = function(){
   navigator.geolocation.watchPosition(locupdate, handleError)
};
</script>
</head>
<body>
<div>
<p>Your location</p>
<div id="d"></div>
<div id="res"></div>
</div>
</body>
</html>
__EOM__

print $out;
}

sub wlog
{
my $latitude = $_[0];
my $longitude = $_[1];
my $accuracy = $_[2];
$latitude =~ s/[^\d\.]+//;
$longitude =~ s/[^\d\.]+//;
$accuracy =~ s/[^\d\.]+//;
my ($sec, $min, $hour, $mday, $mon, $year, $wday, $yday, $isdst) = localtime(time);
my $date = sprintf("%04d/%02d/%02d %02d:%02d:%02d", $year + 1900, $mon +1, $mday, $hour, $min, $sec);
open( NEW, ">> $_[3]" );
flock(NEW,2);
print NEW "$latitude,$longitude,$accuracy,$date\n";
close( NEW );
}

sub map
{
    open( NEW, "< $_[0]" );
    my (@locs,@arrays);
    my $i=0;
    my $lastupd;
    while (<NEW>) {
        if ($_ =~ /[\d\.,]+/) {
            my @loc = split(/,/,$_);
            push(@locs,"$loc[0],$loc[1]");
            $lastupd = $loc[3];
            $arrays[$i] = "points[$i] = new GLatLng($loc[0],$loc[1]);";
        }
    } continue {
        $i++;
    }
    my $arraystxt = "@arrays";
    close( NEW );
print <<__EOM__;
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml"
    xmlns:v="urn:schemas-microsoft-com:vml">
  <head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <script src="http://maps.google.com/maps?file=api&v=2&key=ABQIAAAA349EloqY-HaXK_4YYTOLGxTAzIHsd_HesJK9nApK4bf2sL3RjxQk0HsQ9jBB4sE_uACCkBq6bSC3dQ"

        type="text/javascript" charset="UTF-8"></script>
    <style type="text/css">
    v\:* {
      behavior:url(#default#VML);
    }
    </style>
<title>$locs[-1]</title>
<meta http-equiv="Refresh" content="60">
<link rel="stylesheet" type="text/css" href="keiya.css">
<style type="text/css"><!--
html, body, #map {
margin:0;
padding:0;
width:100%;
height:94%;
}
html {
overflow:hidden;
}
--></style>
  </head>
  <body>
<table border="1px" width=100%><tr><td>Last: $lastupd</td><td width="250px" id="plong">Long:</td><td width="250px" id="plat">Lat:</td><td>Keyboard Operation</td><td>Auto Refresh</td></tr></table>
    <div id="map"></div>
    <script type="text/javascript">
    //<![CDATA[

    if (GBrowserIsCompatible()) {
      var map = new GMap2(document.getElementById("map"));
      map.addControl(new GLargeMapControl());
      map.addControl(new GOverviewMapControl());
      map.addControl(new GHierarchicalMapTypeControl());
      map.addControl(new GScaleControl());
      new GKeyboardHandler(map);
      map.setCenter(new GLatLng($locs[-1]), 13);

      var points = [];
      $arraystxt

      var polyline = new GPolyline(points);

      var marker = new GMarker(new GLatLng($locs[-1]));

      map.addOverlay(polyline);
      map.addOverlay(marker);
GEvent.addListener(map, "move", function(){
var x = (map.getCenter()).lng();
var y = (map.getCenter()).lat();
document.getElementById("plong").innerHTML = "Long:"+x;
document.getElementById("plat").innerHTML = "Lat:"+y;
} );
    }
window.onunload = GUnload;
    

    //]]>
    </script>

<address>posupdater by <a href="mailto:keiya_21\@yahoo.co.jp">Keiya Chinen</a></address>
  </body>
</html>
__EOM__
}
