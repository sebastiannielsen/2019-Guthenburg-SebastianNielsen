#!/usr/bin/perl

use CGI ':standard';
use POSIX 'strftime';
use GD;
use Locale::Country;

$filename = param('filename');
$invert = param('invert');
$i = param('image');

print "Expires: Sat, 26 Jul 1997 05:00:00 GMT\n";
print "Last-Modified: ".strftime('%a, %d %b %Y %H:%M:%S GMT', gmtime)."\n";
print "Pragma: no-cache\n";
print "Cache-Control: private, no-cache, no-store, must-revalidate, max-age=0, pre-check=0, post-check=0\n";

if ($i ne "1") {
	print "Content-Type: text/html\n\n";
	print "<html><head><title>OpenHack SIDA Project</title></head><body>";
	print "<form><select name='filename'>";
	opendir(DIR, "openaid");
	while ($file = readdir(DIR)) {
		next if ($file =~ m/^\./);
		if ($filename eq $file) {
			print "<option value='".$file."' selected>".$file."</option>";
		}
		else
		{
			print "<option value='".$file."'>".$file."</option>";
		}
	}
	closedir(DIR);
	print "</select><br>Invert: <input type='checkbox' name='invert' value='1'";
	if ($invert eq "1") {
		print " checked";
	}
	print "> <input type='submit'></form>";
	if ($filename) {
		print "<img src='index.cgi?image=1&invert=".$invert."&filename=".$filename."' width='1125px' height='558px'>";
	}
	print "</body></html>";
}

if (($filename)&&($i eq "1")) {

	open(CFILE, "data.txt");
	flock(CFILE,1);
	@content = <CFILE>;
	close(CFILE);

	%countrytable = ();
	%cpitable = ();
	%sums = ();

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
		($cpiname, $cpicode, $garbage, $cpiscore, $garbage) = split(";", $entry);
		unless (($cpiname =~ m/Corruption/)||($cpiname eq "")||($cpiname eq "Country")) {
			if (($cpiname)&&($cpicode)&&($cpiscore)) {
				$cpitable{$cpicode} = $cpiscore;
			}
		}
	}

	%sums = scrubfile($filename);

	$highestsum = 0;
	%weights = ();

	foreach $k (keys %sums) {
		if ($sums{$k} > $highestsum) {
			$highestsum = $sums{$k};
		}
	}


	foreach $k (keys %sums) {
		$wval = int(($sums{$k} / $highestsum) * 100);
		if ($invert eq "1") {
			$weights{$k} = 100 - $wval;
		}
		else
		{
			$weights{$k} = $wval;
		}
	}

	$highestcpi = 0;
	%cpiweights = ();

	foreach $k (keys %sums) {
		if ($cpitable{$k} > $highestcpi) {
			$highestcpi = $cpitable{$k};
		}
	}


	foreach $k (keys %sums) {
		$wval = int(($cpitable{$k} / $highestcpi) * 100);
		$cpiweights{$k} = $wval;
	}

	$image = GD::Image->newFromPng("world.png");
	foreach $c (keys %weights) {
		($cname, $cx, $cy) = split(":", $countrytable{$c});
		($red, $green, $blue) = weight($weights{$c}, $cpiweights{$c});
		$lc = $image->colorAllocate($red,$green,$blue);
		$image->fill($cx,$cy,$lc);
	}
	print "Content-Type: image/png\n\n";
	binmode(STDOUT);
	print $image->png;

}


sub weight() {
	$bowla = $_[0];
	$bowlb = $_[1];

	$result = $bowlb - $bowla;

	if ($result < 0) {
		$result = $result * -1;
		$r = 2.55 * $result;
		$g = 2 * (100 - $result);
		$b = 0;
	}
	else
	{
		$b = 2.55 * $result;
		$g = 2 * (100 - $result);
		$r = 0;
	}
	return(int($r), int($g), int($b));
}


sub scrubfile() {
	$filename = $_[0];
	%totalsum = ();
	open(TOSCRUB, "openaid/".$filename);
	@fcontent = <TOSCRUB>;
	close(TOSCRUB);
	$finishedline = "";
	foreach $l (@fcontent) {
		$l =~ s/\n//sgi;
		$l =~ s/\r//sgi;
		$l =~ s/\t//sgi;
		$l =~ s/ //sgi;
		if ($l =~ m/^(D|3),Disbursement,/) {
			if (length($finishedline) > 0) {
				$finishedline =~ s/\"([^"]*)\"//sgi;
				($gar,$gar,$gar,$dollaramount,$gar,$gar,$gar,$gar,$gar,$gar,$gar,$gar,$gar,$gar,$gar,$gar,$gar,$gar,$gar,$gar,$gar,$gar,$cc1,$cc2,$gar) = split(",", $finishedline);
				if ((length($cc1) == 2)&&($cc1 =~ m/^[A-Z]*$/)) {
					$countrycode = $cc1;
				}
				else
				{
					$countrycode = $cc2;
				}
				$countrycode = uc(country_code2code($countrycode,LOCALE_CODE_ALPHA_2, LOCALE_CODE_ALPHA_3));
				if ((length($countrytable{$countrycode}) > 1)&&($dollaramount)&&(substr($dollaramount, 0, 1) ne "-")) {
					$totalsum{$countrycode} = $totalsum{$countrycode} + $dollaramount;
				}
			}
			$finishedline = $l;
		}
		else
		{
			if (length($finishedline) > 0) {
				$finishedline = $finishedline . $l;
			}
		}
	}
	if (length($finishedline) > 0) {
		$finishedline =~ s/\"([^"]*)\"//sgi;
		($gar,$gar,$gar,$dollaramount,$gar,$gar,$gar,$gar,$gar,$gar,$gar,$gar,$gar,$gar,$gar,$gar,$gar,$gar,$gar,$gar,$gar,$gar,$cc1,$cc2,$gar) = split(",", $finishedline);
		if ((length($cc1) == 2)&&($cc1 =~ m/^[A-Z]*$/)) {
			$countrycode = $cc1;
		}
		else
		{
			$countrycode = $cc2;
		}
		$countrycode = uc(country_code2code($countrycode,LOCALE_CODE_ALPHA_2, LOCALE_CODE_ALPHA_3));
		if ((length($countrytable{$countrycode}) > 1)&&($dollaramount)&&(substr($dollaramount, 0, 1) ne "-")) {
			$totalsum{$countrycode} = $totalsum{$countrycode} + $dollaramount;
		}
	}
	return %totalsum;
}
