#!/usr/bin/perl

use CGI ':standard';
use POSIX 'strftime';
use GD;

$i = param('image');
$inx = param('x');
$iny = param('y');
$hf = param('hf');
$hn = param('hn');

if (($inx)&&($iny)&&($hf)&&($hn)) {
	open(PCFILE, ">>data.txt");
	flock(PCFILE,2);
	print PCFILE $hn.";".$hf.";".$inx.";".$iny.";\n";
	close(PCFILE);
}


open(CFILE, "data.txt");
flock(CFILE,1);
@content = <CFILE>;
close(CFILE);

%countrytable = ();
$nextcountrycode = "";
$nextcountryname = "";

foreach $cline (@content) {
	($countryname, $countrycode, $coordx, $coordy, $garbage) = split(";",$cline);
	if (($countryname)&&($countrycode)&&($coordx)&&($coordy)) {
		$countrytable{$countrycode} = $countryname.":".int($coordx).":".int($coordy);
	}
}

open(CPIFILE, "cpi.csv");
@cpidata = <CPIFILE>;
close(CPIFILE);

foreach $entry (@cpidata) {
	($cpiname, $cpicode, $cpiscore, $garbage) = split(";", $entry);
	unless (($cpiname =~ m/Corruption/)||($cpiname eq "")||($cpiname eq "Country")) {
		if (($cpiname)&&($cpicode)&&($cpiscore)) {
			unless ($countrytable{$cpicode}) {
				$nextcountryname = $cpiname;
				$nextcountrycode = $cpicode;
			}
		}
	}
}

print "Expires: Sat, 26 Jul 1997 05:00:00 GMT\n";
print "Last-Modified: ".strftime('%a, %d %b %Y %H:%M:%S GMT', gmtime)."\n";
print "Pragma: no-cache\n";
print "Cache-Control: private, no-cache, no-store, must-revalidate, max-age=0, pre-check=0, post-check=0\n";

if ($i eq '1') {
	$image = GD::Image->newFromPng("world.png");
	foreach $ccode (keys %countrytable) {
		($cname, $cx, $cy) = split(":", $countrytable{$ccode});
		$lc = $image->colorAllocate(int(rand(255)),int(rand(255)), int(rand(255)));
		$image->fill($cx,$cy,$lc);
	}
	print "Content-Type: image/png\n\n";
	binmode(STDOUT);
	print $image->png;
}
else
{
	print "Content-Type: text/html\n\n";
	print "<html><head><title>OpenHack SIDA Project</title></head><body>";
	print "<form>COUNTRY: ".$nextcountryname."<br><input type='image' src='install.cgi?image=1'><input type='hidden' name='hf' value='".$nextcountrycode."'><input type='hidden' name='hn' value='".$nextcountryname."'></form></body><html>";
}
